#!/usr/bin/env python3
"""
Quick GEPA Test with Personality Evolution

Runs a small GEPA experiment to populate the web interface with personality evolution data.
"""

import asyncio
import json
import os
from datetime import datetime
from typing import List
from prompt_optimizer import PromptOptimizer
from models import AIDummy, PersonalityProfile, SocialAnxietyProfile

async def run_quick_gepa_test():
    """Run a quick GEPA test to populate the web interface"""
    print("🚀 QUICK GEPA TEST WITH PERSONALITY EVOLUTION")
    print("=" * 60)
    
    # Initialize optimizer
    optimizer = PromptOptimizer()
    
    # Create test configuration
    test_config = {
        "dummies_count": 2,
        "conversation_rounds": 3,
        "generations": 2,
        "population_size": 3,
        "test_name": "Quick GEPA Test with Personality Evolution",
        "timestamp": datetime.now().isoformat()
    }
    
    print(f"📋 Test Config: {test_config['dummies_count']}d {test_config['conversation_rounds']}r {test_config['generations']}g")
    print()
    
    # Create test dummies
    dummies = []
    for i in range(test_config["dummies_count"]):
        dummy = AIDummy(
            name=f'QuickTestDummy{i+1}',
            age=19 + i,
            gender='female' if i % 2 == 0 else 'male',
            major='Computer Science',
            university='Test University',
            student_type='undergraduate',
            personality=PersonalityProfile(
                extraversion=3 + i,
                agreeableness=7,
                conscientiousness=6 + i,
                neuroticism=7 + i,
                openness=5
            ),
            social_anxiety=SocialAnxietyProfile(
                anxiety_level=7 + i,
                communication_style='hesitant',
                triggers=['large groups', 'presentations', 'new people'],
                social_comfort=3 - i
            ),
            fears=['being judged', 'saying wrong things', 'looking foolish'],
            challenges=['asking questions', 'joining discussions', 'making friends'],
            behaviors=['staying quiet', 'avoiding eye contact', 'sitting alone'],
            goals=['build confidence', 'participate more', 'make connections']
        )
        dummies.append(dummy)
        print(f"✅ Created dummy: {dummy.name} (anxiety: {dummy.social_anxiety.anxiety_level}/10)")
    
    print()
    
    # Set optimizer parameters
    optimizer.generations = test_config["generations"]
    optimizer.population_size = test_config["population_size"]
    optimizer.conversation_rounds = test_config["conversation_rounds"]
    
    # Run GEPA optimization
    try:
        print("🧬 Starting GEPA optimization with personality evolution...")
        result = await optimizer.run_optimization_async(dummies=dummies)
        
        print("✅ GEPA optimization completed!")
        print(f"📊 Best prompt: {result.name}")
        print(f"📊 Best improvement: {result.performance_metrics.get('avg_improvement', 0):.3f}")
        
        # Save results in the format expected by web interface
        experiment_data = {
            "test_config": test_config,
            "optimization": {
                "pareto_frontier": [optimizer._prompt_to_dict(p) for p in optimizer.pareto_frontier],
                "all_prompts": [optimizer._prompt_to_dict(p) for p in optimizer.population],
                "best_per_generation": optimizer.best_per_generation,
                "optimization_history": optimizer.optimization_history
            },
            "conversations": [],
            "assessments": [],
            "dummies": [dummy.model_dump() for dummy in dummies],
            "statistics": {
                "total_conversations": len(result.optimization_history),
                "total_assessments": len(result.optimization_history) * 2,  # pre + post
                "best_improvement": result.best_improvement,
                "average_improvement": sum(h.improvement for h in result.optimization_history) / len(result.optimization_history) if result.optimization_history else 0
            },
            "experiment_info": {
                "experiment_id": f"quick_gepa_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "personality_evolution_enabled": True,
                "completed_at": datetime.now().isoformat()
            }
        }
        
        # Save to the location expected by web interface
        os.makedirs('data', exist_ok=True)
        with open('data/real_api_test_results.json', 'w') as f:
            json.dump(experiment_data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Results saved to: data/real_api_test_results.json")
        print()
        print("🌐 Web interface should now display the experiment results!")
        print("   Visit: http://localhost:5000/optimization")
        print("   Or: http://localhost:5000/evolution")
        
        return result
        
    except Exception as e:
        print(f"❌ GEPA optimization failed: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    print("🧪 Quick GEPA Test with Personality Evolution")
    print("This will populate the web interface with experiment data")
    print()
    
    result = asyncio.run(run_quick_gepa_test())
    
    if result:
        print("\n🎉 Quick GEPA test completed successfully!")
        print("The web interface should now show experiment results.")
    else:
        print("\n❌ Quick GEPA test failed.")
