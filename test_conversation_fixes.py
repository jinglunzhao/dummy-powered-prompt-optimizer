#!/usr/bin/env python3
"""
Test script to verify the conversation truncation and partial testing fixes
Tests that conversations run longer and all dummies are tested
"""

import asyncio
import json
import os
import sys
from datetime import datetime

# Add the current directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from test_gepa_system import run_gepa_test

async def test_conversation_fixes():
    """Test the conversation truncation and partial testing fixes"""
    
    print("🔧 TESTING CONVERSATION TRUNCATION AND PARTIAL TESTING FIXES")
    print("=" * 70)
    print("🎯 Testing that conversations run longer and all dummies are tested")
    print("=" * 70)
    
    # Configuration for testing the fixes
    config = {
        "test_name": "Conversation Fixes Test",
        "dummies_count": 3,  # Small number for quick testing
        "conversation_rounds": 25,  # Full 25 rounds to test truncation fix
        "generations": 2,  # Few generations to focus on testing
        "population_size": 1,
        "mutation_rate": 0.3,
        "crossover_rate": 0.6,
        "use_real_api": True,
        "save_detailed_data": True,
        "output_file": "data/conversation_fixes_test_results.json",
        "optimal_ending_detection": True,
        "milestone_assessment": True,
        "conversation_quality_monitoring": True
    }
    
    print(f"📊 Test Configuration:")
    print(f"   • Dummies: {config['dummies_count']}")
    print(f"   • Rounds: {config['conversation_rounds']} (should NOT be truncated to 10 turns)")
    print(f"   • Generations: {config['generations']}")
    print(f"   • Expected: All prompts tested with ALL {config['dummies_count']} dummies")
    print("=" * 70)
    
    try:
        # Run the GEPA test with the fixes
        results = await run_gepa_test(config)
        
        print("\n🔍 ANALYZING RESULTS FOR CONVERSATION FIXES:")
        print("=" * 70)
        
        if results:
            optimization = results.get('optimization', {})
            all_prompts = optimization.get('all_prompts', [])
            optimization_history = optimization.get('optimization_history', [])
            conversations = results.get('conversations', [])
            
            print(f"📊 RESULTS ANALYSIS:")
            print(f"   • Total prompts generated: {len(all_prompts)}")
            print(f"   • Total optimization results: {len(optimization_history)}")
            print(f"   • Total conversations: {len(conversations)}")
            
            # Analyze conversation length
            print(f"\n🔍 CONVERSATION LENGTH ANALYSIS:")
            conversation_lengths = []
            for conv in conversations:
                turns = conv.get('turns', [])
                conversation_lengths.append(len(turns))
            
            if conversation_lengths:
                avg_length = sum(conversation_lengths) / len(conversation_lengths)
                min_length = min(conversation_lengths)
                max_length = max(conversation_lengths)
                
                print(f"   • Average conversation length: {avg_length:.1f} turns")
                print(f"   • Minimum conversation length: {min_length} turns")
                print(f"   • Maximum conversation length: {max_length} turns")
                
                # Check for truncation (conversations ending too early)
                truncated_conversations = sum(1 for length in conversation_lengths if length < 30)  # Less than 15 rounds
                print(f"   • Truncated conversations (< 30 turns): {truncated_conversations}/{len(conversation_lengths)}")
                
                if truncated_conversations == 0:
                    print(f"   ✅ CONVERSATION TRUNCATION FIX SUCCESSFUL!")
                else:
                    print(f"   ❌ CONVERSATION TRUNCATION ISSUE PERSISTS!")
            
            # Analyze prompt testing completeness
            print(f"\n🔍 PROMPT TESTING COMPLETENESS ANALYSIS:")
            expected_tests = config['dummies_count']
            
            for prompt in all_prompts:
                metrics = prompt.get('performance_metrics', {})
                test_count = metrics.get('test_count', 0)
                improvement = metrics.get('avg_improvement', 0)
                name = prompt.get('name', 'Unknown')
                
                if test_count == expected_tests:
                    print(f"   ✅ {name}: {test_count}/{expected_tests} tests, {improvement:+.3f} improvement")
                else:
                    print(f"   ❌ {name}: {test_count}/{expected_tests} tests, {improvement:+.3f} improvement")
            
            # Check optimization history for test distribution
            print(f"\n🔍 OPTIMIZATION HISTORY ANALYSIS:")
            if optimization_history:
                # Group by prompt to check test distribution
                prompt_tests = {}
                for result in optimization_history:
                    prompt_name = result.get('prompt_name', 'Unknown')
                    if prompt_name not in prompt_tests:
                        prompt_tests[prompt_name] = []
                    prompt_tests[prompt_name].append(result)
                
                for prompt_name, tests in prompt_tests.items():
                    if prompt_name != 'Unknown':
                        print(f"   • {prompt_name}: {len(tests)}/{expected_tests} tests")
            
            # Overall assessment
            print(f"\n📈 OVERALL ASSESSMENT:")
            
            # Check conversation truncation fix
            if conversation_lengths and min(conversation_lengths) >= 30:
                print(f"   ✅ Conversation truncation fix: SUCCESS")
            else:
                print(f"   ❌ Conversation truncation fix: FAILED")
            
            # Check partial testing fix
            all_prompts_tested_completely = all(
                prompt.get('performance_metrics', {}).get('test_count', 0) == expected_tests 
                for prompt in all_prompts
            )
            
            if all_prompts_tested_completely:
                print(f"   ✅ Partial testing fix: SUCCESS")
            else:
                print(f"   ❌ Partial testing fix: FAILED")
            
        else:
            print("❌ Test completed but no results returned")
            
    except Exception as e:
        print(f"❌ Error during conversation fixes test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print(f"🕐 Starting Conversation Fixes Test at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        asyncio.run(test_conversation_fixes())
    except KeyboardInterrupt:
        print("\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
    
    print(f"🕐 Test completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
