#!/usr/bin/env python3
"""
Debug script to test assessment system consistency
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from assessment_system import AssessmentSystem
from models import AIDummy, PersonalityProfile, SocialAnxietyProfile

async def test_assessment_consistency():
    """Test if the same dummy gives consistent assessments"""
    
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
    
    print("🧪 Testing Assessment System Consistency")
    print("=" * 50)
    
    # Test 1: Same dummy, same conditions (should be consistent)
    print("\n📝 Test 1: Pre-assessment (no conversation context)")
    pre1 = await assessment_system.generate_pre_assessment(dummy)
    print(f"   Score: {pre1.average_score:.2f}")
    
    pre2 = await assessment_system.generate_pre_assessment(dummy)
    print(f"   Score: {pre2.average_score:.2f}")
    
    print(f"   Difference: {abs(pre1.average_score - pre2.average_score):.3f}")
    
    # Test 2: Post-assessment with minimal conversation
    print("\n📝 Test 2: Post-assessment (minimal conversation)")
    from models import Conversation
    
    # Create a simple conversation
    conversation = Conversation(
        id="test-conv",
        dummy_id=dummy.id,
        scenario="Test scenario",
        system_prompt="Test prompt",
        turns=[]
    )
    conversation.add_turn("dummy", "Hi, I need help with my studies.")
    conversation.add_turn("ai", "I'd be happy to help! What specific area are you struggling with?")
    conversation.add_turn("dummy", "I'm having trouble with time management.")
    conversation.add_turn("ai", "Let's work on a study schedule together.")
    
    post1 = await assessment_system.generate_post_assessment(dummy, pre1, conversation)
    print(f"   Score: {post1.average_score:.2f}")
    print(f"   Improvement: {post1.average_score - pre1.average_score:.3f}")
    
    # Test 3: Another post-assessment with same conversation
    post2 = await assessment_system.generate_post_assessment(dummy, pre1, conversation)
    print(f"   Score: {post2.average_score:.2f}")
    print(f"   Improvement: {post2.average_score - pre1.average_score:.3f}")
    print(f"   Difference from post1: {abs(post1.average_score - post2.average_score):.3f}")
    
    # Test 4: Check if scores are realistic
    print("\n📊 Test 4: Score Analysis")
    print(f"   Pre-assessment range: {min(pre1.average_score, pre2.average_score):.2f} - {max(pre1.average_score, pre2.average_score):.2f}")
    print(f"   Post-assessment range: {min(post1.average_score, post2.average_score):.2f} - {max(post1.average_score, post2.average_score):.2f}")
    
    # Test 5: Check individual question responses
    print("\n📋 Test 5: Individual Question Analysis")
    print("   Pre-assessment responses:")
    for i, response in enumerate(pre1.responses[:5]):  # First 5 questions
        print(f"     {i+1}. {response.score}/4 - {response.question[:30]}...")
    
    print("   Post-assessment responses:")
    for i, response in enumerate(post1.responses[:5]):  # First 5 questions
        print(f"     {i+1}. {response.score}/4 - {response.question[:30]}...")
    
    return {
        "pre_consistency": abs(pre1.average_score - pre2.average_score),
        "post_consistency": abs(post1.average_score - post2.average_score),
        "improvement": post1.average_score - pre1.average_score,
        "pre_scores": [pre1.average_score, pre2.average_score],
        "post_scores": [post1.average_score, post2.average_score]
    }

if __name__ == "__main__":
    result = asyncio.run(test_assessment_consistency())
    
    print("\n" + "=" * 50)
    print("🔍 ASSESSMENT SYSTEM DIAGNOSIS")
    print("=" * 50)
    
    print(f"Pre-assessment consistency: {result['pre_consistency']:.3f}")
    print(f"Post-assessment consistency: {result['post_consistency']:.3f}")
    print(f"Improvement from conversation: {result['improvement']:.3f}")
    
    if result['pre_consistency'] > 0.1:
        print("❌ ISSUE: Pre-assessments are inconsistent (same dummy, same conditions)")
    
    if result['post_consistency'] > 0.1:
        print("❌ ISSUE: Post-assessments are inconsistent (same dummy, same conversation)")
    
    if abs(result['improvement']) < 0.05:
        print("⚠️  WARNING: Very small improvement from conversation (may be noise)")
    
    if result['improvement'] < -0.1:
        print("❌ ISSUE: Negative improvement (conversation made things worse)")
    
    print("\n🎯 RECOMMENDATION:")
    if result['pre_consistency'] > 0.1 or result['post_consistency'] > 0.1:
        print("   The assessment system has consistency issues. Consider:")
        print("   1. Reducing temperature in API calls")
        print("   2. Adding more specific instructions")
        print("   3. Implementing response validation")
    elif abs(result['improvement']) < 0.05:
        print("   The assessment system may be too noisy. Consider:")
        print("   1. Increasing conversation impact")
        print("   2. Better conversation summarization")
        print("   3. More specific assessment prompts")
    else:
        print("   Assessment system appears to be working correctly.")
