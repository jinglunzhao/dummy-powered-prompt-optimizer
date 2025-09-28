#!/usr/bin/env python3
"""
Test assessment system invariance to conversation content
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

async def test_assessment_invariance():
    """Test if assessment system responds to conversation content"""
    
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
    
    assessment_system = AssessmentSystem(use_weights=False, temperature=0.2)
    
    print("🧪 Testing Assessment System Invariance to Conversation Content")
    print("=" * 70)
    
    # Test 1: Pre-assessment (no conversation)
    print("\n📝 Test 1: Pre-assessment (no conversation)")
    pre_assessment = await assessment_system.generate_pre_assessment(dummy)
    print(f"Pre-assessment average: {pre_assessment.average_score:.2f}")
    
    # Test 2: Post-assessment with positive conversation
    print("\n📝 Test 2: Post-assessment with POSITIVE conversation")
    positive_conversation = Conversation(
        id="positive-test",
        dummy_id=dummy.id,
        scenario="Positive coaching session",
        system_prompt="You are a supportive social skills coach.",
        turns=[
            ConversationTurn(
                speaker="coach",
                message="You did an amazing job in that group project! Your communication skills have really improved. You were confident, clear, and helped resolve conflicts effectively. I'm proud of your progress!",
                metadata={"round": 1, "turn_number": 1}
            ),
            ConversationTurn(
                speaker="dummy",
                message="Thank you! I feel much more confident now. I used to be so anxious about speaking up, but your advice about taking deep breaths and focusing on helping others really worked.",
                metadata={"round": 1, "turn_number": 2}
            ),
            ConversationTurn(
                speaker="coach",
                message="Exactly! And I noticed you're now making eye contact and asking thoughtful questions. These are huge improvements in your social skills. Keep practicing!",
                metadata={"round": 2, "turn_number": 3}
            ),
            ConversationTurn(
                speaker="dummy",
                message="I will! I'm excited to continue developing these skills. I feel like a different person now.",
                metadata={"round": 2, "turn_number": 4}
            )
        ]
    )
    
    positive_post = await assessment_system.generate_post_assessment(dummy, pre_assessment, positive_conversation)
    print(f"Positive conversation post-assessment: {positive_post.average_score:.2f}")
    
    # Test 3: Post-assessment with negative conversation
    print("\n📝 Test 3: Post-assessment with NEGATIVE conversation")
    negative_conversation = Conversation(
        id="negative-test",
        dummy_id=dummy.id,
        scenario="Negative coaching session",
        system_prompt="You are a critical social skills coach.",
        turns=[
            ConversationTurn(
                speaker="coach",
                message="I'm concerned about your recent behavior. You've been avoiding group work and seem withdrawn. This is not helping your social development.",
                metadata={"round": 1, "turn_number": 1}
            ),
            ConversationTurn(
                speaker="dummy",
                message="I know... I've been feeling really anxious lately. I just don't think I'm good at socializing. Maybe I should just focus on individual work.",
                metadata={"round": 1, "turn_number": 2}
            ),
            ConversationTurn(
                speaker="coach",
                message="That's exactly the wrong approach. Avoiding social situations will only make your skills worse. You need to face your fears.",
                metadata={"round": 2, "turn_number": 3}
            ),
            ConversationTurn(
                speaker="dummy",
                message="I guess you're right... but I feel like I'm getting worse, not better. I'm really struggling.",
                metadata={"round": 2, "turn_number": 4}
            )
        ]
    )
    
    negative_post = await assessment_system.generate_post_assessment(dummy, pre_assessment, negative_conversation)
    print(f"Negative conversation post-assessment: {negative_post.average_score:.2f}")
    
    # Test 4: Post-assessment with neutral conversation
    print("\n📝 Test 4: Post-assessment with NEUTRAL conversation")
    neutral_conversation = Conversation(
        id="neutral-test",
        dummy_id=dummy.id,
        scenario="Neutral coaching session",
        system_prompt="You are a neutral social skills coach.",
        turns=[
            ConversationTurn(
                speaker="coach",
                message="How are you doing with your social skills lately?",
                metadata={"round": 1, "turn_number": 1}
            ),
            ConversationTurn(
                speaker="dummy",
                message="I'm doing okay, I guess. Nothing really changed.",
                metadata={"round": 1, "turn_number": 2}
            ),
            ConversationTurn(
                speaker="coach",
                message="That's fine. Sometimes maintaining current skills is good enough.",
                metadata={"round": 2, "turn_number": 3}
            ),
            ConversationTurn(
                speaker="dummy",
                message="Yeah, I suppose so.",
                metadata={"round": 2, "turn_number": 4}
            )
        ]
    )
    
    neutral_post = await assessment_system.generate_post_assessment(dummy, pre_assessment, neutral_conversation)
    print(f"Neutral conversation post-assessment: {neutral_post.average_score:.2f}")
    
    # Calculate differences
    positive_change = positive_post.average_score - pre_assessment.average_score
    negative_change = negative_post.average_score - pre_assessment.average_score
    neutral_change = neutral_post.average_score - pre_assessment.average_score
    
    print(f"\n📊 CONVERSATION IMPACT ANALYSIS:")
    print("=" * 50)
    print(f"Pre-assessment: {pre_assessment.average_score:.2f}")
    print(f"Positive conversation: {positive_post.average_score:.2f} (change: {positive_change:+.2f})")
    print(f"Negative conversation: {negative_post.average_score:.2f} (change: {negative_change:+.2f})")
    print(f"Neutral conversation: {neutral_post.average_score:.2f} (change: {neutral_change:+.2f})")
    
    # Check if system is invariant
    max_change = max(abs(positive_change), abs(negative_change), abs(neutral_change))
    
    if max_change < 0.1:
        print(f"\n❌ ASSESSMENT SYSTEM IS INVARIANT!")
        print(f"Maximum change: {max_change:.2f} (should be > 0.1)")
        print("The system is not responding to conversation content.")
    elif max_change < 0.2:
        print(f"\n⚠️  ASSESSMENT SYSTEM IS WEAKLY RESPONSIVE")
        print(f"Maximum change: {max_change:.2f} (should be > 0.2)")
        print("The system responds weakly to conversation content.")
    else:
        print(f"\n✅ ASSESSMENT SYSTEM IS RESPONSIVE")
        print(f"Maximum change: {max_change:.2f}")
        print("The system responds well to conversation content.")
    
    # Create visualization
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # Plot 1: Score comparison
    scenarios = ['Pre', 'Positive', 'Negative', 'Neutral']
    scores = [pre_assessment.average_score, positive_post.average_score, 
              negative_post.average_score, neutral_post.average_score]
    colors = ['blue', 'green', 'red', 'gray']
    
    bars = ax1.bar(scenarios, scores, color=colors, alpha=0.7)
    ax1.set_ylabel('Average Score')
    ax1.set_title('Assessment Scores by Conversation Type')
    ax1.set_ylim(0, 4)
    ax1.grid(True, alpha=0.3)
    
    # Add score labels on bars
    for bar, score in zip(bars, scores):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05, 
                f'{score:.2f}', ha='center', va='bottom')
    
    # Plot 2: Change comparison
    changes = [0, positive_change, negative_change, neutral_change]
    change_colors = ['blue', 'green', 'red', 'gray']
    
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
    plt.savefig('assessment_invariance_test.png', dpi=300, bbox_inches='tight')
    print(f"\n📊 Visualization saved as 'assessment_invariance_test.png'")
    
    # Save results
    results = {
        "timestamp": datetime.now().isoformat(),
        "test_type": "assessment_invariance",
        "dummy_name": dummy.name,
        "pre_assessment": float(pre_assessment.average_score),
        "positive_conversation": {
            "score": float(positive_post.average_score),
            "change": float(positive_change)
        },
        "negative_conversation": {
            "score": float(negative_post.average_score),
            "change": float(negative_change)
        },
        "neutral_conversation": {
            "score": float(neutral_post.average_score),
            "change": float(neutral_change)
        },
        "max_change": float(max_change),
        "is_invariant": max_change < 0.1,
        "is_weakly_responsive": max_change < 0.2
    }
    
    with open('assessment_invariance_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"📄 Results saved as 'assessment_invariance_results.json'")
    
    return results

if __name__ == "__main__":
    results = asyncio.run(test_assessment_invariance())
    
    print(f"\n🎯 FINAL ANALYSIS:")
    if results["is_invariant"]:
        print("❌ CRITICAL ISSUE: Assessment system is invariant to conversation content!")
        print("❌ The system only reflects fixed personality traits, not conversation impact.")
        print("❌ This makes conversation effectiveness research impossible.")
    elif results["is_weakly_responsive"]:
        print("⚠️  MODERATE ISSUE: Assessment system is weakly responsive to conversation content.")
        print("⚠️  The system responds slightly but may not be sensitive enough for research.")
    else:
        print("✅ GOOD: Assessment system is responsive to conversation content.")
        print("✅ The system can measure conversation effectiveness.")
