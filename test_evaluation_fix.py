#!/usr/bin/env python3
"""
Test script to verify the evaluation logic fix
Tests that all new prompts are properly evaluated
"""

import asyncio
import json
import os
import sys
from datetime import datetime

# Add the current directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from test_gepa_system import run_gepa_test

async def test_evaluation_fix():
    """Test the evaluation logic fix"""
    
    print("🔧 TESTING EVALUATION LOGIC FIX")
    print("=" * 60)
    print("🎯 Testing that all prompts are properly evaluated")
    print("=" * 60)
    
    # Configuration for testing the fix
    config = {
        "test_name": "Evaluation Logic Fix Test",
        "dummies_count": 2,  # Very small for quick testing
        "conversation_rounds": 5,  # Very few rounds for speed
        "generations": 3,  # Enough generations to test evaluation
        "population_size": 1,
        "mutation_rate": 0.3,
        "crossover_rate": 0.6,
        "use_real_api": True,
        "save_detailed_data": True,
        "output_file": "data/evaluation_fix_test_results.json",
        "optimal_ending_detection": True,
        "milestone_assessment": True,
        "conversation_quality_monitoring": True
    }
    
    print(f"📊 Test Configuration:")
    print(f"   • Dummies: {config['dummies_count']}")
    print(f"   • Rounds: {config['conversation_rounds']}")
    print(f"   • Generations: {config['generations']}")
    print(f"   • Expected: All prompts should be tested")
    print("=" * 60)
    
    try:
        # Run the GEPA test with the fix
        results = await run_gepa_test(config)
        
        print("\n🔍 ANALYZING RESULTS FOR EVALUATION FIX:")
        print("=" * 60)
        
        if results:
            optimization = results.get('optimization', {})
            all_prompts = optimization.get('all_prompts', [])
            optimization_history = optimization.get('optimization_history', [])
            
            print(f"📊 RESULTS ANALYSIS:")
            print(f"   • Total prompts generated: {len(all_prompts)}")
            print(f"   • Total optimization results: {len(optimization_history)}")
            
            # Analyze prompt testing
            tested_prompts = 0
            untested_prompts = 0
            zero_improvement_prompts = 0
            
            for i, prompt in enumerate(all_prompts):
                metrics = prompt.get('performance_metrics', {})
                test_count = metrics.get('test_count', 0)
                avg_improvement = metrics.get('avg_improvement', 0)
                
                if test_count > 0:
                    tested_prompts += 1
                    if avg_improvement == 0:
                        zero_improvement_prompts += 1
                else:
                    untested_prompts += 1
                    
                # Show details for first few prompts
                if i < 8:
                    print(f"   Prompt {i+1}: {prompt.get('name', 'Unknown')}")
                    print(f"      • Generation: {prompt.get('generation', 'Unknown')}")
                    print(f"      • Tests: {test_count}")
                    print(f"      • Improvement: {avg_improvement:+.3f}")
            
            print(f"\n📈 SUMMARY:")
            print(f"   • Prompts with tests: {tested_prompts}")
            print(f"   • Prompts with 0 tests: {untested_prompts}")
            print(f"   • Tested prompts with 0 improvement: {zero_improvement_prompts}")
            
            # Check if fix worked
            if untested_prompts == 0:
                print(f"\n✅ FIX SUCCESSFUL!")
                print(f"   • All {tested_prompts} prompts were tested")
                print(f"   • No untested prompts found")
                print(f"   • Evaluation logic fix is working correctly")
            else:
                print(f"\n❌ FIX FAILED!")
                print(f"   • {untested_prompts} prompts were not tested")
                print(f"   • Evaluation logic issue still exists")
                
            # Show optimization history
            if optimization_history:
                print(f"\n🔍 OPTIMIZATION HISTORY ANALYSIS:")
                successful_tests = sum(1 for r in optimization_history if r.get('improvement', 0) > 0)
                failed_tests = sum(1 for r in optimization_history if r.get('improvement', 0) == 0)
                print(f"   • Successful tests (improvement > 0): {successful_tests}")
                print(f"   • Failed tests (improvement = 0): {failed_tests}")
            
        else:
            print("❌ Test completed but no results returned")
            
    except Exception as e:
        print(f"❌ Error during evaluation fix test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print(f"🕐 Starting Evaluation Logic Fix Test at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        asyncio.run(test_evaluation_fix())
    except KeyboardInterrupt:
        print("\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
    
    print(f"🕐 Test completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
