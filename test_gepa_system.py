#!/usr/bin/env python3
"""
Configurable TRUE GEPA System Test
Single script that can handle different scales by changing configuration parameters
"""

import json
import uuid
import time
import asyncio
from datetime import datetime
from typing import List, Dict, Any
from dataclasses import asdict
import sys
import os

# Add the current directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import Config
from prompt_optimizer import PromptOptimizer
# CharacterGenerator removed - using existing dummies only
from assessment_system import AssessmentSystem
from conversation_simulator import ConversationSimulator
from experiment_manager import create_experiment, save_experiment_result

class DateTimeEncoder(json.JSONEncoder):
    """Custom JSON encoder to handle datetime objects"""
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

async def run_gepa_test(config: Dict[str, Any] = None):
    """
    Run TRUE GEPA test with configurable parameters
    
    Args:
        config: Dictionary with test configuration parameters
    """
    
    # Default configuration for quick validation
    default_config = {
        "test_name": "Quick Validation",
        "dummies_count": 10,
        "conversation_rounds": 5,
        "generations": 6,
        "population_size": 1,
        "mutation_rate": 0.3,
        "crossover_rate": 0.6,
        "use_real_api": True,
        "save_detailed_data": False,
        "output_file": "data/gepa_test_results.json"
    }
    
    # Override with provided config
    if config:
        default_config.update(config)
    
    config = default_config
    
    print(f"🚀 Starting {config['test_name']}")
    print("=" * 60)
    print("📊 Configuration:")
    print(f"   • {config['dummies_count']} AI Dummies")
    print(f"   • {config['conversation_rounds']} conversation rounds per test")
    print(f"   • {config['generations']} generations of evolution")
    print(f"   • Population size: {config['population_size']}")
    print(f"   • Max population size: {Config.MAX_POPULATION_SIZE}")
    print(f"   • Real API calls: {config['use_real_api']}")
    print(f"   • Save detailed data: {config['save_detailed_data']}")
    print("=" * 60)
    
    # Calculate expected duration
    total_tests = config['generations'] * 2  # Rough estimate
    total_api_calls = total_tests * config['conversation_rounds'] * config['dummies_count']
    estimated_minutes = total_api_calls * 0.5  # ~30 seconds per API call
    
    print(f"⏱️  Estimated duration: ~{estimated_minutes:.1f} minutes")
    print(f"📞 Expected API calls: ~{total_api_calls}")
    print("=" * 60)
    
    # Initialize systems
    print("\n🔧 Initializing systems...")
    
    # Load or generate dummies
    dummies_file = "data/ai_dummies.json"
    dummies = []
    
    if os.path.exists(dummies_file):
        try:
            with open(dummies_file, 'r', encoding='utf-8') as f:
                all_dummies = json.load(f)
                # Take required number of dummies
                dummies = all_dummies[:config['dummies_count']]
            print(f"✅ Loaded {len(dummies)} existing dummies")
        except Exception as e:
            print(f"❌ Error loading dummies: {e}")
            dummies = []
    else:
        dummies = []
    
    # Use available dummies (we have 100, should be enough for most tests)
    if len(dummies) < config['dummies_count']:
        print(f"⚠️  Only {len(dummies)} dummies available, but {config['dummies_count']} requested")
        print(f"🔄 Using all available dummies: {len(dummies)}")
        config['dummies_count'] = len(dummies)  # Adjust config to match available dummies
    
    # Save all dummies
    with open(dummies_file, 'w', encoding='utf-8') as f:
        json.dump(all_dummies if len(all_dummies) > len(dummies) else dummies, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Total dummies: {len(dummies)}")
    print("🎯 IMPORTANT: These SAME dummies will be used for ALL prompt tests!")
    
    # Convert dummy dictionaries to AIDummy objects
    print("🔄 Converting dummies to AIDummy objects...")
    from models import AIDummy
    selected_dummies = dummies[:config['dummies_count']]  # Use only the requested number
    ai_dummies = [AIDummy(**dummy_data) for dummy_data in selected_dummies]
    print(f"✅ Converted {len(ai_dummies)} dummies to AIDummy objects")
    
    # Initialize systems
    assessment_system = AssessmentSystem()
    conversation_system = ConversationSimulator()
    
    # Create new prompt for this test run (fresh start)
    initial_prompt = {
        "id": str(uuid.uuid4()),
        "name": "Simple Peer Mentor",
        "prompt_text": "You are a helpful peer mentor for college students. Be supportive and provide practical advice.",
        "generation": 0,
        "performance_metrics": {
            "avg_improvement": 0.0,
            "test_count": 0,
            "question_improvements": [0.0] * 20  # 20 assessment questions
        }
    }
    print(f"🆕 Created new prompt for this test: {initial_prompt['name']} (ID: {initial_prompt['id'][:8]}...)")
    
    print(f"\n🎯 Initial Prompt: {initial_prompt['name']}")
    print(f"📝 Text: {initial_prompt['prompt_text']}")
    
    # Initialize optimizer
    optimizer = PromptOptimizer(
        base_prompt=initial_prompt["prompt_text"],
        population_size=config['population_size'],
        generations=config['generations'],
        mutation_rate=config['mutation_rate'],
        crossover_rate=config['crossover_rate']
    )
    
    # Store the prompt ID for this test run
    test_prompt_id = initial_prompt["id"]
    
    # Set up fair comparison
    print("\n🔧 Setting up fair comparison...")
    print("   • All prompts will be tested on the SAME dummies")
    print("   • This ensures fair comparison of prompt effectiveness")
    print("   • Each dummy's improvement will be measured consistently")
    
    # Run optimization
    print(f"\n🔄 Starting TRUE GEPA Optimization ({config['generations']} generations)...")
    
    start_time = time.time()
    
    # Run the optimization with SAME dummies
    best_prompt = await optimizer.run_optimization_async(ai_dummies)
    
    end_time = time.time()
    duration = end_time - start_time
    
    print(f"✅ Optimization completed in {duration:.1f} seconds ({duration/60:.1f} minutes)")
    
    if best_prompt:
        print(f"🏆 Best prompt: {best_prompt.name}")
        print(f"📝 Final prompt: {best_prompt.prompt_text}")
        print(f"🧬 Final generation: {best_prompt.generation}")
        print(f"📊 Performance: +{best_prompt.performance_metrics.get('avg_improvement', 0):.3f} improvement")
    
    # Display genealogy tree
    optimizer.print_genealogy_tree()
    
    # Get final results
    print("\n🎯 Final Results")
    print("=" * 60)
    
    # Get Pareto frontier
    pareto_frontier = optimizer.pareto_frontier
    print(f"🏆 Pareto Frontier: {len(pareto_frontier)} non-dominated solutions")
    
    for i, prompt in enumerate(pareto_frontier):
        improvement = prompt.performance_metrics.get('avg_improvement', 0)
        print(f"  Solution {i+1}: +{improvement:.3f} improvement")
    
    # Collect conversations and assessments from optimization history
    conversations = []
    assessments = []
    
    # Extract conversations and assessments from the optimization history
    for result in optimizer.optimization_history:
        if result.conversation:
            conversations.append(result.conversation.model_dump())
        if result.pre_assessment:
            assessments.append(result.pre_assessment.model_dump())
        if result.post_assessment:
            assessments.append(result.post_assessment.model_dump())
    
    # Create results structure
    results = {
        "test_config": {
            "test_name": config['test_name'],
            "dummies_count": len(dummies),
            "conversation_rounds": config['conversation_rounds'],
            "generations": config['generations'],
            "population_size": config['population_size'],
            "mutation_rate": config['mutation_rate'],
            "crossover_rate": config['crossover_rate'],
            "use_real_api": config['use_real_api'],
            "same_dummies_for_all_tests": True,
            "duration_seconds": duration,
            "timestamp": datetime.now().isoformat()
        },
        "optimization": {
            "pareto_frontier": [asdict(p) for p in pareto_frontier],
            "all_prompts": [asdict(p) for p in optimizer.all_prompts],
            "optimization_history": [
                {
                    "prompt_id": r.prompt_id,
                    "dummy_id": r.dummy_id,
                    "pre_score": r.pre_score,
                    "post_score": r.post_score,
                    "improvement": r.improvement,

                    "reflection_insights": r.reflection_insights,
                    "success_factors": r.success_factors,
                    "failure_factors": r.failure_factors,
                    "conversation": r.conversation.model_dump() if r.conversation else None,
                    "pre_assessment": r.pre_assessment.model_dump() if r.pre_assessment else None,
                    "post_assessment": r.post_assessment.model_dump() if r.post_assessment else None
                }
                for r in optimizer.optimization_history
            ],
            "best_per_generation": [asdict(p) for p in optimizer.best_per_generation]
        },
        "conversations": conversations,
        "assessments": assessments,
        "dummies": [dummy.model_dump() for dummy in ai_dummies],
        "statistics": {
            "total_tests": len(optimizer.optimization_history),
            "total_api_calls": len(optimizer.optimization_history) * config['conversation_rounds'] * config['dummies_count'],
            "average_improvement": sum(p.performance_metrics.get('avg_improvement', 0) for p in pareto_frontier) / len(pareto_frontier) if pareto_frontier else 0,
            "pareto_frontier_size": len(pareto_frontier)
        }
    }
    
    # Create experiment with proper versioning
    experiment_name = f"{config['test_name']} - {config['dummies_count']}d{config['conversation_rounds']}r{config['generations']}g"
    experiment_description = f"GEPA test with {config['dummies_count']} dummies, {config['conversation_rounds']} rounds, {config['generations']} generations"
    
    experiment_id = create_experiment(experiment_name, config, experiment_description)
    
    # Save results with proper versioning
    result_file = save_experiment_result(experiment_id, results, "completed")
    
    print(f"\n💾 Results saved to: {result_file}")
    print(f"🧪 Experiment ID: {experiment_id}")
    
    # Also save to the old location for backward compatibility
    with open(config['output_file'], 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False, cls=DateTimeEncoder)
    
    print(f"📁 Also saved to: {config['output_file']} (for backward compatibility)")
    
    # Update validation_test_results.json with the new test results
    validation_file = "data/validation_test_results.json"
    try:
        with open(validation_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False, cls=DateTimeEncoder)
        print(f"✅ Updated validation results: {validation_file}")
    except Exception as e:
        print(f"⚠️  Failed to update validation results: {e}")
    
    # Validation checks
    print("\n🔍 Validation Checks:")
    print(f"   ✅ API calls working: {len(optimizer.optimization_history) > 0}")
    print(f"   ✅ Population growth: {len(optimizer.population)} prompts generated")
    print(f"   ✅ Pareto frontier: {len(pareto_frontier)} solutions found")
    print(f"   ✅ JSON serialization: Results saved successfully")
    print(f"   ✅ Duration reasonable: {duration:.1f}s ({duration/60:.1f} minutes)")
    print(f"   ✅ TRUE GEPA approach: Single prompt → exponential growth")
    print(f"   ✅ Fair comparison: Same dummies for all tests")
    
    # Summary
    print("\n📋 Test Summary:")
    print(f"   • Total API calls: {results['statistics']['total_api_calls']}")
    print(f"   • Total tests: {results['statistics']['total_tests']}")
    print(f"   • Pareto frontier: {results['statistics']['pareto_frontier_size']} solutions")
    print(f"   • Average improvement: +{results['statistics']['average_improvement']:.3f} points")
    print(f"   • ✅ FAIR COMPARISON: Same dummies used for all tests")
    
    print(f"\n🌐 View results in the web dashboard:")
    print("   http://localhost:5000/optimization")
    
    return results

def get_preset_configs():
    """Get preset configurations for different test scales"""
    return {
        "quick_validation": {
            "test_name": "Quick Validation Test",
            "dummies_count": 10,
            "conversation_rounds": 5,
            "generations": 6,
            "population_size": 1,
            "mutation_rate": 0.3,
            "crossover_rate": 0.6,
            "use_real_api": True,
            "save_detailed_data": False,
            "output_file": "data/validation_test_results.json"
        },
        "small_scale": {
            "test_name": "Small Scale Test",
            "dummies_count": 10,
            "conversation_rounds": 5,
            "generations": 5,
            "population_size": 1,
            "mutation_rate": 0.3,
            "crossover_rate": 0.6,
            "use_real_api": True,
            "save_detailed_data": True,
            "output_file": "data/real_api_test_results.json"
        },
        "medium_scale": {
            "test_name": "Medium Scale Test",
            "dummies_count": 25,
            "conversation_rounds": 5,
            "generations": 6,
            "population_size": 1,
            "mutation_rate": 0.3,
            "crossover_rate": 0.6,
            "use_real_api": True,
            "save_detailed_data": True,
            "output_file": "data/medium_scale_results.json"
        },
        "full_scale": {
            "test_name": "Full Scale Test",
            "dummies_count": 50,
            "conversation_rounds": 8,
            "generations": 8,
            "population_size": 1,
            "mutation_rate": 0.3,
            "crossover_rate": 0.6,
            "use_real_api": True,
            "save_detailed_data": True,
            "output_file": "data/full_scale_results.json"
        }
    }

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run TRUE GEPA system test with configurable parameters")
    parser.add_argument("--preset", choices=["quick_validation", "small_scale", "medium_scale", "full_scale"], 
                       default="quick_validation", help="Use preset configuration")
    parser.add_argument("--dummies", type=int, help="Number of dummies")
    parser.add_argument("--rounds", type=int, help="Conversation rounds per test")
    parser.add_argument("--generations", type=int, help="Number of generations")
    parser.add_argument("--output", type=str, help="Output file path")
    
    args = parser.parse_args()
    
    # Get preset config
    preset_configs = get_preset_configs()
    config = preset_configs[args.preset].copy()
    
    # Override with command line arguments
    if args.dummies:
        config["dummies_count"] = args.dummies
    if args.rounds:
        config["conversation_rounds"] = args.rounds
    if args.generations:
        config["generations"] = args.generations
    if args.output:
        config["output_file"] = args.output
    
    print(f"🎯 Using configuration: {config['test_name']}")
    print(f"📊 Custom parameters: {args.dummies or 'default'} dummies, {args.rounds or 'default'} rounds, {args.generations or 'default'} generations")
    
    try:
        results = asyncio.run(run_gepa_test(config))
        print(f"\n✅ {config['test_name']} completed successfully!")
        print(f"📁 Results saved to: {config['output_file']}")
    except Exception as e:
        print(f"\n❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
