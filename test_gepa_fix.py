#!/usr/bin/env python3
"""
Test script to verify the GEPA population capping fix
Tests that all new prompts are properly evaluated before capping
"""

import asyncio
import json
import os
import sys
from datetime import datetime

# Add the current directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from test_gepa_system import run_gepa_test

async def test_gepa_fix():
    """Test the GEPA population capping fix"""
    
    print("🔧 TESTING GEPA POPULATION CAPPING FIX")
    print("=" * 60)
    print("🎯 Testing that all new prompts are evaluated before capping")
    print("=" * 60)
    
    # Configuration for testing the fix
    config = {
        "test_name": "GEPA Population Capping Fix Test",
        "dummies_count": 3,  # Small number for quick testing
        "conversation_rounds": 10,  # Fewer rounds for speed
        "generations": 4,  # Enough generations to test capping
        "population_size": 1,
        "mutation_rate": 0.3,
        "crossover_rate": 0.6,
        "use_real_api": True,
        "save_detailed_data": True,
        "output_file": "data/gepa_fix_test_results.json",
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
        
        print("\n🔍 ANALYZING RESULTS FOR POPULATION CAPPING FIX:")
        print("=" * 60)
        
        if results:
            optimization = results.get('optimization', {})
            all_prompts = optimization.get('all_prompts', [])
            
            print(f"📊 RESULTS ANALYSIS:")
            print(f"   • Total prompts generated: {len(all_prompts)}")
            
            # Analyze prompt testing
            tested_prompts = 0
            untested_prompts = 0
            
            for i, prompt in enumerate(all_prompts):
                metrics = prompt.get('performance_metrics', {})
                test_count = metrics.get('test_count', 0)
                
                if test_count > 0:
                    tested_prompts += 1
                else:
                    untested_prompts += 1
                    
                # Show details for first few prompts
                if i < 10:
                    improvement = metrics.get('avg_improvement', 0)
                    print(f"   Prompt {i+1}: {prompt.get('name', 'Unknown')}")
                    print(f"      • Generation: {prompt.get('generation', 'Unknown')}")
                    print(f"      • Tests: {test_count}")
                    print(f"      • Improvement: {improvement:+.3f}")
            
            print(f"\n📈 SUMMARY:")
            print(f"   • Prompts with tests: {tested_prompts}")
            print(f"   • Prompts with 0 tests: {untested_prompts}")
            
            # Check if fix worked
            if untested_prompts == 0:
                print(f"\n✅ FIX SUCCESSFUL!")
                print(f"   • All {tested_prompts} prompts were tested")
                print(f"   • No untested prompts found")
                print(f"   • Population capping fix is working correctly")
            else:
                print(f"\n❌ FIX FAILED!")
                print(f"   • {untested_prompts} prompts were not tested")
                print(f"   • Population capping issue still exists")
                
            # Show best prompt
            pareto_frontier = optimization.get('pareto_frontier', [])
            if pareto_frontier:
                best_prompt = pareto_frontier[0]
                print(f"\n🏆 Best System Prompt:")
                print(f"   • Name: {best_prompt.get('name', 'Unknown')}")
                print(f"   • Improvement: +{best_prompt.get('performance_metrics', {}).get('avg_improvement', 0):.3f}")
                print(f"   • Text: {best_prompt.get('prompt_text', 'N/A')[:100]}...")
            
        else:
            print("❌ Test completed but no results returned")
            
    except Exception as e:
        print(f"❌ Error during GEPA fix test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print(f"🕐 Starting GEPA Population Capping Fix Test at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        asyncio.run(test_gepa_fix())
    except KeyboardInterrupt:
        print("\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
    
    print(f"🕐 Test completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
