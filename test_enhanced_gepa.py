#!/usr/bin/env python3
"""
Test script for the Enhanced GEPA System
Demonstrates the new features:
- 25 rounds of conversation per test
- Optimal ending point detection
- Milestone-based personality evolution
- Enhanced genetic algorithm for system prompts
"""

import asyncio
import json
import os
import sys
from datetime import datetime

# Add the current directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from test_gepa_system import run_gepa_test

async def test_enhanced_gepa():
    """Test the enhanced GEPA system with optimal ending detection"""
    
    print("🚀 ENHANCED GEPA SYSTEM TEST")
    print("=" * 60)
    print("🎯 Testing new features:")
    print("   • 25 rounds of conversation per test")
    print("   • Optimal ending point detection")
    print("   • Conversation quality monitoring")
    print("   • Milestone-based personality evolution")
    print("   • Enhanced genetic algorithm")
    print("=" * 60)
    
    # Configuration for enhanced GEPA test
    config = {
        "test_name": "Enhanced GEPA Test",
        "dummies_count": 5,  # Small number for quick testing
        "conversation_rounds": 25,  # 25 rounds as requested
        "generations": 3,  # Fewer generations for testing
        "population_size": 1,
        "mutation_rate": 0.3,
        "crossover_rate": 0.6,
        "use_real_api": True,
        "save_detailed_data": True,
        "output_file": "data/enhanced_gepa_test_results.json",
        "optimal_ending_detection": True,
        "milestone_assessment": True,
        "conversation_quality_monitoring": True
    }
    
    print(f"📊 Test Configuration:")
    print(f"   • Dummies: {config['dummies_count']}")
    print(f"   • Rounds: {config['conversation_rounds']}")
    print(f"   • Generations: {config['generations']}")
    print(f"   • Optimal ending detection: {config['optimal_ending_detection']}")
    print(f"   • Milestone assessment: {config['milestone_assessment']}")
    print(f"   • Quality monitoring: {config['conversation_quality_monitoring']}")
    print("=" * 60)
    
    try:
        # Run the enhanced GEPA test
        results = await run_gepa_test(config)
        
        print("\n✅ ENHANCED GEPA TEST COMPLETED!")
        print("=" * 60)
        
        if results:
            stats = results.get('statistics', {})
            test_config = results.get('test_config', {})
            
            print(f"📊 Results Summary:")
            print(f"   • Total tests: {stats.get('total_tests', 0)}")
            print(f"   • Average improvement: +{stats.get('average_improvement', 0):.3f}")
            print(f"   • Pareto solutions: {stats.get('pareto_frontier_size', 0)}")
            print(f"   • Duration: {test_config.get('duration_seconds', 0):.1f}s")
            
            # Show best prompt if available
            optimization = results.get('optimization', {})
            pareto_frontier = optimization.get('pareto_frontier', [])
            
            if pareto_frontier:
                best_prompt = pareto_frontier[0]  # First in Pareto frontier
                print(f"\n🏆 Best System Prompt:")
                print(f"   • Name: {best_prompt.get('name', 'Unknown')}")
                print(f"   • Generation: {best_prompt.get('generation', 0)}")
                print(f"   • Improvement: +{best_prompt.get('performance_metrics', {}).get('avg_improvement', 0):.3f}")
                print(f"   • Text: {best_prompt.get('prompt_text', 'N/A')[:100]}...")
            
            print(f"\n💾 Results saved to: {config['output_file']}")
            
        else:
            print("❌ Test completed but no results returned")
            
    except Exception as e:
        print(f"❌ Error during enhanced GEPA test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print(f"🕐 Starting Enhanced GEPA Test at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        asyncio.run(test_enhanced_gepa())
    except KeyboardInterrupt:
        print("\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
    
    print(f"🕐 Test completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
