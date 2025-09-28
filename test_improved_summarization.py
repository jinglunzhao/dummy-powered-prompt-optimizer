#!/usr/bin/env python3
"""
Test the improved conversation summarization
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from assessment_system import AssessmentSystem
from models import AIDummy, PersonalityProfile, SocialAnxietyProfile, Conversation

async def test_improved_summarization():
    """Test if improved conversation summarization works better"""
    
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
    
    print("🧪 Testing Improved Conversation Summarization")
    print("=" * 60)
    
    # Pre-assessment
    print("\n📝 Pre-assessment:")
    pre = await assessment_system.generate_pre_assessment(dummy)
    print(f"Score: {pre.average_score:.2f}")
    
    # Create a detailed coaching conversation
    conversation = Conversation(
        id="test-conv",
        dummy_id=dummy.id,
        scenario="Social skills coaching",
        system_prompt="You are a helpful peer mentor for college students. Be supportive and provide practical advice.",
        turns=[]
    )
    
    # Add a realistic coaching conversation
    conversation.add_turn("dummy", "I'm really nervous about asking for help from my professors. I feel like I'm bothering them and they'll think I'm not smart enough.")
    conversation.add_turn("ai", "That's totally understandable! Many students feel this way. But professors actually appreciate when students ask thoughtful questions. It shows you're engaged and care about learning. Try starting with office hours - they're specifically meant for student questions.")
    conversation.add_turn("dummy", "I guess that makes sense. I never thought of office hours that way. I always thought they were for students who were really struggling.")
    conversation.add_turn("ai", "Not at all! Office hours are for all students. Even the top students ask questions. Remember, asking questions helps you learn better and shows initiative. Most professors find it encouraging when students are proactive about their education.")
    conversation.add_turn("dummy", "Thanks, that actually makes me feel more confident about reaching out. Maybe I'll start with my Algorithms professor - she seems really approachable.")
    conversation.add_turn("ai", "That's a great choice! Start small - maybe ask one question in your next class or visit office hours once. You'll see that professors are usually very supportive and want to help you succeed.")
    
    # Show the conversation summary
    conversation_context = assessment_system._summarize_conversation_for_assessment(conversation)
    print(f"\n📝 Conversation Summary:")
    print(f"'{conversation_context}'")
    
    # Post-assessment
    print(f"\n📝 Post-assessment:")
    post = await assessment_system.generate_post_assessment(dummy, pre, conversation)
    print(f"Score: {post.average_score:.2f}")
    print(f"Improvement: {post.average_score - pre.average_score:.3f}")
    
    # Check specific improvements
    help_question_idx = 0  # "I ask for help when I need it."
    pre_help_score = pre.responses[help_question_idx].score
    post_help_score = post.responses[help_question_idx].score
    
    print(f"\n📊 Help-seeking improvement: {pre_help_score}/4 → {post_help_score}/4 ({post_help_score - pre_help_score:+d})")
    
    # Show the actual responses
    print(f"\n📝 Pre-assessment response:")
    print(f"'{pre.responses[help_question_idx].notes[:150]}...'")
    print(f"\n📝 Post-assessment response:")
    print(f"'{post.responses[help_question_idx].notes[:150]}...'")
    
    return {
        "pre_score": pre.average_score,
        "post_score": post.average_score,
        "improvement": post.average_score - pre.average_score,
        "help_seeking_change": post_help_score - pre_help_score
    }

if __name__ == "__main__":
    result = asyncio.run(test_improved_summarization())
    
    print(f"\n🎯 RESULTS:")
    print(f"Pre-assessment: {result['pre_score']:.2f}")
    print(f"Post-assessment: {result['post_score']:.2f}")
    print(f"Overall improvement: {result['improvement']:.3f}")
    print(f"Help-seeking change: {result['help_seeking_change']:+d}")
    
    if result['improvement'] > 0.1:
        print("✅ EXCELLENT: Significant improvement achieved!")
    elif result['improvement'] > 0.05:
        print("✅ GOOD: Moderate improvement achieved!")
    elif result['improvement'] > 0:
        print("✅ POSITIVE: Some improvement achieved!")
    else:
        print("⚠️  MINIMAL: Little improvement achieved")
    
    if result['help_seeking_change'] > 0:
        print("✅ Help-seeking improved as expected from coaching!")
    else:
        print("⚠️  Help-seeking didn't improve despite relevant coaching")
