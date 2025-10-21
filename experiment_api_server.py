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
    return send_from_directory('templates', 'conversation_journey_visualizer.html')

@app.route('/api/experiments')
def get_experiments():
    """Get list of available experiments"""
    try:
        experiments = []
        experiment_files = glob.glob('data/experiments/continuous_conversation*_exp_*.json')
        
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
                
                # Check if personality evolution is enabled
                evolution_enabled = exp_info.get('personality_evolution_enabled', False)
                evolution_text = " (with Evolution)" if evolution_enabled else ""
                
                # Get turns (new format) or convert from rounds (old format)
                max_turns = exp_info.get('max_turns')
                if max_turns is None and 'max_rounds' in exp_info:
                    max_turns = 1 + exp_info['max_rounds'] * 2  # Convert old format
                
                # Get milestone turns (new format) or convert from exchanges (old format)
                milestone_turns = exp_info.get('assessment_milestone_turns')
                if milestone_turns is None and 'assessment_milestones' in exp_info:
                    # Old format: exchange numbers
                    milestone_turns = [1 + m*2 for m in exp_info['assessment_milestones']]
                
                experiments.append({
                    'filename': os.path.basename(file_path),
                    'name': f"Experiment ({exp_info.get('num_dummies', '?')} dummies, {max_turns or '?'} turns){evolution_text}",
                    'date': date_str,
                    'dummies': exp_info.get('num_dummies', 0),
                    'max_turns': max_turns or 0,
                    'milestones': milestone_turns or [],
                    'personality_evolution_enabled': evolution_enabled
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

@app.route('/api/experiment/<filename>/details')
def get_experiment_details(filename):
    """Get experiment data with conversation details (if available)"""
    try:
        file_path = os.path.join('data/experiments', filename)
        
        if not os.path.exists(file_path):
            return jsonify({'error': 'Experiment not found'}), 404
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Filter results to only include those with conversation_details
        results_with_details = []
        for result in data.get('results', []):
            if 'conversation_details' in result:
                results_with_details.append(result)
        
        if not results_with_details:
            return jsonify({'error': 'No conversation details available for this experiment'}), 404
        
        return jsonify(results_with_details)
    
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
    print("🌐 Access at: http://localhost:5002")
    print("📁 Serving experiments from: data/experiments/")
    
    app.run(host='0.0.0.0', port=5002, debug=True)
