#!/usr/bin/env python3
"""
Test assessment consistency at different temperatures
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

async def test_temperature_consistency():
    """Test assessment consistency at different temperatures"""
    
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
    
    temperatures = [0.3, 0.2, 0.1]
    results = {}
    
    print("🧪 Testing Temperature Impact on Assessment Consistency")
    print("=" * 70)
    
    for temp in temperatures:
        print(f"\n🌡️  Testing Temperature: {temp}")
        print("-" * 40)
        
        # Create assessment system with specified temperature
        assessment_system = AssessmentSystem(use_weights=False, temperature=temp)
        
        # Run 5 assessments at this temperature (to save API quota)
        tasks = []
        for i in range(5):
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
        
        results[temp] = {
            "scores": scores,
            "total_scores": total_scores,
            "mean": mean_score,
            "std": std_score,
            "min": min_score,
            "max": max_score,
            "range": range_score,
            "consistency": consistency,
            "assessments": assessment_results
        }
    
    # Create comparison visualization
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
    
    # Plot 1: Score distributions for each temperature
    colors = ['skyblue', 'lightgreen', 'lightcoral']
    for i, temp in enumerate(temperatures):
        scores = results[temp]["scores"]
        ax1.hist(scores, bins=5, alpha=0.7, label=f'T={temp}', color=colors[i], edgecolor='black')
    
    ax1.set_xlabel('Average Score')
    ax1.set_ylabel('Frequency')
    ax1.set_title('Score Distributions by Temperature')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: Standard deviation comparison
    temps = list(results.keys())
    stds = [results[temp]["std"] for temp in temps]
    ax2.bar([str(t) for t in temps], stds, color=colors, alpha=0.7)
    ax2.set_xlabel('Temperature')
    ax2.set_ylabel('Standard Deviation')
    ax2.set_title('Consistency (Lower is Better)')
    ax2.grid(True, alpha=0.3)
    
    # Add std dev values on bars
    for i, std in enumerate(stds):
        ax2.text(i, std + 0.01, f'{std:.3f}', ha='center', va='bottom')
    
    # Plot 3: Score ranges
    ranges = [results[temp]["range"] for temp in temps]
    ax3.bar([str(t) for t in temps], ranges, color=colors, alpha=0.7)
    ax3.set_xlabel('Temperature')
    ax3.set_ylabel('Score Range')
    ax3.set_title('Variability (Lower is Better)')
    ax3.grid(True, alpha=0.3)
    
    # Add range values on bars
    for i, range_val in enumerate(ranges):
        ax3.text(i, range_val + 0.01, f'{range_val:.3f}', ha='center', va='bottom')
    
    # Plot 4: Individual assessment attempts
    for i, temp in enumerate(temperatures):
        scores = results[temp]["scores"]
        x_pos = np.arange(len(scores)) + i * 0.25
        ax4.bar(x_pos, scores, width=0.25, label=f'T={temp}', color=colors[i], alpha=0.7)
    
    ax4.set_xlabel('Assessment Attempt')
    ax4.set_ylabel('Average Score')
    ax4.set_title('Individual Assessment Scores')
    ax4.set_xticks(np.arange(5) + 0.25)
    ax4.set_xticklabels([f'{i+1}' for i in range(5)])
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('temperature_consistency_test.png', dpi=300, bbox_inches='tight')
    print(f"\n📊 Visualization saved as 'temperature_consistency_test.png'")
    
    # Save detailed results
    results_data = {
        "timestamp": datetime.now().isoformat(),
        "test_type": "temperature_consistency",
        "dummy_name": dummy.name,
        "dummy_id": dummy.id,
        "temperatures_tested": temperatures,
        "results": {}
    }
    
    for temp in temperatures:
        results_data["results"][str(temp)] = {
            "scores": [float(s) for s in results[temp]["scores"]],
            "total_scores": results[temp]["total_scores"],
            "statistics": {
                "mean": float(results[temp]["mean"]),
                "std": float(results[temp]["std"]),
                "min": float(results[temp]["min"]),
                "max": float(results[temp]["max"]),
                "range": float(results[temp]["range"]),
                "consistency": results[temp]["consistency"]
            }
        }
    
    with open('temperature_consistency_results.json', 'w') as f:
        json.dump(results_data, f, indent=2)
    
    print(f"📄 Detailed results saved as 'temperature_consistency_results.json'")
    
    # Print summary
    print(f"\n🎯 TEMPERATURE COMPARISON SUMMARY:")
    print("=" * 50)
    for temp in temperatures:
        result = results[temp]
        print(f"Temperature {temp}:")
        print(f"  Std Dev: {result['std']:.3f}")
        print(f"  Range:   {result['range']:.3f}")
        print(f"  Status:  {result['consistency']}")
        print()
    
    # Find best temperature
    best_temp = min(temperatures, key=lambda t: results[t]["std"])
    print(f"🏆 BEST TEMPERATURE: {best_temp}")
    print(f"   Standard Deviation: {results[best_temp]['std']:.3f}")
    print(f"   Consistency: {results[best_temp]['consistency']}")
    
    return results

if __name__ == "__main__":
    results = asyncio.run(test_temperature_consistency())
    
    # Check if we achieved good consistency
    best_temp = min(results.keys(), key=lambda t: results[t]["std"])
    best_std = results[best_temp]["std"]
    
    print(f"\n🎯 FINAL RECOMMENDATION:")
    if best_std < 0.1:
        print(f"✅ EXCELLENT: Temperature {best_temp} provides excellent consistency!")
        print("✅ Ready to proceed with conversation length experiments")
    elif best_std < 0.2:
        print(f"✅ GOOD: Temperature {best_temp} provides good consistency!")
        print("✅ Ready to proceed with conversation length experiments")
    elif best_std < 0.3:
        print(f"⚠️  MODERATE: Temperature {best_temp} provides moderate consistency")
        print("⚠️  Consider testing parallel question approach")
    else:
        print(f"❌ POOR: Even temperature {best_temp} has poor consistency")
        print("❌ Must implement parallel question approach")
