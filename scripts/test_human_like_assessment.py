#!/usr/bin/env python3
"""
Test the more human-like assessment approach
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from assessment_system import AssessmentSystem
from models import AIDummy, PersonalityProfile, SocialAnxietyProfile, Conversation

async def test_human_like_assessment():
    """Test if the assessment system now behaves more like a human"""
    
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
    
    print("🧪 Testing Human-Like Assessment System")
    print("=" * 50)
    
    # Test 1: Pre-assessment (baseline)
    print("\n📝 Test 1: Pre-assessment (baseline)")
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
    
    post = await assessment_system.generate_post_assessment(dummy, pre, conversation)
    print(f"   Score: {post.average_score:.2f}")
    print(f"   Improvement: {post.average_score - pre.average_score:.3f}")
    
    # Test 3: Check specific question changes
    print("\n📋 Test 3: Individual Question Analysis")
    print("   Help-seeking question changes:")
    help_question_idx = 0  # "I ask for help when I need it."
    pre_help_score = pre.responses[help_question_idx].score
    post_help_score = post.responses[help_question_idx].score
    print(f"     Pre: {pre_help_score}/4")
    print(f"     Post: {post_help_score}/4")
    print(f"     Change: {post_help_score - pre_help_score}")
    
    print("\n   Calmness question changes:")
    calm_question_idx = 1  # "I stay calm when dealing with problems."
    pre_calm_score = pre.responses[calm_question_idx].score
    post_calm_score = post.responses[calm_question_idx].score
    print(f"     Pre: {pre_calm_score}/4")
    print(f"     Post: {post_calm_score}/4")
    print(f"     Change: {post_calm_score - pre_calm_score}")
    
    return {
        "pre_score": pre.average_score,
        "post_score": post.average_score,
        "improvement": post.average_score - pre.average_score,
        "help_seeking_change": post_help_score - pre_help_score,
        "calmness_change": post_calm_score - pre_calm_score
    }

if __name__ == "__main__":
    result = asyncio.run(test_human_like_assessment())
    
    print("\n" + "=" * 50)
    print("🔍 HUMAN-LIKE ASSESSMENT ANALYSIS")
    print("=" * 50)
    
    print(f"Pre-assessment: {result['pre_score']:.2f}")
    print(f"Post-assessment: {result['post_score']:.2f}")
    print(f"Overall improvement: {result['improvement']:.3f}")
    print(f"Help-seeking improvement: {result['help_seeking_change']}")
    print(f"Calmness improvement: {result['calmness_change']}")
    
    print("\n🎯 ASSESSMENT:")
    if result['improvement'] > 0.1:
        print("✅ GOOD: Coaching conversation had positive impact")
    elif result['improvement'] > 0.05:
        print("✅ MODERATE: Some improvement from coaching")
    elif abs(result['improvement']) < 0.05:
        print("⚠️  MINIMAL: Little change from coaching")
    else:
        print("❌ NEGATIVE: Coaching had negative impact")
    
    if result['help_seeking_change'] > 0:
        print("✅ Help-seeking improved (conversation was about asking for help)")
    else:
        print("❌ Help-seeking didn't improve (unexpected)")
    
    print("\n🎯 CONCLUSION:")
    if result['improvement'] > 0 and result['help_seeking_change'] > 0:
        print("   The assessment system now behaves like a human who can be influenced by coaching!")
    else:
        print("   The system may still need adjustment to show realistic human-like improvement.")
