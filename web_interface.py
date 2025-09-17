#!/usr/bin/env python3
"""
Web Interface for AI Dummy Analysis
Interactive web application to explore dummy personalities, assessments, and conversations
"""
from flask import Flask, render_template, jsonify, request
import json
import os
from typing import List, Dict, Any
from collections import defaultdict
from conversation_storage import conversation_storage

app = Flask(__name__)

def load_data():
    """Load all the data files"""
    data = {}
    
    # Load AI dummies
    dummies_file = "data/ai_dummies.json"
    if os.path.exists(dummies_file):
        try:
            with open(dummies_file, 'r', encoding='utf-8') as f:
                data['dummies'] = json.load(f)
        except Exception as e:
            print(f"Error loading dummies: {e}")
            data['dummies'] = []
    else:
        data['dummies'] = []
    
    # Load assessments
    assessments_file = "data/assessments.json"
    if os.path.exists(assessments_file):
        try:
            with open(assessments_file, 'r', encoding='utf-8') as f:
                data['assessments'] = json.load(f)
        except Exception as e:
            print(f"Error loading assessments: {e}")
            data['assessments'] = []
    else:
        data['assessments'] = []
    
    # Load conversations
    conversations_file = "data/conversations.json"
    if os.path.exists(conversations_file):
        try:
            with open(conversations_file, 'r', encoding='utf-8') as f:
                data['conversations'] = json.load(f)
        except Exception as e:
            print(f"Error loading conversations: {e}")
            data['conversations'] = []
    else:
        data['conversations'] = []
    
    # Load optimization results (try multiple files in order of preference)
    optimization_files = [
        "data/real_api_test_results.json",
        "data/validation_test_results.json", 
        "data/gepa_test_results.json",
        "data/college_test_results.json"
    ]
    
    data['optimization'] = {}
    for optimization_file in optimization_files:
        if os.path.exists(optimization_file):
            try:
                with open(optimization_file, 'r', encoding='utf-8') as f:
                    loaded_data = json.load(f)
                    # Extract optimization data from the loaded structure
                    if 'optimization' in loaded_data:
                        data['optimization'] = loaded_data['optimization']
                        print(f"✅ Loaded optimization results from: {optimization_file}")
                        break
                    else:
                        data['optimization'] = loaded_data  # Fallback for old format
                        print(f"✅ Loaded optimization results from: {optimization_file}")
                        break
            except Exception as e:
                print(f"❌ Error loading {optimization_file}: {e}")
                continue
    
    return data

def get_dummy_data(dummy_id: str) -> Dict[str, Any]:
    """Get complete data for a specific dummy"""
    data = load_data()
    
    # Find the dummy
    dummy = None
    for d in data['dummies']:
        if d.get('id') == dummy_id:
            dummy = d
            break
    
    if not dummy:
        return {}
    
    # Find pre and post assessments (assuming back-to-back storage)
    pre_assessment = None
    post_assessment = None
    
    print(f"Looking for assessments for dummy {dummy_id}")
    print(f"Total assessments: {len(data['assessments'])}")
    
    for i in range(0, len(data['assessments']) - 1, 2):
        if data['assessments'][i].get('dummy_id') == dummy_id:
            pre_assessment = data['assessments'][i]
            post_assessment = data['assessments'][i+1]
            print(f"Found assessments at positions {i} and {i+1}")
            print(f"Pre-assessment dummy_id: {pre_assessment.get('dummy_id')}")
            print(f"Post-assessment dummy_id: {post_assessment.get('dummy_id')}")
            break
    
    if not pre_assessment:
        print(f"No pre-assessment found for dummy {dummy_id}")
    if not post_assessment:
        print(f"No post-assessment found for dummy {dummy_id}")
    
    # Find conversation
    conversation = None
    for conv in data['conversations']:
        if conv.get('dummy_id') == dummy_id:
            conversation = conv
            break
    
    return {
        'dummy': dummy,
        'pre_assessment': pre_assessment,
        'post_assessment': post_assessment,
        'conversation': conversation
    }

@app.route('/')
def index():
    """Main page with dummy selection"""
    data = load_data()
    
    # Get summary statistics
    total_dummies = len(data['dummies'])
    total_assessments = len(data['assessments'])
    total_conversations = len(data['conversations'])
    
    # Count complete pairs
    complete_pairs = 0
    for i in range(0, len(data['assessments']) - 1, 2):
        if i + 1 < len(data['assessments']):
            pre = data['assessments'][i]
            post = data['assessments'][i + 1]
            if pre.get('dummy_id') == post.get('dummy_id'):
                complete_pairs += 1
    
    return render_template('index.html', 
                         total_dummies=total_dummies,
                         total_assessments=total_assessments,
                         total_conversations=total_conversations,
                         complete_pairs=complete_pairs)

@app.route('/api/dummies')
def api_dummies():
    """API endpoint to get all dummies"""
    data = load_data()
    return jsonify(data['dummies'])

@app.route('/api/dummy/<dummy_id>')
def api_dummy(dummy_id):
    """API endpoint to get specific dummy data"""
    dummy_data = get_dummy_data(dummy_id)
    return jsonify(dummy_data)

@app.route('/dummy/<dummy_id>')
def dummy_detail(dummy_id):
    """Dummy detail page"""
    dummy_data = get_dummy_data(dummy_id)
    if not dummy_data.get('dummy'):
        return "Dummy not found", 404
    
    return render_template('dummy_detail.html', dummy_data=dummy_data)

@app.route('/api/statistics')
def api_statistics():
    """API endpoint to get overall statistics"""
    data = load_data()
    
    # Calculate statistics
    if data['assessments']:
        # Pair assessments
        pre_scores = []
        post_scores = []
        improvements = []
        
        for i in range(0, len(data['assessments']) - 1, 2):
            if i + 1 < len(data['assessments']):
                pre = data['assessments'][i]
                post = data['assessments'][i + 1]
                if pre.get('dummy_id') == post.get('dummy_id'):
                    pre_score = pre.get('average_score', 0)
                    post_score = post.get('average_score', 0)
                    improvement = post_score - pre_score
                    
                    pre_scores.append(pre_score)
                    post_scores.append(post_score)
                    improvements.append(improvement)
        
        if pre_scores:
            stats = {
                'total_dummies': len(data['dummies']),
                'complete_pairs': len(pre_scores),
                'pre_avg': sum(pre_scores) / len(pre_scores),
                'post_avg': sum(post_scores) / len(post_scores),
                'improvement_avg': sum(improvements) / len(improvements),
                'improvement_pct': (sum(improvements) / len(improvements)) / (sum(pre_scores) / len(pre_scores)) * 100 if pre_scores else 0
            }
        else:
            stats = {'total_dummies': len(data['dummies']), 'complete_pairs': 0}
    else:
        stats = {'total_dummies': len(data['dummies']), 'complete_pairs': 0}
    
    return jsonify(stats)

@app.route('/optimization')
def optimization_results():
    """Optimization results page showing TRUE GEPA progress"""
    data = load_data()
    return render_template('optimization.html', data=data)

@app.route('/generation/<int:generation_num>')
def generation_detail(generation_num):
    """Detailed view of a specific generation"""
    data = load_data()
    return render_template('generation_detail.html', data=data, generation_num=generation_num)

@app.route('/prompt/<prompt_id>')
def prompt_detail(prompt_id):
    """Detailed view of a specific prompt with all dummy results"""
    data = load_data()
    return render_template('prompt_detail.html', data=data, prompt_id=prompt_id)

@app.route('/api/optimization')
def api_optimization():
    """API endpoint to get optimization results"""
    data = load_data()
    optimization_data = data.get('optimization', {})
    
    # Return data in the format expected by the frontend
    return jsonify({
        'pareto_frontier': optimization_data.get('pareto_frontier', []),
        'best_per_generation': optimization_data.get('best_per_generation', []),
        'all_prompts': optimization_data.get('all_prompts', []),
        'optimization_history': optimization_data.get('optimization_history', [])
    })

@app.route('/api/generation/<int:generation_num>')
def api_generation(generation_num):
    """API endpoint to get specific generation data"""
    data = load_data()
    optimization_data = data.get('optimization', {})
    
    # Filter prompts by generation - use all_prompts instead of pareto_frontier
    if 'all_prompts' in optimization_data:
        generation_prompts = [p for p in optimization_data['all_prompts'] if p.get('generation') == generation_num]
        return jsonify({
            'generation': generation_num,
            'prompts': generation_prompts,
            'total_prompts': len(generation_prompts)
        })
    elif 'pareto_frontier' in optimization_data:
        # Fallback to pareto_frontier if all_prompts not available
        generation_prompts = [p for p in optimization_data['pareto_frontier'] if p.get('generation') == generation_num]
        return jsonify({
            'generation': generation_num,
            'prompts': generation_prompts,
            'total_prompts': len(generation_prompts)
        })
    
    return jsonify({'generation': generation_num, 'prompts': [], 'total_prompts': 0})

@app.route('/api/prompt/<prompt_id>')
def api_prompt(prompt_id):
    """API endpoint to get specific prompt data with all dummy results"""
    data = load_data()
    optimization_data = data.get('optimization', {})
    
    # Find the prompt - check all_prompts first, then pareto_frontier
    prompt = None
    if 'all_prompts' in optimization_data:
        for p in optimization_data['all_prompts']:
            if p.get('id') == prompt_id:
                prompt = p
                break
    
    if not prompt and 'pareto_frontier' in optimization_data:
        for p in optimization_data['pareto_frontier']:
            if p.get('id') == prompt_id:
                prompt = p
                break
    
    if not prompt:
        return jsonify({'error': 'Prompt not found'}), 404
    
    # Get conversations from the new storage system
    conversations = conversation_storage.get_conversations_by_prompt(prompt_id)
    
    # Process conversations from new storage system
    prompt_results = []
    if conversations:
        print(f"🔍 Found {len(conversations)} conversations from storage for prompt {prompt_id}")
        for conversation in conversations:
            # Get dummy details
            dummy = None
            for d in data.get('dummies', []):
                if d.get('id') == conversation.get('dummy_id'):
                    dummy = d
                    break
            
            if dummy:
                # Convert conversation to result format
                result = {
                    'pre_score': conversation.get('pre_assessment', {}).get('average_score', 0),
                    'post_score': conversation.get('post_assessment', {}).get('average_score', 0),
                    'improvement': conversation.get('improvement', 0),
                    'conversation': conversation.get('conversation', []),
                    'reflection_insights': conversation.get('reflection_insights', []),
                    'reflection': conversation.get('reflection', '')  # Add individual conversation reflection
                }
                print(f"💬 Conversation for {dummy.get('name')}: {len(result['conversation'])} turns")
                prompt_results.append({
                    'dummy': dummy,
                    'result': result
                })
    else:
        print(f"❌ No conversations found for prompt {prompt_id}")
    
    return jsonify({
        'prompt': prompt,
        'results': prompt_results,
        'total_results': len(prompt_results)
    })

@app.route('/api/conversation/<conversation_id>')
def api_conversation(conversation_id):
    """API endpoint to get a specific conversation by ID"""
    conversation = conversation_storage.get_conversation_by_id(conversation_id)
    if not conversation:
        return jsonify({'error': 'Conversation not found'}), 404
    
    return jsonify(conversation)

@app.route('/api/dummy/<dummy_id>/conversations')
def api_dummy_conversations(dummy_id):
    """API endpoint to get all conversations for a specific dummy"""
    dummy_conversations = conversation_storage.get_dummy_conversations(dummy_id)
    if not dummy_conversations:
        return jsonify({'error': 'No conversations found for this dummy'}), 404
    
    return jsonify(dummy_conversations)

@app.route('/api/conversations/stats')
def api_conversation_stats():
    """API endpoint to get conversation storage statistics"""
    stats = conversation_storage.get_conversation_stats()
    return jsonify(stats)

@app.route('/api/prompt/<prompt_id>/synthesis')
def api_prompt_synthesis(prompt_id):
    """API endpoint to get synthesis analysis for a specific prompt"""
    try:
        synthesis_file = f"data/synthesis_analysis/synthesis_analysis_{prompt_id}.json"
        
        if not os.path.exists(synthesis_file):
            return jsonify({'error': 'Synthesis analysis not found'}), 404
        
        with open(synthesis_file, 'r', encoding='utf-8') as f:
            synthesis_data = json.load(f)
        
        return jsonify(synthesis_data)
        
    except Exception as e:
        return jsonify({'error': f'Failed to load synthesis analysis: {str(e)}'}), 500

@app.route('/api/family-tree')
def api_family_tree():
    """API endpoint to get family tree data for all prompts from synthesis files only"""
    try:
        prompts = []
        
        # Load prompts from synthesis files only for consistency
        synthesis_dir = "data/synthesis_analysis"
        if not os.path.exists(synthesis_dir):
            return jsonify({'error': 'Synthesis analysis directory not found'}), 404
        
        synthesis_files = [f for f in os.listdir(synthesis_dir) if f.startswith('synthesis_analysis_') and f.endswith('.json')]
        
        if not synthesis_files:
            return jsonify({'error': 'No synthesis analysis files found'}), 404
        
        for synthesis_file in synthesis_files:
            try:
                with open(os.path.join(synthesis_dir, synthesis_file), 'r', encoding='utf-8') as f:
                    synthesis_data = json.load(f)
                
                prompt_id = synthesis_data.get('prompt_id', '')
                prompt_name = synthesis_data.get('prompt_name', 'Unknown')
                generation = synthesis_data.get('generation', 0)
                
                # Determine prompt type
                prompt_type = "genesis"
                if generation > 0:
                    if 'M' in prompt_name:
                        prompt_type = "mutation"
                    elif 'C' in prompt_name:
                        prompt_type = "crossover"
                
                prompt = {
                    'id': prompt_id,
                    'name': prompt_name,
                    'prompt_text': f"[Synthesis available - {len(synthesis_data.get('synthesis_analysis', ''))} chars]",
                    'generation': generation,
                    'performance_metrics': {},
                    'type': prompt_type,
                    'created_at': synthesis_data.get('timestamp', ''),
                    'last_tested': synthesis_data.get('timestamp', ''),
                    'has_synthesis': True
                }
                prompts.append(prompt)
                    
            except Exception as e:
                print(f"Warning: Could not load synthesis file {synthesis_file}: {e}")
                continue
        
        # Sort by generation, then by name
        prompts.sort(key=lambda x: (x['generation'], x['name']))
        
        return jsonify({
            'prompts': prompts,
            'total_prompts': len(prompts),
            'generations': len(set(p['generation'] for p in prompts))
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to load family tree data: {str(e)}'}), 500

@app.route('/family-tree')
def family_tree():
    """Route to display the family tree page"""
    return render_template('prompt_family_tree.html')

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    
    # Create the main template
    main_template = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Dummy Analysis Dashboard</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        .dummy-card {
            transition: transform 0.2s, box-shadow 0.2s;
            cursor: pointer;
        }
        .dummy-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 25px rgba(0,0,0,0.15);
        }
        .personality-badge {
            font-size: 0.8em;
            margin: 2px;
        }
        .score-display {
            font-size: 1.2em;
            font-weight: bold;
        }
        .improvement-positive { color: #28a745; }
        .improvement-negative { color: #dc3545; }
        .improvement-neutral { color: #6c757d; }
        .conversation-turn {
            margin-bottom: 15px;
            padding: 10px;
            border-radius: 8px;
        }
        .dummy-turn {
            background-color: #f8f9fa;
            border-left: 4px solid #007bff;
        }
        .ai-turn {
            background-color: #e7f3ff;
            border-left: 4px solid #28a745;
        }
        .assessment-question {
            margin-bottom: 10px;
            padding: 8px;
            background-color: #f8f9fa;
            border-radius: 5px;
        }
        .loading {
            text-align: center;
            padding: 50px;
            color: #6c757d;
        }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand" href="/">
                <i class="fas fa-robot me-2"></i>AI Dummy Analysis Dashboard
            </a>
            <div class="navbar-nav ms-auto">
                <a class="nav-link" href="/">
                    <i class="fas fa-home me-1"></i>Dashboard
                </a>
                <a class="nav-link" href="/optimization">
                    <i class="fas fa-chart-line me-1"></i>TRUE GEPA Results
                </a>
            </div>
        </div>
    </nav>

    <div class="container mt-4">
        <div class="row">
            <div class="col-12">
                <div class="card">
                    <div class="card-header">
                        <h4><i class="fas fa-chart-bar me-2"></i>Overview Statistics</h4>
                    </div>
                    <div class="card-body">
                        <div class="row text-center">
                            <div class="col-md-3">
                                <div class="border rounded p-3">
                                    <h3 class="text-primary">{{ total_dummies }}</h3>
                                    <p class="mb-0">Total Dummies</p>
                                </div>
                            </div>
                            <div class="col-md-3">
                                <div class="border rounded p-3">
                                    <h3 class="text-success">{{ total_assessments }}</h3>
                                    <p class="mb-0">Total Assessments</p>
                                </div>
                            </div>
                            <div class="col-md-3">
                                <div class="border rounded p-3">
                                    <h3 class="text-info">{{ total_conversations }}</h3>
                                    <p class="mb-0">Total Conversations</p>
                                </div>
                            </div>
                            <div class="col-md-3">
                                <div class="border rounded p-3">
                                    <h3 class="text-warning">{{ complete_pairs }}</h3>
                                    <p class="mb-0">Complete Pairs</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div class="row mt-4">
            <div class="col-12">
                <div class="card">
                    <div class="card-header d-flex justify-content-between align-items-center">
                        <h4><i class="fas fa-users me-2"></i>AI Dummies</h4>
                        <div class="input-group" style="max-width: 300px;">
                            <span class="input-group-text"><i class="fas fa-search"></i></span>
                            <input type="text" class="form-control" id="searchInput" placeholder="Search dummies...">
                        </div>
                    </div>
                    <div class="card-body">
                        <div id="dummiesContainer" class="row">
                            <div class="loading">
                                <i class="fas fa-spinner fa-spin fa-2x mb-3"></i>
                                <p>Loading dummies...</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        // Load dummies on page load
        document.addEventListener('DOMContentLoaded', function() {
            loadDummies();
        });

        // Search functionality
        document.getElementById('searchInput').addEventListener('input', function(e) {
            const searchTerm = e.target.value.toLowerCase();
            filterDummies(searchTerm);
        });

        function loadDummies() {
            fetch('/api/dummies')
                .then(response => response.json())
                .then(dummies => {
                    console.log('Loaded dummies:', dummies);
                    if (dummies.length > 0) {
                        console.log('First dummy structure:', dummies[0]);
                    }
                    displayDummies(dummies);
                })
                .catch(error => {
                    console.error('Error loading dummies:', error);
                    document.getElementById('dummiesContainer').innerHTML = 
                        '<div class="col-12 text-center text-danger">Error loading dummies: ' + error.message + '</div>';
                });
        }

        function displayDummies(dummies) {
            const container = document.getElementById('dummiesContainer');
            
            if (dummies.length === 0) {
                container.innerHTML = '<div class="col-12 text-center">No dummies found</div>';
                return;
            }

            const html = dummies.map(dummy => {
                // Calculate anxiety category from the anxiety level
                const anxietyLevel = dummy.social_anxiety?.anxiety_level || 0;
                const anxietyCategory = getAnxietyCategory(anxietyLevel);
                const anxietyColor = getAnxietyColor(anxietyLevel);
                
                return `
                    <div class="col-lg-4 col-md-6 mb-4 dummy-item" data-name="${dummy.name?.toLowerCase() || ''}" data-gender="${dummy.gender?.toLowerCase() || ''}" data-age="${dummy.age || 0}">
                        <div class="card dummy-card h-100" onclick="viewDummy('${dummy.id || ''}')">
                            <div class="card-header text-center">
                                <h5 class="mb-0">${dummy.name || 'Unknown'}</h5>
                                <small class="text-muted">${dummy.gender || 'Unknown'}, ${dummy.age || 0} years old</small>
                            </div>
                            <div class="card-body">
                                <div class="mb-3">
                                    <strong>Anxiety Level:</strong> ${anxietyLevel}/10
                                    <span class="badge bg-${anxietyColor} ms-2">
                                        ${anxietyCategory}
                                    </span>
                                </div>
                                <div class="mb-3">
                                    <strong>Personality:</strong><br>
                                    <span class="badge bg-primary personality-badge">E: ${dummy.personality?.extraversion || 0}</span>
                                    <span class="badge bg-success personality-badge">A: ${dummy.personality?.agreeableness || 0}</span>
                                    <span class="badge bg-info personality-badge">C: ${dummy.personality?.conscientiousness || 0}</span>
                                    <span class="badge bg-warning personality-badge">N: ${dummy.personality?.neuroticism || 0}</span>
                                    <span class="badge bg-secondary personality-badge">O: ${dummy.personality?.openness || 0}</span>
                                </div>
                                <div class="text-center">
                                    <button class="btn btn-primary btn-sm">
                                        <i class="fas fa-eye me-1"></i>View Details
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                `;
            }).join('');

            container.innerHTML = html;
        }

        function getAnxietyCategory(level) {
            if (level <= 3) return 'Low';
            if (level <= 6) return 'Moderate';
            return 'High';
        }

        function getAnxietyColor(level) {
            if (level <= 3) return 'success';
            if (level <= 6) return 'warning';
            return 'danger';
        }

        function filterDummies(searchTerm) {
            const dummyItems = document.querySelectorAll('.dummy-item');
            
            dummyItems.forEach(item => {
                const name = item.dataset.name;
                const gender = item.dataset.gender;
                const age = item.dataset.age;
                
                if (name.includes(searchTerm) || gender.includes(searchTerm) || age.toString().includes(searchTerm)) {
                    item.style.display = 'block';
                } else {
                    item.style.display = 'none';
                }
            });
        }

        function viewDummy(dummyId) {
            window.location.href = `/dummy/${dummyId}`;
        }
    </script>
</body>
</html>'''
    
    # Create the dummy detail template
    detail_template = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dummy Detail - AI Dummy Analysis</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        .personality-badge {
            font-size: 0.9em;
            margin: 3px;
        }
        .score-display {
            font-size: 1.3em;
            font-weight: bold;
        }
        .improvement-positive { color: #28a745; }
        .improvement-negative { color: #dc3545; }
        .improvement-neutral { color: #6c757d; }
        .conversation-turn {
            margin-bottom: 15px;
            padding: 15px;
            border-radius: 10px;
        }
        .dummy-turn {
            background-color: #f8f9fa;
            border-left: 5px solid #007bff;
        }
        .ai-turn {
            background-color: #e7f3ff;
            border-left: 5px solid #28a745;
        }
        .assessment-question {
            margin-bottom: 12px;
            padding: 10px;
            background-color: #f8f9fa;
            border-radius: 8px;
            border-left: 3px solid #dee2e6;
        }
        .assessment-score {
            font-weight: bold;
            font-size: 1.1em;
        }
        .loading {
            text-align: center;
            padding: 50px;
            color: #6c757d;
        }
        .nav-tabs .nav-link {
            color: #495057;
        }
        .nav-tabs .nav-link.active {
            color: #007bff;
            font-weight: bold;
        }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand" href="/">
                <i class="fas fa-robot me-2"></i>AI Dummy Analysis Dashboard
            </a>
            <div class="navbar-nav ms-auto">
                <a class="nav-link" href="/">
                    <i class="fas fa-arrow-left me-1"></i>Back to Dashboard
                </a>
            </div>
        </div>
    </nav>

    <div class="container mt-4">
        <div id="dummyDetailContainer">
            <div class="loading">
                <i class="fas fa-spinner fa-spin fa-2x mb-3"></i>
                <p>Loading dummy details...</p>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        // Get dummy ID from URL
        const dummyId = window.location.pathname.split('/').pop();
        
        // Load dummy details on page load
        document.addEventListener('DOMContentLoaded', function() {
            loadDummyDetails(dummyId);
        });

        function loadDummyDetails(dummyId) {
            fetch(`/api/dummy/${dummyId}`)
                .then(response => response.json())
                .then(data => {
                    displayDummyDetails(data);
                })
                .catch(error => {
                    console.error('Error loading dummy details:', error);
                    document.getElementById('dummyDetailContainer').innerHTML = 
                        '<div class="text-center text-danger">Error loading dummy details</div>';
                });
        }

        function displayDummyDetails(data) {
            const container = document.getElementById('dummyDetailContainer');
            const dummy = data.dummy;
            
            if (!dummy) {
                container.innerHTML = '<div class="text-center text-danger">Dummy not found</div>';
                return;
            }

            // Calculate anxiety category from the anxiety level
            const anxietyLevel = dummy.social_anxiety?.anxiety_level || 0;
            const anxietyCategory = getAnxietyCategory(anxietyLevel);
            const anxietyColor = getAnxietyColor(anxietyLevel);

            const html = `
                <div class="row">
                    <div class="col-12">
                        <div class="card">
                            <div class="card-header">
                                <div class="d-flex justify-content-between align-items-center">
                                    <h3><i class="fas fa-user me-2"></i>${dummy.name || 'Unknown'}</h3>
                                    <div>
                                        <span class="badge bg-secondary fs-6">${dummy.gender || 'Unknown'}</span>
                                        <span class="badge bg-info fs-6">${dummy.age || 0} years old</span>
                                    </div>
                                </div>
                            </div>
                            <div class="card-body">
                                <div class="row">
                                    <div class="col-md-6">
                                        <h5><i class="fas fa-brain me-2"></i>Personality Profile</h5>
                                        <div class="mb-3">
                                            <strong>Big Five Traits:</strong><br>
                                            <span class="badge bg-primary personality-badge">Extraversion: ${dummy.personality?.extraversion || 0}</span>
                                            <span class="badge bg-success personality-badge">Agreeableness: ${dummy.personality?.agreeableness || 0}</span>
                                            <span class="badge bg-info personality-badge">Conscientiousness: ${dummy.personality?.conscientiousness || 0}</span>
                                            <span class="badge bg-warning personality-badge">Neuroticism: ${dummy.personality?.neuroticism || 0}</span>
                                            <span class="badge bg-secondary personality-badge">Openness: ${dummy.personality?.openness || 0}</span>
                                        </div>
                                        <div class="mb-3">
                                            <strong>Background:</strong><br>
                                            <p class="mb-1">${dummy.background || 'No background information available.'}</p>
                                        </div>
                                    </div>
                                    <div class="col-md-6">
                                        <h5><i class="fas fa-exclamation-triangle me-2"></i>Social Anxiety Profile</h5>
                                        <div class="mb-3">
                                            <strong>Anxiety Level:</strong> ${anxietyLevel}/10
                                            <span class="badge bg-${anxietyColor} ms-2">
                                                ${anxietyCategory}
                                            </span>
                                        </div>
                                        <div class="mb-3">
                                            <strong>Fears:</strong><br>
                                            <p class="mb-1">${dummy.fears ? dummy.fears.join(', ') : 'No fears information available.'}</p>
                                        </div>
                                        <div class="mb-3">
                                            <strong>Challenges:</strong><br>
                                            <p class="mb-1">${dummy.challenges ? dummy.challenges.join(', ') : 'No challenges information available.'}</p>
                                        </div>
                                        <div class="mb-3">
                                            <strong>Behaviors:</strong><br>
                                            <p class="mb-1">${dummy.behaviors ? dummy.behaviors.join(', ') : 'No behaviors information available.'}</p>
                                        </div>
                                        <div class="mb-3">
                                            <strong>Anxiety Triggers:</strong><br>
                                            <p class="mb-1">${dummy.social_anxiety?.triggers ? dummy.social_anxiety.triggers.join(', ') : 'No triggers information available.'}</p>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="row mt-4">
                    <div class="col-12">
                        <div class="card">
                            <div class="card-header">
                                <ul class="nav nav-tabs card-header-tabs" id="detailTabs" role="tablist">
                                    <li class="nav-item" role="presentation">
                                        <button class="nav-link active" id="pre-assessment-tab" data-bs-toggle="tab" data-bs-target="#pre-assessment" type="button" role="tab">
                                            <i class="fas fa-clipboard me-2"></i>Pre-Assessment
                                        </button>
                                    </li>
                                    <li class="nav-item" role="presentation">
                                        <button class="nav-link" id="post-assessment-tab" data-bs-toggle="tab" data-bs-target="#post-assessment" type="button" role="tab">
                                            <i class="fas fa-clipboard-check me-2"></i>Post-Assessment
                                        </button>
                                    </li>
                                    <li class="nav-item" role="presentation">
                                        <button class="nav-link" id="conversation-tab" data-bs-toggle="tab" data-bs-target="#conversation" type="button" role="tab">
                                            <i class="fas fa-comments me-2"></i>Conversation
                                        </button>
                                    </li>
                                </ul>
                            </div>
                            <div class="card-body">
                                <div class="tab-content" id="detailTabsContent">
                                    <div class="tab-pane fade show active" id="pre-assessment" role="tabpanel">
                                        ${generatePreAssessmentHTML(data)}
                                    </div>
                                    <div class="tab-pane fade" id="post-assessment" role="tabpanel">
                                        ${generatePostAssessmentHTML(data)}
                                    </div>
                                    <div class="tab-pane fade" id="conversation" role="tabpanel">
                                        ${generateConversationHTML(data)}
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            `;

            container.innerHTML = html;
        }

        function generatePreAssessmentHTML(data) {
            const pre = data.pre_assessment;
            
            if (!pre) {
                return '<div class="text-center text-muted">No pre-assessment available for this dummy.</div>';
            }

            return `
                <div class="row">
                    <div class="col-12">
                        <h5 class="text-primary"><i class="fas fa-clipboard me-2"></i>Pre-Assessment Results</h5>
                        <div class="mb-3">
                            <strong>Overall Score:</strong>
                            <span class="score-display text-primary">${(pre.average_score || 0).toFixed(2)}/4.0</span>
                        </div>
                        <div class="mb-3">
                            <strong>Total Score:</strong> ${(pre.total_score || 0).toFixed(1)}/80.0
                        </div>
                        ${generateQuestionsHTML(pre.responses || [], 'pre')}
                    </div>
                </div>
            `;
        }

        function generatePostAssessmentHTML(data) {
            const post = data.post_assessment;
            
            if (!post) {
                return '<div class="text-center text-muted">No post-assessment available for this dummy.</div>';
            }

            return `
                <div class="row">
                    <div class="col-12">
                        <h5 class="text-success"><i class="fas fa-clipboard-check me-2"></i>Post-Assessment Results</h5>
                        <div class="mb-3">
                            <strong>Overall Score:</strong>
                            <span class="score-display text-success">${(post.average_score || 0).toFixed(2)}/4.0</span>
                        </div>
                        <div class="mb-3">
                            <strong>Total Score:</strong> ${(post.total_score || 0).toFixed(1)}/80.0
                        </div>
                        ${generateQuestionsHTML(post.responses || [], 'post')}
                        
                        ${generateImprovementSummary(data)}
                    </div>
                </div>
            `;
        }

        function generateImprovementSummary(data) {
            const pre = data.pre_assessment;
            const post = data.post_assessment;
            
            if (!pre || !post) {
                return '';
            }
            
            const preScore = pre.average_score || 0;
            const postScore = post.average_score || 0;
            const improvement = postScore - preScore;
            const improvementClass = improvement > 0 ? 'improvement-positive' : 
                                   improvement < 0 ? 'improvement-negative' : 'improvement-neutral';
            const improvementIcon = improvement > 0 ? 'fa-arrow-up' : 
                                  improvement < 0 ? 'fa-arrow-down' : 'fa-minus';
            
            return `
                <div class="row mt-4">
                    <div class="col-12">
                        <div class="card border-${improvement > 0 ? 'success' : improvement < 0 ? 'danger' : 'secondary'}">
                            <div class="card-header">
                                <h6 class="mb-0"><i class="fas fa-chart-line me-2"></i>Improvement Summary</h6>
                            </div>
                            <div class="card-body text-center">
                                <div class="score-display ${improvementClass}">
                                    <i class="fas ${improvementIcon} me-2"></i>
                                    ${improvement > 0 ? '+' : ''}${improvement.toFixed(2)} points
                                </div>
                                <p class="mb-0 mt-2">
                                    ${improvement > 0 ? 'Improved' : improvement < 0 ? 'Declined' : 'No change'} 
                                    from ${preScore.toFixed(2)} to ${postScore.toFixed(2)}
                                </p>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        }

        function generateAssessmentsHTML(data) {
            const pre = data.pre_assessment;
            const post = data.post_assessment;
            
            if (!pre && !post) {
                return '<div class="text-center text-muted">No assessments available for this dummy.</div>';
            }

            let html = '<div class="row">';
            
            if (pre) {
                html += `
                    <div class="col-md-6">
                        <h5 class="text-primary"><i class="fas fa-clipboard me-2"></i>Pre-Assessment</h5>
                        <div class="mb-3">
                            <strong>Overall Score:</strong>
                            <span class="score-display text-primary">${(pre.average_score || 0).toFixed(2)}/4.0</span>
                        </div>
                        <div class="mb-3">
                            <strong>Total Score:</strong> ${(pre.total_score || 0).toFixed(1)}/80.0
                        </div>
                        ${generateQuestionsHTML(pre.responses || [], 'pre')}
                    </div>
                `;
            }
            
            if (post) {
                html += `
                    <div class="col-md-6">
                        <h5 class="text-success"><i class="fas fa-clipboard-check me-2"></i>Post-Assessment</h5>
                        <div class="mb-3">
                            <strong>Overall Score:</strong>
                            <span class="score-display text-success">${(post.average_score || 0).toFixed(2)}/4.0</span>
                        </div>
                        <div class="mb-3">
                            <strong>Total Score:</strong> ${(post.total_score || 0).toFixed(1)}/80.0
                        </div>
                        ${generateQuestionsHTML(post.responses || [], 'post')}
                    </div>
                `;
            }
            
            html += '</div>';
            
            // Add improvement summary if both assessments exist
            if (pre && post) {
                const improvement = post.average_score - pre.average_score;
                const improvementClass = improvement > 0 ? 'improvement-positive' : 
                                       improvement < 0 ? 'improvement-negative' : 'improvement-neutral';
                const improvementIcon = improvement > 0 ? 'fa-arrow-up' : 
                                      improvement < 0 ? 'fa-arrow-down' : 'fa-minus';
                
                html += `
                    <div class="row mt-4">
                        <div class="col-12">
                            <div class="card border-${improvement > 0 ? 'success' : improvement < 0 ? 'danger' : 'secondary'}">
                                <div class="card-header">
                                    <h6 class="mb-0"><i class="fas fa-chart-line me-2"></i>Improvement Summary</h6>
                                </div>
                                <div class="card-body text-center">
                                    <div class="score-display ${improvementClass}">
                                        <i class="fas ${improvementIcon} me-2"></i>
                                        ${improvement > 0 ? '+' : ''}${improvement.toFixed(2)} points
                                    </div>
                                    <p class="mb-0 mt-2">
                                        ${improvement > 0 ? 'Improved' : improvement < 0 ? 'Declined' : 'No change'} 
                                        from ${pre.average_score.toFixed(2)} to ${post.average_score.toFixed(2)}
                                    </p>
                                </div>
                            </div>
                        </div>
                    </div>
                `;
            }
            
            return html;
        }

        function generateQuestionsHTML(responses, type) {
            if (!responses || responses.length === 0) {
                return '<p class="text-muted">No question responses available.</p>';
            }

            let html = '<h6>Question Responses:</h6>';
            
            responses.forEach((response, index) => {
                const score = response.score || 0;
                const scoreClass = score >= 3 ? 'text-success' : 
                                 score >= 2 ? 'text-warning' : 'text-danger';
                
                html += `
                    <div class="assessment-question">
                        <div class="d-flex justify-content-between align-items-start">
                            <div class="flex-grow-1">
                                <strong>Q${index + 1}:</strong> ${response.question || 'Question not available'}
                            </div>
                            <span class="assessment-score ${scoreClass} ms-2">
                                ${score}/4
                            </span>
                        </div>
                        ${response.notes ? `<small class="text-muted mt-1 d-block">${response.notes}</small>` : ''}
                    </div>
                `;
            });
            
            return html;
        }

        function generateConversationHTML(data) {
            const conversation = data.conversation;
            
            if (!conversation || !conversation.turns || conversation.turns.length === 0) {
                return '<div class="text-center text-muted">No conversation available for this dummy.</div>';
            }

            let html = `
                <div class="mb-3">
                    <h6><i class="fas fa-info-circle me-2"></i>Conversation Details</h6>
                    <p class="mb-1"><strong>Scenario:</strong> ${conversation.scenario || 'No scenario specified'}</p>
                    <p class="mb-1"><strong>Total Turns:</strong> ${conversation.turns.length}</p>
                    <p class="mb-0"><strong>Date:</strong> ${conversation.timestamp ? new Date(conversation.timestamp).toLocaleString() : 'No timestamp available'}</p>
                </div>
                <hr>
                <h6><i class="fas fa-comments me-2"></i>Conversation Flow</h6>
            `;
            
            conversation.turns.forEach((turn, index) => {
                const isDummy = turn.speaker === 'dummy';
                const turnClass = isDummy ? 'dummy-turn' : 'ai-turn';
                const speakerName = isDummy ? 'Dummy' : 'AI Assistant';
                const speakerIcon = isDummy ? 'fa-user' : 'fa-robot';
                
                html += `
                    <div class="conversation-turn ${turnClass}">
                        <div class="d-flex align-items-start">
                            <div class="me-3">
                                <i class="fas ${speakerIcon} fa-lg text-${isDummy ? 'primary' : 'success'}"></i>
                            </div>
                            <div class="flex-grow-1">
                                <div class="d-flex justify-content-between align-items-center mb-2">
                                    <strong>${speakerName}</strong>
                                    <small class="text-muted">Turn ${index + 1}</small>
                                </div>
                                <div class="mb-2">${turn.message || 'No message content'}</div>
                                ${turn.ai_reasoning ? `<div class="text-muted small"><strong>AI Reasoning:</strong> ${turn.ai_reasoning}</div>` : ''}
                                ${turn.ai_final_response ? `<div class="text-muted small"><strong>AI Response:</strong> ${turn.ai_final_response}</div>` : ''}
                            </div>
                        </div>
                    </div>
                `;
            });
            
            return html;
        }

        function getAnxietyColor(level) {
            if (level <= 3) return 'success';
            if (level <= 6) return 'warning';
            return 'danger';
        }

        function getAnxietyCategory(level) {
            if (level <= 3) return 'Low';
            if (level <= 6) return 'Moderate';
            return 'High';
        }
    </script>
</body>
</html>'''
    
    # Create the optimization template
    optimization_template = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TRUE GEPA Optimization Results - AI Dummy Analysis</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        .generation-card {
            transition: transform 0.2s, box-shadow 0.2s;
            cursor: pointer;
        }
        .generation-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        .prompt-card {
            transition: transform 0.2s, box-shadow 0.2s;
            cursor: pointer;
        }
        .prompt-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        }
        .performance-metric {
            font-size: 1.2em;
            font-weight: bold;
        }
        .improvement-positive { color: #28a745; }
        .improvement-negative { color: #dc3545; }
        .improvement-neutral { color: #6c757d; }
        .loading {
            text-align: center;
            padding: 50px;
            color: #6c757d;
        }
        .generation-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        .chart-container {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            margin: 20px 0;
        }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand" href="/">
                <i class="fas fa-robot me-2"></i>AI Dummy Analysis Dashboard
            </a>
            <div class="navbar-nav ms-auto">
                <a class="nav-link" href="/">
                    <i class="fas fa-home me-1"></i>Dashboard
                </a>
                <a class="nav-link active" href="/optimization">
                    <i class="fas fa-chart-line me-1"></i>TRUE GEPA Results
                </a>
            </div>
        </div>
    </nav>

    <div class="container mt-4">
        <!-- Header -->
        <div class="generation-header text-center">
            <h2><i class="fas fa-brain me-2"></i>TRUE GEPA Evolution Dashboard</h2>
            <p class="mb-0">5 Generations of Evolutionary Prompt Optimization</p>
            <p class="mb-0">AI Dummies • Test Runs • Component Discovery</p>
        </div>

        <!-- Best Results Chart -->
        <div class="chart-container">
            <h5 class="text-center mb-3"><i class="fas fa-chart-line me-2"></i>Best Performance by Generation</h5>
            <canvas id="generationChart" width="400" height="200"></canvas>
        </div>

        <!-- Generations Overview -->
        <div class="row" id="generationsContainer">
            <div class="loading">
                <i class="fas fa-spinner fa-spin fa-2x mb-3"></i>
                <p>Loading generations...</p>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        // Load optimization results on page load
        document.addEventListener('DOMContentLoaded', function() {
            loadOptimizationResults();
        });

        function loadOptimizationResults() {
            fetch('/api/optimization')
                .then(response => response.json())
                .then(data => {
                    displayGenerationsOverview(data);
                    initializeGenerationChart(data);
                })
                .catch(error => {
                    console.error('Error loading optimization results:', error);
                    document.getElementById('generationsContainer').innerHTML = 
                        '<div class="text-center text-danger"><i class="fas fa-exclamation-triangle me-2"></i>Error loading optimization results</div>';
                });
        }

        function displayGenerationsOverview(data) {
            const container = document.getElementById('generationsContainer');
            
            // Add toggle buttons for different views
            const toggleHtml = `
                <div class="row mb-4">
                    <div class="col-12 text-center">
                        <div class="btn-group" role="group">
                            <button type="button" class="btn btn-outline-primary active" onclick="switchView('generations')">
                                <i class="fas fa-layer-group me-2"></i>Evolutionary Process
                            </button>
                            <button type="button" class="btn btn-outline-success" onclick="switchView('pareto')">
                                <i class="fas fa-trophy me-2"></i>Pareto Frontier (7 Solutions)
                            </button>
                        </div>
                    </div>
                </div>
            `;
            
            // Use all_prompts to show total count per generation, then group by generation
            const displayData = data.all_prompts || data.best_per_generation || data.pareto_frontier;
            
            if (!data || !displayData || displayData.length === 0) {
                container.innerHTML = `
                    <div class="col-12 text-center text-muted">
                        <i class="fas fa-info-circle fa-3x mb-3"></i>
                        <h5>No optimization results available</h5>
                        <p>Run the TRUE GEPA optimization test to see results here.</p>
                        <a href="/" class="btn btn-primary">Back to Dashboard</a>
                    </div>
                `;
                return;
            }

            // Group prompts by generation
            const generations = {};
            displayData.forEach(prompt => {
                const gen = prompt.generation || 0;
                if (!generations[gen]) {
                    generations[gen] = [];
                }
                generations[gen].push(prompt);
            });

            let html = toggleHtml;
            
            // Create generation cards
            Object.keys(generations).sort((a, b) => parseInt(a) - parseInt(b)).forEach(genNum => {
                const genPrompts = generations[genNum];
                const bestPrompt = genPrompts.reduce((best, current) => {
                    const bestScore = (best.performance_metrics?.avg_improvement || 0);
                    const currentScore = (current.performance_metrics?.avg_improvement || 0);
                    return currentScore > bestScore ? current : best;
                });

                const avgImprovement = bestPrompt.performance_metrics?.avg_improvement || 0;
                const totalPrompts = genPrompts.length;

                html += `
                    <div class="col-lg-4 col-md-6 mb-4">
                        <div class="card generation-card h-100" onclick="viewGeneration(${genNum})">
                            <div class="card-header text-center bg-primary text-white">
                                <h5 class="mb-0"><i class="fas fa-layer-group me-2"></i>Generation ${genNum}</h5>
                            </div>
                            <div class="card-body text-center">
                                <div class="performance-metric improvement-positive mb-3">
                                    +${avgImprovement.toFixed(2)} points
                                </div>

                                <div class="mb-3">
                                    <strong>Prompts:</strong> ${totalPrompts}
                                </div>
                                <div class="mb-3">
                                    <strong>Dummies Tested:</strong> ${bestPrompt.performance_metrics?.test_count || 0}
                                </div>
                                <button class="btn btn-outline-primary btn-sm">
                                    <i class="fas fa-eye me-1"></i>View Details
                                </button>
                            </div>
                        </div>
                    </div>
                `;
            });

            container.innerHTML = html;
        }
        
        function switchView(viewType) {
            const container = document.getElementById('generationsContainer');
            
            if (viewType === 'pareto') {
                // Show Pareto frontier solutions
                fetch('/api/optimization')
                    .then(response => response.json())
                    .then(data => {
                        const paretoData = data.pareto_frontier || [];
                        
                        if (paretoData.length === 0) {
                            container.innerHTML = `
                                <div class="col-12 text-center text-muted">
                                    <i class="fas fa-trophy fa-3x mb-3"></i>
                                    <h5>No Pareto frontier solutions available</h5>
                                    <p>These represent the 7 non-dominated solutions across all generations.</p>
                                </div>
                            `;
                            return;
                        }
                        
                        let html = `
                            <div class="row mb-4">
                                <div class="col-12 text-center">
                                    <div class="btn-group" role="group">
                                        <button type="button" class="btn btn-outline-primary" onclick="switchView('generations')">
                                            <i class="fas fa-layer-group me-2"></i>Evolutionary Process
                                        </button>
                                        <button type="button" class="btn btn-outline-success active" onclick="switchView('pareto')">
                                            <i class="fas fa-trophy me-2"></i>Pareto Frontier (${paretoData.length} Solutions)
                                        </button>
                                    </div>
                                </div>
                            </div>
                            <div class="row">
                                <div class="col-12 mb-3">
                                    <div class="alert alert-info">
                                        <i class="fas fa-info-circle me-2"></i>
                                        <strong>Pareto Frontier:</strong> These ${paretoData.length} solutions are non-dominated across all 20 assessment criteria. 
                                        Each represents a different optimization strategy for social skills training.
                                    </div>
                                </div>
                            </div>
                        `;
                        
                        paretoData.forEach((prompt, index) => {
                            const avgImprovement = prompt.performance_metrics?.avg_improvement || 0;
                            
                            html += `
                                <div class="col-lg-6 col-md-12 mb-4">
                                    <div class="card prompt-card h-100" onclick="viewPrompt('${prompt.id}')">
                                        <div class="card-header text-center bg-success text-white">
                                            <h6 class="mb-0"><i class="fas fa-trophy me-2"></i>Pareto Solution ${index + 1}</h6>
                                        </div>
                                        <div class="card-body">
                                            <div class="mb-3">
                                                <strong>Name:</strong> ${prompt.name}
                                            </div>
                                            <div class="mb-3">
                                                <strong>Generation:</strong> ${prompt.generation}
                                            </div>
                                            <div class="mb-3">
                                                <strong>Prompt:</strong><br>
                                                <small class="text-muted">${prompt.prompt_text}</small>
                                            </div>
                                            <div class="row text-center">
                                                <div class="col-12">
                                                    <div class="performance-metric improvement-positive">
                                                        +${avgImprovement.toFixed(2)}
                                                    </div>
                                                    <small>Avg Improvement</small>
                                                </div>
                                            </div>
                                            <div class="text-center mt-3">
                                                <button class="btn btn-outline-success btn-sm" onclick="viewPromptDetails('${prompt.id}')">
                                                    <i class="fas fa-eye me-1"></i>View ${prompt.performance_metrics?.test_count || 0} Dummy Results
                                                </button>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            `;
                        });
                        
                        container.innerHTML = html;
                    });
            } else {
                // Show evolutionary process (default view)
                loadOptimizationResults();
            }
        }

        function initializeGenerationChart(data) {
            // Use best_per_generation for chart display
            const displayData = data.all_prompts || data.best_per_generation || data.pareto_frontier;
            if (!displayData || displayData.length === 0) return;

            const ctx = document.getElementById('generationChart');
            if (!ctx) return;

            // Group by generation and find best performance
            const generations = {};
            displayData.forEach(prompt => {
                const gen = prompt.generation || 0;
                if (!generations[gen]) {
                    generations[gen] = [];
                }
                generations[gen].push(prompt);
            });

            const labels = Object.keys(generations).sort((a, b) => parseInt(a) - parseInt(b));
            const improvements = labels.map(gen => {
                const genPrompts = generations[gen];
                const bestPrompt = genPrompts.reduce((best, current) => {
                    const bestScore = (current.performance_metrics?.avg_improvement || 0);
                    const currentScore = (best.performance_metrics?.avg_improvement || 0);
                    return bestScore > currentScore ? best : current;
                });
                return bestPrompt.performance_metrics?.avg_improvement || 0;
            });

            new Chart(ctx, {
                type: 'line',
                data: {
                    labels: labels.map(gen => `Generation ${gen}`),
                    datasets: [{
                        label: 'Best Improvement (points)',
                        data: improvements,
                        borderColor: '#28a745',
                        backgroundColor: 'rgba(40, 167, 69, 0.1)',
                        borderWidth: 3,
                        pointBackgroundColor: '#28a745',
                        pointBorderColor: '#fff',
                        pointBorderWidth: 2,
                        pointRadius: 6
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        title: {
                            display: true,
                            text: 'Performance Evolution Across Generations'
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            title: {
                                display: true,
                                text: 'Improvement (points)'
                            }
                        },
                        x: {
                            title: {
                                display: true,
                                text: 'Generation'
                            }
                        }
                    }
                }
            });
        }

        function viewGeneration(generationNum) {
            window.location.href = `/generation/${generationNum}`;
        }

        function viewPromptDetails(promptId) {
            window.location.href = `/prompt/${promptId}`;
        }
    </script>
</body>
</html>'''

    # Write templates to files
    with open('templates/index.html', 'w', encoding='utf-8') as f:
        f.write(main_template)
    
    with open('templates/dummy_detail.html', 'w', encoding='utf-8') as f:
        f.write(detail_template)
    
    with open('templates/optimization.html', 'w', encoding='utf-8') as f:
        f.write(optimization_template)
    
    # Create the generation detail template
    generation_detail_template = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Generation {{ generation_num }} - TRUE GEPA Optimization</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        .prompt-card {
            transition: transform 0.2s, box-shadow 0.2s;
            cursor: pointer;
        }
        .prompt-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        }
        .performance-metric {
            font-size: 1.1em;
            font-weight: bold;
        }
        .improvement-positive { color: #28a745; }
        .improvement-negative { color: #dc3545; }
        .improvement-neutral { color: #6c757d; }
        .loading {
            text-align: center;
            padding: 50px;
            color: #6c757d;
        }
        .generation-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
        }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand" href="/">
                <i class="fas fa-robot me-2"></i>AI Dummy Analysis Dashboard
            </a>
            <div class="navbar-nav ms-auto">
                <a class="nav-link" href="/">
                    <i class="fas fa-home me-1"></i>Dashboard
                </a>
                <a class="nav-link" href="/optimization">
                    <i class="fas fa-chart-line me-1"></i>TRUE GEPA Results
                </a>
                <a class="nav-link active" href="/generation/{{ generation_num }}">
                    <i class="fas fa-layer-group me-1"></i>Generation {{ generation_num }}
                </a>
            </div>
        </div>
    </nav>

    <div class="container mt-4">
        <!-- Header -->
        <div class="generation-header text-center">
            <h2><i class="fas fa-layer-group me-2"></i>Generation {{ generation_num }}</h2>
            <p class="mb-0">Evolutionary Prompt Optimization Results</p>
            <p class="mb-0">Crossed and Mutated Prompts with AI Dummy Test Results</p>
        </div>

        <!-- Prompts in this Generation -->
        <div class="row" id="promptsContainer">
            <div class="loading">
                <i class="fas fa-spinner fa-spin fa-2x mb-3"></i>
                <p>Loading generation prompts...</p>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        const generationNum = {{ generation_num }};
        
        // Load generation data on page load
        document.addEventListener('DOMContentLoaded', function() {
            loadGenerationData(generationNum);
        });

        function loadGenerationData(genNum) {
            fetch(`/api/generation/${genNum}`)
                .then(response => response.json())
                .then(data => {
                    displayGenerationPrompts(data);
                })
                .catch(error => {
                    console.error('Error loading generation data:', error);
                    document.getElementById('promptsContainer').innerHTML = 
                        '<div class="text-center text-danger"><i class="fas fa-exclamation-triangle me-2"></i>Error loading generation data</div>';
                });
        }

        function displayGenerationPrompts(data) {
            const container = document.getElementById('promptsContainer');
            
            if (!data.prompts || data.prompts.length === 0) {
                container.innerHTML = `
                    <div class="col-12 text-center text-muted">
                        <i class="fas fa-info-circle fa-3x mb-3"></i>
                        <h5>No prompts found for Generation ${data.generation}</h5>
                        <p>This generation may not have been completed yet.</p>
                        <a href="/optimization" class="btn btn-primary">Back to Generations</a>
                    </div>
                `;
                return;
            }

            let html = '';
            
            // Create prompt cards
            data.prompts.forEach((prompt, index) => {
                const avgImprovement = prompt.performance_metrics?.avg_improvement || 0;
                const testCount = prompt.performance_metrics?.test_count || 0;

                html += `
                    <div class="col-lg-6 col-md-12 mb-4">
                        <div class="card prompt-card h-100" onclick="viewPrompt('${prompt.id}')">
                            <div class="card-header text-center bg-info text-white">
                                <h6 class="mb-0"><i class="fas fa-puzzle-piece me-2"></i>${prompt.name}</h6>
                            </div>
                            <div class="card-body">
                                <div class="mb-3">
                                    <strong>Prompt Text:</strong><br>
                                    <small class="text-muted">${prompt.prompt_text}</small>
                                </div>
                                <div class="row text-center">
                                    <div class="col-6">
                                        <div class="performance-metric improvement-positive">
                                            +${avgImprovement.toFixed(2)}
                                        </div>
                                        <small>Improvement</small>
                                    </div>
                                    <div class="col-6">
                                        <div class="performance-metric">
                                            ${testCount}
                                        </div>
                                        <small>Tests</small>
                                    </div>
                                </div>
                                <div class="text-center mt-3">
                                    <button class="btn btn-outline-info btn-sm" onclick="viewPromptDetails('${prompt.id}')">
                                        <i class="fas fa-eye me-1"></i>View All ${prompt.performance_metrics?.test_count || 0} Dummy Results
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                `;
            });

            container.innerHTML = html;
        }

        function viewPrompt(promptId) {
            window.location.href = `/prompt/${promptId}`;
        }
    </script>
</body>
</html>'''
    
    print("🌐 Web interface created successfully!")
    print("📁 Templates saved to: templates/")
    
    # Create the prompt detail template
    prompt_detail_template = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Prompt Results - TRUE GEPA Optimization</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        .dummy-result-card {
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .dummy-result-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        }
        .performance-metric {
            font-size: 1.1em;
            font-weight: bold;
        }
        .improvement-positive { color: #28a745; }
        .improvement-negative { color: #dc3545; }
        .improvement-neutral { color: #6c757d; }
        .loading {
            text-align: center;
            padding: 50px;
            color: #6c757d;
        }
        .prompt-header {
            background: linear-gradient(135deg, #17a2b8 0%, #138496 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        .conversation-turn {
            margin-bottom: 15px;
            padding: 15px;
            border-radius: 10px;
        }
        .dummy-turn {
            background-color: #f8f9fa;
            border-left: 5px solid #007bff;
        }
        .ai-turn {
            background-color: #e7f3ff;
            border-left: 5px solid #28a745;
        }
        .assessment-question {
            margin-bottom: 12px;
            padding: 10px;
            background-color: #f8f9fa;
            border-radius: 8px;
            border-left: 3px solid #dee2e6;
        }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand" href="/">
                <i class="fas fa-robot me-2"></i>AI Dummy Analysis Dashboard
            </a>
            <div class="navbar-nav ms-auto">
                <a class="nav-link" href="/">
                    <i class="fas fa-home me-1"></i>Dashboard
                </a>
                <a class="nav-link" href="/optimization">
                    <i class="fas fa-chart-line me-1"></i>TRUE GEPA Results
                </a>
                <a class="nav-link" href="/generation/0">
                    <i class="fas fa-layer-group me-1"></i>Generations
                </a>
                <a class="nav-link active" href="#">
                    <i class="fas fa-puzzle-piece me-1"></i>Prompt Results
                </a>
            </div>
        </div>
    </nav>

    <div class="container mt-4">
        <!-- Prompt Header -->
        <div class="prompt-header" id="promptHeader">
            <div class="loading">
                <i class="fas fa-spinner fa-spin fa-2x mb-3"></i>
                <p>Loading prompt details...</p>
            </div>
        </div>

        <!-- Dummy Results -->
        <div class="row" id="dummyResultsContainer">
            <div class="loading">
                <i class="fas fa-spinner fa-spin fa-2x mb-3"></i>
                <p>Loading dummy results...</p>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        const promptId = window.location.pathname.split('/').pop();
        
        // Load prompt data on page load
        document.addEventListener('DOMContentLoaded', function() {
            loadPromptData(promptId);
        });

        function loadPromptData(promptId) {
            fetch(`/api/prompt/${promptId}`)
                .then(response => response.json())
                .then(data => {
                    displayPromptHeader(data.prompt);
                    displayDummyResults(data.results);
                })
                .catch(error => {
                    console.error('Error loading prompt data:', error);
                    document.getElementById('promptHeader').innerHTML = 
                        '<div class="text-center text-danger"><i class="fas fa-exclamation-triangle me-2"></i>Error loading prompt data</div>';
                });
        }

        function displayPromptHeader(prompt) {
            const header = document.getElementById('promptHeader');
            
            const avgImprovement = prompt.performance_metrics?.avg_improvement || 0;
            const testCount = prompt.performance_metrics?.test_count || 0;

            header.innerHTML = `
                <div class="row">
                    <div class="col-md-8">
                        <h3><i class="fas fa-puzzle-piece me-2"></i>${prompt.name}</h3>
                        <p class="mb-2"><strong>Prompt Text:</strong> ${prompt.prompt_text}</p>
                        <p class="mb-0"><strong>Generation:</strong> ${prompt.generation}</p>
                    </div>
                    <div class="col-md-4 text-center">
                        <div class="row">
                            <div class="col-6">
                                <div class="performance-metric improvement-positive">
                                    +${avgImprovement.toFixed(2)}
                                </div>
                                <small>Improvement</small>
                            </div>
                            <div class="col-6">
                                <div class="performance-metric">
                                    ${testCount}
                                </div>
                                <small>Tests</small>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        }

        function displayDummyResults(results) {
            const container = document.getElementById('dummyResultsContainer');
            
            if (!results || results.length === 0) {
                container.innerHTML = `
                    <div class="col-12 text-center text-muted">
                        <i class="fas fa-info-circle fa-3x mb-3"></i>
                        <h5>No dummy results found for this prompt</h5>
                        <p>This prompt may not have been tested yet.</p>
                    </div>
                `;
                return;
            }

            let html = '';
            
            // Create dummy result cards
            results.forEach((item, index) => {
                const result = item.result;
                const dummy = item.dummy;
                
                if (!dummy) return;

                const improvement = result.improvement || 0;
                const improvementClass = improvement > 0 ? 'improvement-positive' : 
                                       improvement < 0 ? 'improvement-negative' : 'improvement-neutral';
                const improvementIcon = improvement > 0 ? 'fa-arrow-up' : 
                                      improvement < 0 ? 'fa-arrow-down' : 'fa-minus';

                html += `
                    <div class="col-lg-6 col-md-12 mb-4">
                        <div class="card dummy-result-card h-100">
                            <div class="card-header">
                                <div class="d-flex justify-content-between align-items-center">
                                    <h6 class="mb-0"><i class="fas fa-user me-2"></i>${dummy.name || 'Unknown'}</h6>
                                    <span class="badge bg-secondary">${dummy.gender || 'Unknown'}, ${dummy.age || 0}</span>
                                </div>
                            </div>
                            <div class="card-body">
                                <!-- Compact Performance Summary -->
                                <div class="row text-center mb-3">
                                    <div class="col-6">
                                        <div class="performance-metric ${improvementClass}">
                                            <i class="fas ${improvementIcon} me-1"></i>
                                            ${improvement > 0 ? '+' : ''}${improvement.toFixed(2)}
                                        </div>
                                        <small>Improvement</small>
                                    </div>
                                    <div class="col-6">
                                        <div class="performance-metric text-${dummy.social_anxiety?.anxiety_level <= 3 ? 'success' : dummy.social_anxiety?.anxiety_level <= 6 ? 'warning' : 'danger'}">
                                            ${dummy.social_anxiety?.anxiety_level || 0}/10
                                        </div>
                                        <small>Anxiety Level</small>
                                    </div>
                                </div>

                                <!-- Expandable Details -->
                                <div class="accordion" id="accordion${index}">
                                    <!-- Assessment Details -->
                                    <div class="accordion-item">
                                        <h2 class="accordion-header">
                                            <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#assessment${index}">
                                                <i class="fas fa-clipboard me-2"></i>Assessment Details
                                            </button>
                                        </h2>
                                        <div id="assessment${index}" class="accordion-collapse collapse" data-bs-parent="#accordion${index}">
                                            <div class="accordion-body">
                                                <div class="row">
                                                    <div class="col-md-6">
                                                        <h6 class="text-primary">Pre-Assessment</h6>
                                                        <p><strong>Score:</strong> ${(result.pre_score || 0).toFixed(2)}/4.0</p>
                                                    </div>
                                                    <div class="col-md-6">
                                                        <h6 class="text-success">Post-Assessment</h6>
                                                        <p><strong>Score:</strong> ${(result.post_score || 0).toFixed(2)}/4.0</p>
                                                    </div>
                                                </div>
                                                <div class="text-center">
                                                    <span class="badge bg-${improvement > 0 ? 'success' : improvement < 0 ? 'danger' : 'secondary'} fs-6">
                                                        ${improvement > 0 ? 'Improved' : improvement < 0 ? 'Declined' : 'No Change'}: ${improvement > 0 ? '+' : ''}${improvement.toFixed(2)} points
                                                    </span>
                                                </div>
                                            </div>
                                        </div>
                                    </div>

                                    <!-- Conversation Details -->
                                    <div class="accordion-item">
                                        <h2 class="accordion-header">
                                            <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#conversation${index}">
                                                <i class="fas fa-comments me-2"></i>Conversation Details
                                            </button>
                                        </h2>
                                        <div id="conversation${index}" class="accordion-collapse collapse" data-bs-parent="#accordion${index}">
                                            <div class="accordion-body">
                                                ${result.conversation && result.conversation.length > 0 ? `
                                                    <h6 class="text-primary mb-3"><i class="fas fa-comments me-2"></i>Full Conversation</h6>
                                                    <div class="conversation-container">
                                                        ${result.conversation.map((turn, turnIndex) => `
                                                            <div class="conversation-turn ${turn.speaker === 'dummy' ? 'dummy-turn' : 'ai-turn'}">
                                                                <div class="d-flex justify-content-between align-items-center mb-2">
                                                                    <strong>${turn.speaker === 'dummy' ? dummy.name : 'AI Assistant'}</strong>
                                                                    <small class="text-muted">Turn ${turnIndex + 1}</small>
                                                                </div>
                                                                <p class="mb-0">${turn.content}</p>
                                                            </div>
                                                        `).join('')}
                                                    </div>
                                                ` : `
                                                    <p class="text-muted"><i class="fas fa-info-circle me-2"></i>No conversation data available</p>
                                                `}
                                                
                                                ${result.reflection_insights && result.reflection_insights.length > 0 ? `
                                                    <hr class="my-3">
                                                    <h6 class="text-success mb-3"><i class="fas fa-lightbulb me-2"></i>Reflection Insights</h6>
                                                    <ul>
                                                        ${result.reflection_insights.map(insight => `<li>${insight}</li>`).join('')}
                                                    </ul>
                                                ` : ''}
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                `;
            });

            container.innerHTML = html;
        }
    </script>
</body>
</html>'''
    
    # Write all templates to files
    with open('templates/optimization.html', 'w', encoding='utf-8') as f:
        f.write(optimization_template)
    
    with open('templates/generation_detail.html', 'w', encoding='utf-8') as f:
        f.write(generation_detail_template)
    
    with open('templates/prompt_detail.html', 'w', encoding='utf-8') as f:
        f.write(prompt_detail_template)
    print("🚀 Starting Flask server...")
    print("📱 Open your browser and go to: http://localhost:5000")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
