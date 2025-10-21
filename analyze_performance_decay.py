#!/usr/bin/env python3
"""
Analyze performance decay in conversation length experiments.

This script examines why assessment scores might be declining during conversations.
"""

import json
import sys
from typing import Dict, List
from statistics import mean

def analyze_experiment(filepath: str):
    """Analyze a conversation length experiment for performance decay patterns"""
    
    with open(filepath) as f:
        data = json.load(f)
    
    exp_info = data['experiment_info']
    results = data['results']
    
    print("="*80)
    print("PERFORMANCE DECAY ANALYSIS")
    print("="*80)
    print(f"\n📊 Experiment Configuration:")
    print(f"   • Max turns: {exp_info['max_turns']}")
    print(f"   • Milestone turns: {exp_info.get('assessment_milestone_turns', 'N/A')}")
    print(f"   • Dummies: {exp_info['num_dummies']}")
    print(f"   • Prompt: {exp_info['base_prompt'][:100]}...")
    
    # Analyze conversation lengths
    print(f"\n📏 Conversation Lengths:")
    turn_counts = [r['total_conversation_turns'] for r in results]
    print(f"   • Average: {mean(turn_counts):.1f} turns")
    print(f"   • Min: {min(turn_counts)} turns")
    print(f"   • Max: {max(turn_counts)} turns")
    print(f"   • Ended early: {sum(1 for r in results if r.get('conversation_ended_early', False))}/{len(results)}")
    
    # Analyze overall improvement
    print(f"\n📈 Overall Performance:")
    improvements = [r['final_improvement'] for r in results]
    print(f"   • Average improvement: {mean(improvements):+.3f}")
    print(f"   • Best: {max(improvements):+.3f}")
    print(f"   • Worst: {min(improvements):+.3f}")
    print(f"   • Positive: {sum(1 for i in improvements if i > 0)}/{len(improvements)}")
    print(f"   • Negative: {sum(1 for i in improvements if i < 0)}/{len(improvements)}")
    
    # Analyze milestone patterns
    print(f"\n🎯 Milestone Performance Patterns:")
    
    # Collect scores at each milestone
    milestone_data = {}
    for result in results:
        for milestone in result['milestone_results']:
            turn = milestone.get('milestone_turn', milestone.get('milestone_rounds', 0))
            if turn not in milestone_data:
                milestone_data[turn] = {
                    'scores': [],
                    'improvements': [],
                    'reached_count': 0,
                    'total_count': 0
                }
            
            milestone_data[turn]['total_count'] += 1
            if milestone.get('reached', True):
                milestone_data[turn]['reached_count'] += 1
                milestone_data[turn]['scores'].append(milestone['milestone_score'])
                milestone_data[turn]['improvements'].append(milestone['improvement'])
    
    # Print milestone analysis
    for turn in sorted(milestone_data.keys()):
        md = milestone_data[turn]
        if md['scores']:
            avg_score = mean(md['scores'])
            avg_improvement = mean(md['improvements'])
            reached_pct = 100 * md['reached_count'] / md['total_count']
            
            print(f"\n   Turn {turn}:")
            print(f"      • Reached: {md['reached_count']}/{md['total_count']} ({reached_pct:.0f}%)")
            print(f"      • Avg score: {avg_score:.3f}")
            print(f"      • Avg improvement: {avg_improvement:+.3f}")
            
            if len(md['improvements']) > 1:
                pos = sum(1 for x in md['improvements'] if x > 0)
                neg = sum(1 for x in md['improvements'] if x < 0)
                print(f"      • Distribution: {pos} positive, {neg} negative")
    
    # Analyze specific problematic conversations
    print(f"\n⚠️  Most Problematic Conversations:")
    negative_results = sorted(
        [(r['dummy_name'], r['final_improvement'], r['total_conversation_turns']) 
         for r in results if r['final_improvement'] < -0.1],
        key=lambda x: x[1]
    )[:5]
    
    for name, improvement, turns in negative_results:
        print(f"   • {name}: {improvement:+.3f} ({turns} turns)")
    
    # Check for early ending correlation
    print(f"\n🔍 Early Ending vs Performance:")
    early_ended = [r for r in results if r.get('conversation_ended_early', False)]
    completed = [r for r in results if not r.get('conversation_ended_early', False)]
    
    if early_ended:
        early_improvements = [r['final_improvement'] for r in early_ended]
        print(f"   • Early ended avg: {mean(early_improvements):+.3f} (n={len(early_ended)})")
    
    if completed:
        completed_improvements = [r['final_improvement'] for r in completed]
        print(f"   • Completed avg: {mean(completed_improvements):+.3f} (n={len(completed)})")

if __name__ == "__main__":
    import glob
    
    # Find latest experiment file if no argument provided
    if len(sys.argv) > 1:
        filepath = sys.argv[1]
    else:
        # Find latest continuous_conversation_with_evolution experiment
        files = glob.glob("data/experiments/continuous_conversation_with_evolution_exp_*.json")
        if not files:
            print("No experiment files found!")
            sys.exit(1)
        filepath = sorted(files)[-1]
        print(f"Using latest experiment: {filepath}\n")
    
    analyze_experiment(filepath)

