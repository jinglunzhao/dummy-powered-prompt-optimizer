#!/usr/bin/env python3
"""
Test assessment consistency by having the same dummy take the assessment 10 times in parallel
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

async def test_assessment_consistency():
    """Test if the same dummy gets consistent assessment results"""
    
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
    
    assessment_system = AssessmentSystem(use_weights=False)
    
    print("🧪 Testing Assessment Consistency")
    print("=" * 60)
    print(f"Running 10 parallel assessments for {dummy.name}...")
    
    # Run 10 assessments in parallel
    tasks = []
    for i in range(10):
        task = assessment_system.generate_pre_assessment(dummy)
        tasks.append(task)
    
    # Wait for all assessments to complete
    results = await asyncio.gather(*tasks)
    
    # Extract scores
    scores = [result.average_score for result in results]
    total_scores = [result.total_score for result in results]
    
    print(f"\n📊 Assessment Results:")
    print(f"Average Scores: {[f'{s:.2f}' for s in scores]}")
    print(f"Total Scores: {total_scores}")
    
    # Calculate statistics
    mean_score = np.mean(scores)
    std_score = np.std(scores)
    min_score = np.min(scores)
    max_score = np.max(scores)
    range_score = max_score - min_score
    
    print(f"\n📈 Statistics:")
    print(f"Mean: {mean_score:.3f}")
    print(f"Standard Deviation: {std_score:.3f}")
    print(f"Min: {min_score:.3f}")
    print(f"Max: {max_score:.3f}")
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
    
    # Create visualizations
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # Plot 1: Score distribution
    ax1.bar(range(1, 11), scores, color='skyblue', alpha=0.7)
    ax1.axhline(y=mean_score, color='red', linestyle='--', label=f'Mean: {mean_score:.3f}')
    ax1.set_xlabel('Assessment Attempt')
    ax1.set_ylabel('Average Score')
    ax1.set_title(f'Assessment Consistency Test - {dummy.name}')
    ax1.set_ylim(0, 4)
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Add score labels on bars
    for i, score in enumerate(scores):
        ax1.text(i+1, score + 0.05, f'{score:.2f}', ha='center', va='bottom')
    
    # Plot 2: Score distribution histogram
    ax2.hist(scores, bins=8, alpha=0.7, color='lightgreen', edgecolor='black')
    ax2.axvline(x=mean_score, color='red', linestyle='--', label=f'Mean: {mean_score:.3f}')
    ax2.set_xlabel('Average Score')
    ax2.set_ylabel('Frequency')
    ax2.set_title('Score Distribution')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('assessment_consistency_test.png', dpi=300, bbox_inches='tight')
    print(f"\n📊 Visualization saved as 'assessment_consistency_test.png'")
    
    # Save detailed results
    results_data = {
        "timestamp": datetime.now().isoformat(),
        "dummy_name": dummy.name,
        "dummy_id": dummy.id,
        "personality": {
            "extraversion": dummy.personality.extraversion,
            "agreeableness": dummy.personality.agreeableness,
            "conscientiousness": dummy.personality.conscientiousness,
            "neuroticism": dummy.personality.neuroticism,
            "openness": dummy.personality.openness
        },
        "anxiety": {
            "anxiety_level": dummy.social_anxiety.anxiety_level,
            "communication_style": dummy.social_anxiety.communication_style
        },
        "assessments": [
            {
                "attempt": i+1,
                "average_score": float(result.average_score),
                "total_score": result.total_score,
                "responses": [
                    {
                        "question": resp.question,
                        "score": resp.score,
                        "confidence": resp.confidence
                    }
                    for resp in result.responses
                ]
            }
            for i, result in enumerate(results)
        ],
        "statistics": {
            "mean": float(mean_score),
            "std": float(std_score),
            "min": float(min_score),
            "max": float(max_score),
            "range": float(range_score),
            "consistency": consistency
        }
    }
    
    with open('assessment_consistency_results.json', 'w') as f:
        json.dump(results_data, f, indent=2)
    
    print(f"📄 Detailed results saved as 'assessment_consistency_results.json'")
    
    return {
        "scores": scores,
        "mean": mean_score,
        "std": std_score,
        "range": range_score,
        "consistency": consistency
    }

if __name__ == "__main__":
    result = asyncio.run(test_assessment_consistency())
    
    print(f"\n🎯 FINAL RESULTS:")
    print(f"Consistency: {result['consistency']}")
    print(f"Standard Deviation: {result['std']:.3f}")
    print(f"Score Range: {result['range']:.3f}")
    
    if result['std'] > 0.3:
        print("\n⚠️  WARNING: High variability detected!")
        print("The assessment system shows significant inconsistency.")
        print("This could explain the disappointing experiment results.")
    elif result['std'] > 0.2:
        print("\n⚠️  CAUTION: Moderate variability detected.")
        print("The assessment system shows some inconsistency.")
    else:
        print("\n✅ Assessment system shows good consistency.")
