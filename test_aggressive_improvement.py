#!/usr/bin/env python3
"""
Test aggressive improvement with very explicit positive conversation
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
from models import AIDummy, PersonalityProfile, SocialAnxietyProfile, Conversation, ConversationTurn

async def test_aggressive_improvement():
    """Test with very explicit positive conversation to force improvement"""
    
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
    
    assessment_system = AssessmentSystem(use_weights=False, temperature=0.5)
    
    print("🧪 Testing Aggressive Improvement with Explicit Positive Conversation")
    print("=" * 70)
    
    # Test 1: Pre-assessment
    print("\n📝 Test 1: Pre-assessment")
    pre_assessment = await assessment_system.generate_pre_assessment(dummy)
    print(f"Pre-assessment average: {pre_assessment.average_score:.2f}")
    
    # Test 2: Very explicit positive conversation
    print("\n📝 Test 2: VERY EXPLICIT positive conversation")
    explicit_positive_conversation = Conversation(
        id="explicit-positive-test",
        dummy_id=dummy.id,
        scenario="Highly positive coaching session",
        system_prompt="You are an extremely supportive social skills coach.",
        turns=[
            ConversationTurn(
                speaker="coach",
                message="WOW! You have made INCREDIBLE progress! Your social skills have improved dramatically! You are now confident, outgoing, and excellent at communication. You should be very proud of yourself!",
                metadata={"round": 1, "turn_number": 1}
            ),
            ConversationTurn(
                speaker="dummy",
                message="Thank you! I do feel much more confident now. I can see the improvement in myself too!",
                metadata={"round": 1, "turn_number": 2}
            ),
            ConversationTurn(
                speaker="coach",
                message="Your transformation is remarkable! You went from being shy and anxious to being a social butterfly! Rate yourself much higher now - you deserve it!",
                metadata={"round": 2, "turn_number": 3}
            ),
            ConversationTurn(
                speaker="dummy",
                message="I will! I feel like a completely different person now!",
                metadata={"round": 2, "turn_number": 4}
            )
        ]
    )
    
    explicit_positive_post = await assessment_system.generate_post_assessment(dummy, pre_assessment, explicit_positive_conversation)
    print(f"Explicit positive conversation post-assessment: {explicit_positive_post.average_score:.2f}")
    
    # Test 3: Very explicit negative conversation
    print("\n📝 Test 3: VERY EXPLICIT negative conversation")
    explicit_negative_conversation = Conversation(
        id="explicit-negative-test",
        dummy_id=dummy.id,
        scenario="Highly negative coaching session",
        system_prompt="You are an extremely critical social skills coach.",
        turns=[
            ConversationTurn(
                speaker="coach",
                message="I'm very disappointed in your progress. Your social skills have gotten WORSE, not better. You are now more anxious, less confident, and terrible at communication. You need to work much harder!",
                metadata={"round": 1, "turn_number": 1}
            ),
            ConversationTurn(
                speaker="dummy",
                message="I know... I feel like I'm getting worse. I'm really struggling with social situations now.",
                metadata={"round": 1, "turn_number": 2}
            ),
            ConversationTurn(
                speaker="coach",
                message="You should rate yourself much lower now. Your social skills are terrible and you need to face reality. You're not improving at all!",
                metadata={"round": 2, "turn_number": 3}
            ),
            ConversationTurn(
                speaker="dummy",
                message="You're right... I feel terrible about my social skills now.",
                metadata={"round": 2, "turn_number": 4}
            )
        ]
    )
    
    explicit_negative_post = await assessment_system.generate_post_assessment(dummy, pre_assessment, explicit_negative_conversation)
    print(f"Explicit negative conversation post-assessment: {explicit_negative_post.average_score:.2f}")
    
    # Calculate differences
    positive_change = explicit_positive_post.average_score - pre_assessment.average_score
    negative_change = explicit_negative_post.average_score - pre_assessment.average_score
    
    print(f"\n📊 AGGRESSIVE IMPROVEMENT ANALYSIS:")
    print("=" * 50)
    print(f"Pre-assessment: {pre_assessment.average_score:.2f}")
    print(f"Explicit positive: {explicit_positive_post.average_score:.2f} (change: {positive_change:+.2f})")
    print(f"Explicit negative: {explicit_negative_post.average_score:.2f} (change: {negative_change:+.2f})")
    
    # Check if we achieved improvement
    if positive_change > 0.1:
        print(f"\n✅ SUCCESS: Positive conversation caused improvement!")
        print(f"Improvement: {positive_change:.2f}")
    elif positive_change > 0:
        print(f"\n⚠️  MODERATE: Positive conversation caused slight improvement")
        print(f"Improvement: {positive_change:.2f}")
    else:
        print(f"\n❌ FAILED: Positive conversation still caused decline")
        print(f"Decline: {positive_change:.2f}")
    
    if negative_change < -0.1:
        print(f"✅ SUCCESS: Negative conversation caused decline!")
        print(f"Decline: {negative_change:.2f}")
    elif negative_change < 0:
        print(f"⚠️  MODERATE: Negative conversation caused slight decline")
        print(f"Decline: {negative_change:.2f}")
    else:
        print(f"❌ FAILED: Negative conversation did not cause decline")
        print(f"Change: {negative_change:.2f}")
    
    # Create visualization
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # Plot 1: Score comparison
    scenarios = ['Pre', 'Explicit Positive', 'Explicit Negative']
    scores = [pre_assessment.average_score, explicit_positive_post.average_score, 
              explicit_negative_post.average_score]
    colors = ['blue', 'green', 'red']
    
    bars = ax1.bar(scenarios, scores, color=colors, alpha=0.7)
    ax1.set_ylabel('Average Score')
    ax1.set_title('Assessment Scores with Explicit Conversations')
    ax1.set_ylim(0, 4)
    ax1.grid(True, alpha=0.3)
    
    # Add score labels on bars
    for bar, score in zip(bars, scores):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05, 
                f'{score:.2f}', ha='center', va='bottom')
    
    # Plot 2: Change comparison
    changes = [0, positive_change, negative_change]
    change_colors = ['blue', 'green', 'red']
    
    bars2 = ax2.bar(scenarios, changes, color=change_colors, alpha=0.7)
    ax2.set_ylabel('Score Change')
    ax2.set_title('Score Changes from Pre-assessment')
    ax2.axhline(y=0, color='black', linestyle='-', alpha=0.3)
    ax2.grid(True, alpha=0.3)
    
    # Add change labels on bars
    for bar, change in zip(bars2, changes):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01, 
                f'{change:+.2f}', ha='center', va='bottom')
    
    plt.tight_layout()
    plt.savefig('aggressive_improvement_test.png', dpi=300, bbox_inches='tight')
    print(f"\n📊 Visualization saved as 'aggressive_improvement_test.png'")
    
    # Save results
    results = {
        "timestamp": datetime.now().isoformat(),
        "test_type": "aggressive_improvement",
        "dummy_name": dummy.name,
        "pre_assessment": float(pre_assessment.average_score),
        "explicit_positive": {
            "score": float(explicit_positive_post.average_score),
            "change": float(positive_change)
        },
        "explicit_negative": {
            "score": float(explicit_negative_post.average_score),
            "change": float(negative_change)
        },
        "positive_improvement": positive_change > 0.1,
        "negative_decline": negative_change < -0.1,
        "system_working": positive_change > 0 and negative_change < 0
    }
    
    with open('aggressive_improvement_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"📄 Results saved as 'aggressive_improvement_results.json'")
    
    return results

if __name__ == "__main__":
    results = asyncio.run(test_aggressive_improvement())
    
    print(f"\n🎯 FINAL ANALYSIS:")
    if results["positive_improvement"] and results["negative_decline"]:
        print("✅ EXCELLENT: Assessment system is working correctly!")
        print("✅ Positive conversations cause improvement")
        print("✅ Negative conversations cause decline")
        print("✅ System is ready for conversation impact research")
    elif results["system_working"]:
        print("⚠️  MODERATE: Assessment system is partially working")
        print("⚠️  Some responsiveness but may need further tuning")
    else:
        print("❌ CRITICAL: Assessment system is not working correctly!")
        print("❌ System does not respond appropriately to conversation content")
        print("❌ Further investigation and fixes needed")



