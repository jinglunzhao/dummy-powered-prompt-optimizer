#!/usr/bin/env python3
"""
Test the multi-turn conversation assessment approach
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from assessment_system import AssessmentSystem
from models import AIDummy, PersonalityProfile, SocialAnxietyProfile, Conversation

async def test_multiturn_assessment():
    """Test if multi-turn conversations enable human-like behavior"""
    
    # Create a test dummy with moderate personality
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
    
    print("🧪 Testing Multi-Turn Conversation Assessment")
    print("=" * 50)
    
    # Test 1: Pre-assessment (baseline)
    print("\n📝 Test 1: Pre-assessment (multi-turn baseline)")
    pre = await assessment_system.generate_pre_assessment(dummy)
    print(f"   Score: {pre.average_score:.2f}")
    
    # Test 2: Create a helpful coaching conversation
    print("\n📝 Test 2: Post-assessment after helpful coaching")
    conversation = Conversation(
        id="test-conv",
        dummy_id=dummy.id,
        scenario="Social skills coaching",
        system_prompt="You are a helpful peer mentor for college students. Be supportive and provide practical advice.",
        turns=[]
    )
    
    # Add a helpful coaching conversation
    conversation.add_turn("dummy", "I'm really nervous about asking for help from my professors. I feel like I'm bothering them.")
    conversation.add_turn("ai", "That's totally understandable! Professors actually appreciate when students ask thoughtful questions. It shows you're engaged and care about learning. Try starting with office hours - they're specifically meant for student questions.")
    conversation.add_turn("dummy", "I guess that makes sense. I never thought of office hours that way.")
    conversation.add_turn("ai", "Exactly! And remember, asking questions helps you learn better and shows initiative. Most professors find it encouraging when students are proactive about their education.")
    conversation.add_turn("dummy", "Thanks, that actually makes me feel more confident about reaching out.")
    conversation.add_turn("ai", "You're welcome! Start small - maybe ask one question in your next class. You'll see that professors are usually very supportive.")
    
    post = await assessment_system.generate_post_assessment(dummy, pre, conversation)
    print(f"   Score: {post.average_score:.2f}")
    print(f"   Improvement: {post.average_score - pre.average_score:.3f}")
    
    # Test 3: Check specific question changes
    print("\n📋 Test 3: Individual Question Analysis")
    help_question_idx = 0  # "I ask for help when I need it."
    pre_help_score = pre.responses[help_question_idx].score
    post_help_score = post.responses[help_question_idx].score
    print(f"   Help-seeking (Q1): {pre_help_score}/4 → {post_help_score}/4 (change: {post_help_score - pre_help_score})")
    
    calm_question_idx = 1  # "I stay calm when dealing with problems."
    pre_calm_score = pre.responses[calm_question_idx].score
    post_calm_score = post.responses[calm_question_idx].score
    print(f"   Calmness (Q2): {pre_calm_score}/4 → {post_calm_score}/4 (change: {post_calm_score - pre_calm_score})")
    
    # Test 4: Show some actual responses
    print("\n📝 Test 4: Sample Response Analysis")
    print("   Pre-assessment help-seeking response:")
    print(f"     {pre.responses[help_question_idx].notes[:100]}...")
    print("   Post-assessment help-seeking response:")
    print(f"     {post.responses[help_question_idx].notes[:100]}...")
    
    return {
        "pre_score": pre.average_score,
        "post_score": post.average_score,
        "improvement": post.average_score - pre.average_score,
        "help_seeking_change": post_help_score - pre_help_score,
        "calmness_change": post_calm_score - pre_calm_score
    }

if __name__ == "__main__":
    result = asyncio.run(test_multiturn_assessment())
    
    print("\n" + "=" * 50)
    print("🔍 MULTI-TURN ASSESSMENT ANALYSIS")
    print("=" * 50)
    
    print(f"Pre-assessment: {result['pre_score']:.2f}")
    print(f"Post-assessment: {result['post_score']:.2f}")
    print(f"Overall improvement: {result['improvement']:.3f}")
    print(f"Help-seeking improvement: {result['help_seeking_change']}")
    print(f"Calmness improvement: {result['calmness_change']}")
    
    print("\n🎯 ASSESSMENT:")
    if result['improvement'] > 0.1:
        print("✅ EXCELLENT: Multi-turn conversation achieved significant improvement")
    elif result['improvement'] > 0.05:
        print("✅ GOOD: Multi-turn conversation achieved moderate improvement")
    elif result['improvement'] > 0:
        print("✅ POSITIVE: Multi-turn conversation achieved some improvement")
    elif abs(result['improvement']) < 0.05:
        print("⚠️  MINIMAL: Little change from multi-turn conversation")
    else:
        print("❌ NEGATIVE: Multi-turn conversation had negative impact")
    
    if result['help_seeking_change'] > 0:
        print("✅ Help-seeking improved (conversation was specifically about asking for help)")
    elif result['help_seeking_change'] == 0:
        print("⚠️  Help-seeking unchanged (may need better conversation context)")
    else:
        print("❌ Help-seeking decreased (unexpected)")
    
    print("\n🎯 CONCLUSION:")
    if result['improvement'] > 0 and result['help_seeking_change'] > 0:
        print("   🎉 SUCCESS: Multi-turn conversations enable human-like behavior!")
        print("   The LLM now builds self-awareness through ongoing dialogue.")
    else:
        print("   🤔 Multi-turn approach needs refinement to achieve human-like improvement.")
