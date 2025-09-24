#!/usr/bin/env python3
"""
Experiment API Server for Conversation Journey Visualizer
========================================================

A simple Flask server that provides API endpoints for the conversation journey visualizer.
This server reads experiment data from JSON files and serves it to the frontend.
"""

import json
import os
import glob
from datetime import datetime
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for the frontend

@app.route('/')
def index():
    """Serve the main visualizer page"""
    return send_from_directory('.', 'conversation_journey_visualizer.html')

@app.route('/api/experiments')
def get_experiments():
    """Get list of available experiments"""
    try:
        experiments = []
        experiment_files = glob.glob('data/experiments/continuous_conversation_exp_*.json')
        
        for file_path in experiment_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Extract experiment info
                exp_info = data.get('experiment_info', {})
                timestamp = exp_info.get('timestamp', '')
                
                # Parse timestamp
                try:
                    if timestamp:
                        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                        date_str = dt.strftime('%Y-%m-%d %H:%M')
                    else:
                        date_str = 'Unknown'
                except:
                    date_str = 'Unknown'
                
                experiments.append({
                    'filename': os.path.basename(file_path),
                    'name': f"Experiment ({exp_info.get('num_dummies', '?')} dummies, {exp_info.get('max_rounds', '?')} rounds)",
                    'date': date_str,
                    'dummies': exp_info.get('num_dummies', 0),
                    'max_rounds': exp_info.get('max_rounds', 0),
                    'milestones': exp_info.get('assessment_milestones', [])
                })
            except Exception as e:
                print(f"Error processing {file_path}: {e}")
                continue
        
        # Sort by date (newest first)
        experiments.sort(key=lambda x: x['date'], reverse=True)
        
        return jsonify(experiments)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/experiment/<filename>')
def get_experiment(filename):
    """Get detailed experiment data"""
    try:
        file_path = os.path.join('data/experiments', filename)
        
        if not os.path.exists(file_path):
            return jsonify({'error': 'Experiment not found'}), 404
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return jsonify(data)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/experiment/<filename>/summary')
def get_experiment_summary(filename):
    """Get experiment summary statistics"""
    try:
        file_path = os.path.join('data/experiments', filename)
        
        if not os.path.exists(file_path):
            return jsonify({'error': 'Experiment not found'}), 404
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Calculate summary statistics
        results = data.get('results', [])
        analysis = data.get('analysis', {})
        
        summary = {
            'experiment_info': data.get('experiment_info', {}),
            'total_dummies': len(results),
            'milestones': data.get('experiment_info', {}).get('assessment_milestones', []),
            'analysis': analysis,
            'dummy_summaries': []
        }
        
        # Calculate per-dummy summaries
        for result in results:
            dummy_summary = {
                'name': result.get('dummy_name', 'Unknown'),
                'pre_score': result.get('pre_assessment_score', 0),
                'final_score': result.get('final_assessment_score', 0),
                'final_improvement': result.get('final_improvement', 0),
                'milestones': []
            }
            
            # Process milestone results
            for milestone in result.get('milestone_results', []):
                dummy_summary['milestones'].append({
                    'rounds': milestone.get('milestone_rounds', 0),
                    'improvement': milestone.get('improvement', 0),
                    'score': milestone.get('milestone_score', 0)
                })
            
            summary['dummy_summaries'].append(dummy_summary)
        
        return jsonify(summary)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

if __name__ == '__main__':
    print("🚀 Starting Experiment API Server...")
    print("📊 Serving conversation journey visualizer")
    print("🌐 Access at: http://localhost:5001")
    print("📁 Serving experiments from: data/experiments/")
    
    app.run(host='0.0.0.0', port=5001, debug=True)
