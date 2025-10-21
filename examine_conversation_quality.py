#!/usr/bin/env python3
"""
Examine conversation quality to understand why assessments might be negative.

This script looks at actual conversation content and assessment responses
to identify issues.
"""

import json
import sys
from typing import Dict, List

def examine_conversation(filepath: str, dummy_name: str = None):
    """Examine specific conversation details"""
    
    with open(filepath) as f:
        data = json.load(f)
    
    results = data['results']
    
    # Find the dummy with the worst performance if not specified
    if dummy_name is None:
        worst_result = min(results, key=lambda r: r['final_improvement'])
        dummy_name = worst_result['dummy_name']
        print(f"📉 Examining worst performer: {dummy_name}")
        print(f"   Improvement: {worst_result['final_improvement']:+.3f}\n")
    
    # Find the dummy's data
    result = next((r for r in results if r['dummy_name'] == dummy_name), None)
    if not result:
        print(f"❌ Dummy '{dummy_name}' not found!")
        return
    
    print("="*80)
    print(f"CONVERSATION QUALITY EXAMINATION: {dummy_name}")
    print("="*80)
    
    # Show assessment trajectory
    print(f"\n📊 Assessment Trajectory:")
    print(f"   Pre-assessment: {result['pre_assessment_score']:.2f}")
    
    for milestone in result['milestone_results']:
        turn = milestone.get('milestone_turn', milestone.get('milestone_rounds', 0))
        print(f"   Turn {turn}: {milestone['milestone_score']:.2f} (Δ {milestone['improvement']:+.3f})")
    
    print(f"   Final: {result['final_assessment_score']:.2f} (Total Δ {result['final_improvement']:+.3f})")
    
    # Show conversation details if available
    if 'conversation_details' in result and result['conversation_details']:
        conv_details = result['conversation_details']
        
        if 'conversation' in conv_details:
            conversation = conv_details['conversation']
            turns = conversation.get('turns', [])
            
            print(f"\n💬 Conversation ({len(turns)} turns):")
            print(f"\n   First 3 exchanges:")
            for i, turn in enumerate(turns[:6]):  # First 3 exchanges (6 turns)
                speaker = "👤 Student" if turn['speaker'] == 'dummy' else "🤖 Mentor"
                message = turn['message'][:150] + "..." if len(turn['message']) > 150 else turn['message']
                print(f"\n   Turn {i+1} ({speaker}):")
                print(f"      {message}")
            
            if len(turns) > 6:
                print(f"\n   ... (showing first 3 exchanges, total {len(turns)} turns)")
        
        # Show pre-assessment details
        if 'pre_assessment' in conv_details:
            pre_assessment = conv_details['pre_assessment']
            print(f"\n📋 Pre-Assessment Highlights (first 5 criteria):")
            
            responses = pre_assessment.get('responses', [])
            for i, resp in enumerate(responses[:5]):
                question = resp['question'][:60] + "..." if len(resp['question']) > 60 else resp['question']
                score = resp['score']
                print(f"   {i+1}. {question}")
                print(f"      Score: {score}/4")
        
        # Show post-assessment to compare
        if 'post_assessment' in conv_details:
            post_assessment = conv_details['post_assessment']
            print(f"\n📋 Post-Assessment Highlights (first 5 criteria):")
            
            pre_responses = pre_assessment.get('responses', [])
            post_responses = post_assessment.get('responses', [])
            
            for i in range(min(5, len(post_responses))):
                question = post_responses[i]['question'][:60] + "..." if len(post_responses[i]['question']) > 60 else post_responses[i]['question']
                pre_score = pre_responses[i]['score'] if i < len(pre_responses) else 2.5
                post_score = post_responses[i]['score']
                change = post_score - pre_score
                
                symbol = "📈" if change > 0 else "📉" if change < 0 else "➡️"
                print(f"   {i+1}. {question}")
                print(f"      {symbol} {pre_score} → {post_score} (Δ {change:+.1f})")
    
    # Show personality info
    print(f"\n🧑 Dummy Profile:")
    if 'conversation_details' in result and 'dummy_profile' in result['conversation_details']:
        profile = result['conversation_details']['dummy_profile']
        print(f"   Anxiety level: {profile.get('anxiety_level', 'N/A')}/10")
        
        fears = profile.get('fears', [])
        if fears:
            print(f"   Fears: {', '.join(fears[:3])}")
        
        challenges = profile.get('challenges', [])
        if challenges:
            print(f"   Challenges: {', '.join(challenges[:3])}")
    
    return result

def compare_best_and_worst(filepath: str):
    """Compare best and worst performing conversations"""
    
    with open(filepath) as f:
        data = json.load(f)
    
    results = data['results']
    
    best = max(results, key=lambda r: r['final_improvement'])
    worst = min(results, key=lambda r: r['final_improvement'])
    
    print("="*80)
    print("BEST vs WORST COMPARISON")
    print("="*80)
    
    print(f"\n🏆 BEST: {best['dummy_name']}")
    print(f"   Improvement: {best['final_improvement']:+.3f}")
    print(f"   Pre: {best['pre_assessment_score']:.2f} → Post: {best['final_assessment_score']:.2f}")
    print(f"   Turns: {best['total_conversation_turns']}")
    
    print(f"\n📉 WORST: {worst['dummy_name']}")
    print(f"   Improvement: {worst['final_improvement']:+.3f}")
    print(f"   Pre: {worst['pre_assessment_score']:.2f} → Post: {worst['final_assessment_score']:.2f}")
    print(f"   Turns: {worst['total_conversation_turns']}")
    
    print(f"\n🔍 Detailed Examination of WORST:")
    examine_conversation(filepath, worst['dummy_name'])

if __name__ == "__main__":
    import glob
    
    # Find latest experiment file if no argument provided
    if len(sys.argv) > 1:
        filepath = sys.argv[1]
    else:
        files = glob.glob("data/experiments/continuous_conversation_with_evolution_exp_*.json")
        if not files:
            print("No experiment files found!")
            sys.exit(1)
        filepath = sorted(files)[-1]
        print(f"Using latest experiment: {filepath}\n")
    
    # Run comparison
    compare_best_and_worst(filepath)

