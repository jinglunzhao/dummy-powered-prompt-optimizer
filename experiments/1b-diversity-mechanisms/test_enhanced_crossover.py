#!/usr/bin/env python3
"""
Test Enhanced Crossover: Performance + Diversity Balance
=======================================================

This script tests the enhanced crossover approach that balances:
1. Preserving parent performance strengths
2. Encouraging diversity and uniqueness
3. Maintaining effectiveness while adding variety
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from enhanced_crossover import EnhancedCrossover, ParentAnalysis
import requests
import json
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_enhanced_crossover():
    """Test the enhanced crossover with real examples"""
    
    # Initialize enhanced crossover
    crossover = EnhancedCrossover()
    
    # Create realistic parent analyses based on our validation results
    parent1_analysis = ParentAnalysis(
        prompt_text="Be supportive and provide practical, confidence-building advice",
        performance_metrics={
            'improvement_build_confidence': 0.85,
            'improvement_show_empathy': 0.78,
            'improvement_provide_feedback': 0.72,
            'improvement_encourage_participation': 0.68,
            'improvement_ask_for_help': 0.45,
            'improvement_stay_calm': 0.82,
            'improvement_listen_actively': 0.75,
            'improvement_express_clearly': 0.70,
            'improvement_ask_clarifying': 0.38,
            'improvement_give_constructive': 0.80,
            'improvement_handle_conflict': 0.65,
            'improvement_respect_boundaries': 0.73,
            'improvement_offer_support': 0.77,
            'improvement_celebrate_success': 0.69,
            'improvement_address_concerns': 0.71,
            'improvement_foster_connection': 0.66,
            'improvement_model_behavior': 0.74,
            'improvement_create_safety': 0.68,
            'improvement_promote_growth': 0.76,
            'improvement_maintain_balance': 0.72
        },
        strengths=[('build_confidence', 0.85), ('show_empathy', 0.78), ('provide_feedback', 0.72)],
        weaknesses=[('ask_clarifying', 0.38), ('ask_for_help', 0.45)],
        style_characteristics={
            'tone': {'encouraging': 2, 'direct': 1, 'collaborative': 0},
            'structure': {'has_question': False, 'has_action_verb': True, 'has_qualifier': True},
            'approaches': {'practical': 2, 'confidence': 1, 'emotional': 0, 'social': 0},
            'dominant_tone': 'encouraging',
            'dominant_approach': 'practical'
        },
        length=67,
        generation=2
    )
    
    parent2_analysis = ParentAnalysis(
        prompt_text="Guide students through social challenges with empathy and practical strategies",
        performance_metrics={
            'improvement_show_empathy': 0.92,
            'improvement_guide': 0.88,
            'improvement_handle_conflict': 0.85,
            'improvement_foster_connection': 0.82,
            'improvement_ask_for_help': 0.78,
            'improvement_stay_calm': 0.75,
            'improvement_listen_actively': 0.88,
            'improvement_express_clearly': 0.80,
            'improvement_ask_clarifying': 0.82,
            'improvement_give_constructive': 0.85,
            'improvement_build_confidence': 0.70,
            'improvement_encourage_participation': 0.78,
            'improvement_respect_boundaries': 0.80,
            'improvement_offer_support': 0.85,
            'improvement_celebrate_success': 0.75,
            'improvement_address_concerns': 0.82,
            'improvement_model_behavior': 0.78,
            'improvement_provide_feedback': 0.80,
            'improvement_create_safety': 0.85,
            'improvement_promote_growth': 0.88,
            'improvement_maintain_balance': 0.80
        },
        strengths=[('show_empathy', 0.92), ('guide', 0.88), ('handle_conflict', 0.85)],
        weaknesses=[('build_confidence', 0.70)],
        style_characteristics={
            'tone': {'encouraging': 0, 'direct': 0, 'collaborative': 2},
            'structure': {'has_question': False, 'has_action_verb': True, 'has_qualifier': True},
            'approaches': {'practical': 1, 'confidence': 0, 'emotional': 1, 'social': 1},
            'dominant_tone': 'collaborative',
            'dominant_approach': 'emotional'
        },
        length=78,
        generation=2
    )
    
    # Simulate existing population (common patterns from our validation results)
    existing_prompts = [
        "Be supportive and provide practical, confidence-building advice",
        "Be supportive and provide practical, growth-oriented advice",
        "Be supportive and provide practical, growth-focused advice",
        "Be supportive and provide practical, confidence-building guidance",
        "Be supportive and provide practical, growth-oriented feedback",
        "Be supportive and provide practical, growth-focused guidance",
        "Be encouraging and provide practical, growth-oriented advice",
        "Listen actively and offer supportive, constructive guidance"
    ]
    
    print("🧬 Testing Enhanced Crossover: Performance + Diversity Balance")
    print("=" * 70)
    
    # Test 1: High diversity weight (prioritize uniqueness)
    print("\n📊 Test 1: High Diversity Weight (0.8)")
    print("-" * 50)
    
    prompt1 = crossover.create_performance_diversity_crossover_prompt(
        parent1_analysis, parent2_analysis, existing_prompts, diversity_weight=0.8
    )
    
    print("Generated LLM Instruction (first 200 chars):")
    print(f'"{prompt1[:200]}..."')
    print(f"Full length: {len(prompt1)} characters")
    
    # Test 2: Balanced weight (equal performance and diversity)
    print("\n📊 Test 2: Balanced Weight (0.5)")
    print("-" * 50)
    
    prompt2 = crossover.create_performance_diversity_crossover_prompt(
        parent1_analysis, parent2_analysis, existing_prompts, diversity_weight=0.5
    )
    
    print("Generated LLM Instruction (first 200 chars):")
    print(f'"{prompt2[:200]}..."')
    print(f"Full length: {len(prompt2)} characters")
    
    # Test 3: High performance weight (prioritize parent strengths)
    print("\n📊 Test 3: High Performance Weight (0.2)")
    print("-" * 50)
    
    prompt3 = crossover.create_performance_diversity_crossover_prompt(
        parent1_analysis, parent2_analysis, existing_prompts, diversity_weight=0.2
    )
    
    print("Generated LLM Instruction (first 200 chars):")
    print(f'"{prompt3[:200]}..."')
    print(f"Full length: {len(prompt3)} characters")
    
    # Analyze the results
    print("\n🔍 Analysis of Generated Prompts")
    print("=" * 70)
    
    for i, prompt in enumerate([prompt1, prompt2, prompt3], 1):
        print(f"\nPrompt {i}:")
        print(f'Text: "{prompt}"')
        print(f'Length: {len(prompt)} characters')
        
        # Calculate scores
        scores = crossover.calculate_performance_diversity_score(
            prompt, parent1_analysis, parent2_analysis, existing_prompts
        )
        
        print(f'Performance Score: {scores["performance_score"]:.3f}')
        print(f'Diversity Score: {scores["diversity_score"]:.3f}')
        print(f'Combined Score: {scores["combined_score"]:.3f}')
        
        # Analyze style
        child_style = crossover._analyze_style_characteristics(prompt)
        print(f'Style: {child_style["dominant_tone"]} tone, {child_style["dominant_approach"]} approach')

def test_with_llm():
    """Test the enhanced crossover with actual LLM calls"""
    
    print("\n🤖 Testing with Real LLM Calls")
    print("=" * 70)
    
    # Initialize enhanced crossover
    crossover = EnhancedCrossover()
    
    # Create parent analyses
    parent1_analysis = ParentAnalysis(
        prompt_text="Be supportive and provide practical, confidence-building advice",
        performance_metrics={'improvement_build_confidence': 0.85, 'improvement_show_empathy': 0.78},
        strengths=[('build_confidence', 0.85), ('show_empathy', 0.78)],
        weaknesses=[('ask_clarifying', 0.38)],
        style_characteristics={'dominant_tone': 'encouraging', 'dominant_approach': 'practical'},
        length=67,
        generation=2
    )
    
    parent2_analysis = ParentAnalysis(
        prompt_text="Guide students through social challenges with empathy and practical strategies",
        performance_metrics={'improvement_show_empathy': 0.92, 'improvement_guide': 0.88},
        strengths=[('show_empathy', 0.92), ('guide', 0.88)],
        weaknesses=[('build_confidence', 0.70)],
        style_characteristics={'dominant_tone': 'collaborative', 'dominant_approach': 'emotional'},
        length=78,
        generation=2
    )
    
    existing_prompts = [
        "Be supportive and provide practical, confidence-building advice",
        "Be supportive and provide practical, growth-oriented advice"
    ]
    
    # Create enhanced crossover prompt
    enhanced_prompt = crossover.create_performance_diversity_crossover_prompt(
        parent1_analysis, parent2_analysis, existing_prompts, diversity_weight=0.7
    )
    
    print("Enhanced Crossover Prompt:")
    print(enhanced_prompt)
    
    # Make LLM call
    try:
        from config import Config
        
        print("\n🔄 Making LLM call...")
        response = requests.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {Config.DEEPSEEK_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "deepseek-chat",
                "messages": [{"role": "user", "content": enhanced_prompt}],
                "temperature": 0.8,  # Higher temperature for diversity
                "max_tokens": 200
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if 'choices' in result and len(result['choices']) > 0:
                generated_text = result['choices'][0]['message']['content'].strip()
                
                print(f"\n✅ Generated Child Prompt:")
                print(f'"{generated_text}"')
                print(f'Length: {len(generated_text)} characters')
                
                # Calculate scores
                scores = crossover.calculate_performance_diversity_score(
                    generated_text, parent1_analysis, parent2_analysis, existing_prompts
                )
                
                print(f'\n📊 Scores:')
                print(f'Performance Score: {scores["performance_score"]:.3f}')
                print(f'Diversity Score: {scores["diversity_score"]:.3f}')
                print(f'Combined Score: {scores["combined_score"]:.3f}')
                
                # Analyze style
                child_style = crossover._analyze_style_characteristics(generated_text)
                print(f'Style: {child_style["dominant_tone"]} tone, {child_style["dominant_approach"]} approach')
                
            else:
                print("❌ No choices in response")
        else:
            print(f"❌ API Error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    # Run tests
    test_enhanced_crossover()
    test_with_llm()
