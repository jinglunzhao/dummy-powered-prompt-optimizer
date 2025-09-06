#!/usr/bin/env python3
"""
Simple Test: Performance + Diversity Balance
===========================================

This script tests the corrected enhanced crossover with actual LLM calls
and shows the generated child prompts clearly.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from corrected_enhanced_crossover import CorrectedEnhancedCrossover, ParentPerformanceProfile
import requests
import json
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_determinism():
    """Test if the model generates different prompts with higher temperature"""
    
    print("🧬 Testing LLM Determinism with Higher Temperature")
    print("=" * 60)
    
    # Initialize corrected crossover
    crossover = CorrectedEnhancedCrossover()
    
    # Create parent performance profiles based on actual assessment results
    parent1_profile = ParentPerformanceProfile(
        prompt_text="Be supportive and provide practical, confidence-building advice",
        performance_metrics={
            'improvement_build_confidence': 0.85,
            'improvement_show_empathy': 0.78,
            'improvement_provide_feedback': 0.72,
            'improvement_encourage_participation': 0.68,
            'improvement_ask_for_help': 0.45,
            'avg_improvement': 0.65
        },
        top_performing_criteria=[('build_confidence', 0.85), ('show_empathy', 0.78), ('provide_feedback', 0.72)],
        weak_criteria=[('ask_for_help', 0.45)],
        performance_pattern={
            'top_3_criteria': ['build_confidence', 'show_empathy', 'provide_feedback'],
            'contributing_characteristics': ['supportive_approach', 'confidence_focused', 'feedback_focused'],
            'dominant_approach': 'supportive_approach',
            'structure_analysis': {
                'has_question': False,
                'has_action_verb': True,
                'has_qualifier': True,
                'is_directive': True,
                'is_collaborative': False
            }
        },
        generation=2,
        length=67
    )
    
    parent2_profile = ParentPerformanceProfile(
        prompt_text="Guide students through social challenges with empathy and practical strategies",
        performance_metrics={
            'improvement_show_empathy': 0.92,
            'improvement_guide': 0.88,
            'improvement_handle_conflict': 0.85,
            'improvement_foster_connection': 0.82,
            'improvement_ask_for_help': 0.78,
            'avg_improvement': 0.80
        },
        top_performing_criteria=[('show_empathy', 0.92), ('guide', 0.88), ('handle_conflict', 0.85)],
        weak_criteria=[('build_confidence', 0.70)],
        performance_pattern={
            'top_3_criteria': ['show_empathy', 'guide', 'handle_conflict'],
            'contributing_characteristics': ['collaborative_approach', 'empathy_focused', 'practical_approach'],
            'dominant_approach': 'collaborative_approach',
            'structure_analysis': {
                'has_question': False,
                'has_action_verb': True,
                'has_qualifier': True,
                'is_directive': False,
                'is_collaborative': True
            }
        },
        generation=2,
        length=78
    )
    
    # Simulate existing population
    existing_prompts = [
        "Be supportive and provide practical, confidence-building advice",
        "Be supportive and provide practical, growth-oriented advice"
    ]
    
    # Create crossover prompt (same for all tests)
    print("📝 Creating crossover prompt...")
    enhanced_prompt = crossover.create_performance_diversity_crossover_prompt(
        parent1_profile, parent2_profile, existing_prompts, diversity_weight=0.7
    )
    
    print(f"📏 LLM instruction length: {len(enhanced_prompt)} characters")
    print("🔄 Testing with temperature 0.9 - generating 10 prompts...")
    
    # Generate 10 prompts to test determinism
    generated_prompts = []
    
    try:
        from config import Config
        
        for i in range(10):
            print(f"\n--- Generation {i+1}/10 ---")
            
            response = requests.post(
                "https://api.deepseek.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {Config.DEEPSEEK_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "deepseek-chat",
                    "messages": [{"role": "user", "content": enhanced_prompt}],
                    "temperature": 0.9,  # Higher temperature for diversity
                    "max_tokens": 200
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if 'choices' in result and len(result['choices']) > 0:
                    generated_text = result['choices'][0]['message']['content'].strip()
                    generated_prompts.append(generated_text)
                    
                    print(f'Prompt {i+1}: "{generated_text}"')
                    print(f'Length: {len(generated_text)} characters')
                else:
                    print(f"❌ No choices in response for generation {i+1}")
            else:
                print(f"❌ API Error for generation {i+1}: {response.status_code}")
                
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Analyze results
    print(f"\n📊 Determinism Analysis:")
    print(f"Total prompts generated: {len(generated_prompts)}")
    
    if len(generated_prompts) > 1:
        unique_prompts = list(set(generated_prompts))
        print(f"Unique prompts: {len(unique_prompts)}")
        print(f"Determinism rate: {len(unique_prompts)/len(generated_prompts):.2%}")
        
        if len(unique_prompts) == 1:
            print("🔴 Model is DETERMINISTIC - same input always gives same output")
        elif len(unique_prompts) < len(generated_prompts) * 0.5:
            print("🟡 Model is PARTIALLY DETERMINISTIC - some variation but limited")
        else:
            print("🟢 Model is NON-DETERMINISTIC - good variation in outputs")
            
        # Show unique prompts
        print(f"\n🔍 Unique Prompts Generated:")
        for i, prompt in enumerate(unique_prompts, 1):
            print(f"{i}. \"{prompt}\"")
    else:
        print("❌ Not enough prompts generated for analysis")

if __name__ == "__main__":
    test_determinism()
