#!/usr/bin/env python3
"""
Test parallel vs single API call assessment approaches for consistency
"""

import asyncio
import sys
import os
import json
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from assessment_system import AssessmentSystem
from models import AIDummy, PersonalityProfile, SocialAnxietyProfile

async def test_assessment_approaches():
    """Compare parallel vs single API call assessment approaches"""
    
    # Create a test dummy
    personality = PersonalityProfile(
        extraversion=5, agreeableness=5, conscientiousness=5,
        neuroticism=5, openness=5
    )
    
    anxiety = SocialAnxietyProfile(
        anxiety_level=5, communication_style="Balanced",
        triggers=["Public speaking"], social_comfort=5
    )
    
    dummy = AIDummy(
        id="test-dummy",
        name="Test Dummy",
        age=20,
        gender="Non-binary",
        university="Test University",
        student_type="Undergraduate",
        major="Computer Science",
        personality=personality,
        social_anxiety=anxiety,
        fears=["Academic failure"],
        goals=["Graduate with honors"],
        challenges=["Time management"],
        behaviors=["Studies regularly"]
    )
    
    approaches = ["single", "parallel"]
    results = {}
    
    print("🧪 Testing Parallel vs Single API Call Assessment Approaches")
    print("=" * 70)
    
    for approach in approaches:
        print(f"\n🔧 Testing Approach: {approach.upper()}")
        print("-" * 40)
        
        # Create assessment system
        assessment_system = AssessmentSystem(use_weights=False, temperature=0.2)  # Use best temperature from previous test
        
        # Run 3 assessments with this approach (to save API quota)
        tasks = []
        for i in range(3):
            if approach == "parallel":
                task = assessment_system._ask_dummy_parallel_assessment_questions(dummy)
            else:
                task = assessment_system.generate_pre_assessment(dummy)
            tasks.append(task)
        
        # Wait for all assessments to complete
        assessment_results = await asyncio.gather(*tasks)
        
        # Extract scores
        scores = [result.average_score for result in assessment_results]
        total_scores = [result.total_score for result in assessment_results]
        
        print(f"Average Scores: {[f'{s:.2f}' for s in scores]}")
        print(f"Total Scores: {total_scores}")
        
        # Calculate statistics
        mean_score = np.mean(scores)
        std_score = np.std(scores)
        min_score = np.min(scores)
        max_score = np.max(scores)
        range_score = max_score - min_score
        
        print(f"Mean: {mean_score:.3f}")
        print(f"Std Dev: {std_score:.3f}")
        print(f"Range: {range_score:.3f}")
        
        # Check consistency
        if std_score < 0.1:
            consistency = "✅ EXCELLENT"
        elif std_score < 0.2:
            consistency = "✅ GOOD"
        elif std_score < 0.3:
            consistency = "⚠️  MODERATE"
        else:
            consistency = "❌ POOR"
        
        print(f"Consistency: {consistency}")
        
        # Calculate API calls used
        api_calls = 3 if approach == "single" else 3 * 20  # 20 questions per assessment for parallel
        
        results[approach] = {
            "scores": scores,
            "total_scores": total_scores,
            "mean": mean_score,
            "std": std_score,
            "min": min_score,
            "max": max_score,
            "range": range_score,
            "consistency": consistency,
            "api_calls": api_calls,
            "assessments": assessment_results
        }
    
    # Create comparison visualization
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
    
    # Plot 1: Score distributions
    colors = ['skyblue', 'lightgreen']
    for i, approach in enumerate(approaches):
        scores = results[approach]["scores"]
        ax1.hist(scores, bins=3, alpha=0.7, label=f'{approach.title()} API', color=colors[i], edgecolor='black')
    
    ax1.set_xlabel('Average Score')
    ax1.set_ylabel('Frequency')
    ax1.set_title('Score Distributions by Approach')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: Standard deviation comparison
    approaches_list = list(results.keys())
    stds = [results[approach]["std"] for approach in approaches_list]
    ax2.bar([approach.title() for approach in approaches_list], stds, color=colors, alpha=0.7)
    ax2.set_xlabel('Assessment Approach')
    ax2.set_ylabel('Standard Deviation')
    ax2.set_title('Consistency Comparison (Lower is Better)')
    ax2.grid(True, alpha=0.3)
    
    # Add std dev values on bars
    for i, std in enumerate(stds):
        ax2.text(i, std + 0.01, f'{std:.3f}', ha='center', va='bottom')
    
    # Plot 3: Score ranges
    ranges = [results[approach]["range"] for approach in approaches_list]
    ax3.bar([approach.title() for approach in approaches_list], ranges, color=colors, alpha=0.7)
    ax3.set_xlabel('Assessment Approach')
    ax3.set_ylabel('Score Range')
    ax3.set_title('Variability Comparison (Lower is Better)')
    ax3.grid(True, alpha=0.3)
    
    # Add range values on bars
    for i, range_val in enumerate(ranges):
        ax3.text(i, range_val + 0.01, f'{range_val:.3f}', ha='center', va='bottom')
    
    # Plot 4: API calls vs consistency
    api_calls = [results[approach]["api_calls"] for approach in approaches_list]
    ax4.bar([approach.title() for approach in approaches_list], api_calls, color=colors, alpha=0.7)
    ax4.set_xlabel('Assessment Approach')
    ax4.set_ylabel('API Calls Used')
    ax4.set_title('API Call Usage')
    ax4.grid(True, alpha=0.3)
    
    # Add API call values on bars
    for i, calls in enumerate(api_calls):
        ax4.text(i, calls + 1, f'{calls}', ha='center', va='bottom')
    
    plt.tight_layout()
    plt.savefig('parallel_vs_single_assessment_test.png', dpi=300, bbox_inches='tight')
    print(f"\n📊 Visualization saved as 'parallel_vs_single_assessment_test.png'")
    
    # Save detailed results
    results_data = {
        "timestamp": datetime.now().isoformat(),
        "test_type": "parallel_vs_single_assessment",
        "dummy_name": dummy.name,
        "dummy_id": dummy.id,
        "approaches_tested": approaches,
        "results": {}
    }
    
    for approach in approaches:
        results_data["results"][approach] = {
            "scores": [float(s) for s in results[approach]["scores"]],
            "total_scores": results[approach]["total_scores"],
            "statistics": {
                "mean": float(results[approach]["mean"]),
                "std": float(results[approach]["std"]),
                "min": float(results[approach]["min"]),
                "max": float(results[approach]["max"]),
                "range": float(results[approach]["range"]),
                "consistency": results[approach]["consistency"],
                "api_calls": results[approach]["api_calls"]
            }
        }
    
    with open('parallel_vs_single_assessment_results.json', 'w') as f:
        json.dump(results_data, f, indent=2)
    
    print(f"📄 Detailed results saved as 'parallel_vs_single_assessment_results.json'")
    
    # Print summary
    print(f"\n🎯 APPROACH COMPARISON SUMMARY:")
    print("=" * 50)
    for approach in approaches:
        result = results[approach]
        print(f"{approach.title()} API:")
        print(f"  Std Dev: {result['std']:.3f}")
        print(f"  Range:   {result['range']:.3f}")
        print(f"  Status:  {result['consistency']}")
        print(f"  API Calls: {result['api_calls']}")
        print()
    
    # Find best approach
    best_approach = min(approaches, key=lambda a: results[a]["std"])
    print(f"🏆 BEST APPROACH: {best_approach.title()}")
    print(f"   Standard Deviation: {results[best_approach]['std']:.3f}")
    print(f"   Consistency: {results[best_approach]['consistency']}")
    print(f"   API Calls: {results[best_approach]['api_calls']}")
    
    # Calculate improvement
    single_std = results["single"]["std"]
    parallel_std = results["parallel"]["std"]
    improvement = ((single_std - parallel_std) / single_std) * 100
    
    print(f"\n📈 IMPROVEMENT ANALYSIS:")
    print(f"Single API std dev: {single_std:.3f}")
    print(f"Parallel API std dev: {parallel_std:.3f}")
    print(f"Improvement: {improvement:.1f}%")
    
    return results

if __name__ == "__main__":
    results = asyncio.run(test_assessment_approaches())
    
    # Final recommendation
    single_std = results["single"]["std"]
    parallel_std = results["parallel"]["std"]
    
    print(f"\n🎯 FINAL RECOMMENDATION:")
    if parallel_std < 0.1:
        print(f"✅ EXCELLENT: Parallel approach provides excellent consistency!")
        print("✅ RECOMMEND: Use parallel approach for all assessments")
        print("✅ Ready to proceed with conversation length experiments")
    elif parallel_std < 0.2:
        print(f"✅ GOOD: Parallel approach provides good consistency!")
        print("✅ RECOMMEND: Use parallel approach for all assessments")
        print("✅ Ready to proceed with conversation length experiments")
    elif parallel_std < single_std:
        print(f"⚠️  IMPROVED: Parallel approach is better than single API")
        print(f"⚠️  Improvement: {((single_std - parallel_std) / single_std) * 100:.1f}%")
        print("⚠️  Consider: Use parallel approach despite higher API usage")
    else:
        print(f"❌ NO IMPROVEMENT: Parallel approach not better than single API")
        print("❌ Consider: Stick with single API approach")
        print("❌ Need: Further investigation required")
