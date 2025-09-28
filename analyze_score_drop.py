#!/usr/bin/env python3
"""
Analyze why overall scores drop despite dummy acknowledging improvement
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from assessment_system import AssessmentSystem
from models import AIDummy, PersonalityProfile, SocialAnxietyProfile, Conversation

async def analyze_score_drop():
    """Analyze what's causing the overall score drop"""
    
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
    
    print("🔍 ANALYZING SCORE DROP")
    print("=" * 60)
    
    # Pre-assessment
    print("\n📝 PRE-ASSESSMENT:")
    pre = await assessment_system.generate_pre_assessment(dummy)
    print(f"Overall Score: {pre.average_score:.2f}")
    
    # Show all 20 question scores
    print("\nAll 20 Question Scores (Pre):")
    for i, response in enumerate(pre.responses):
        print(f"  {i+1:2d}. {response.question[:40]:<40} {response.score}/4")
    
    # Create coaching conversation
    conversation = Conversation(
        id="test-conv",
        dummy_id=dummy.id,
        scenario="Social skills coaching",
        system_prompt="You are a helpful peer mentor for college students. Be supportive and provide practical advice.",
        turns=[]
    )
    
    # Add coaching conversation
    conversation.add_turn("dummy", "I'm really nervous about asking for help from my professors. I feel like I'm bothering them.")
    conversation.add_turn("ai", "That's totally understandable! Professors actually appreciate when students ask thoughtful questions. It shows you're engaged and care about learning. Try starting with office hours - they're specifically meant for student questions.")
    conversation.add_turn("dummy", "I guess that makes sense. I never thought of office hours that way.")
    conversation.add_turn("ai", "Exactly! And remember, asking questions helps you learn better and shows initiative. Most professors find it encouraging when students are proactive about their education.")
    conversation.add_turn("dummy", "Thanks, that actually makes me feel more confident about reaching out.")
    
    # Post-assessment
    print("\n📝 POST-ASSESSMENT:")
    post = await assessment_system.generate_post_assessment(dummy, pre, conversation)
    print(f"Overall Score: {post.average_score:.2f}")
    print(f"Overall Change: {post.average_score - pre.average_score:.3f}")
    
    # Show all 20 question scores
    print("\nAll 20 Question Scores (Post):")
    for i, response in enumerate(post.responses):
        print(f"  {i+1:2d}. {response.question[:40]:<40} {response.score}/4")
    
    # Analyze changes
    print("\n📊 DETAILED ANALYSIS:")
    print("=" * 60)
    
    improvements = 0
    declines = 0
    unchanged = 0
    total_change = 0
    
    print("Question-by-Question Changes:")
    for i, (pre_resp, post_resp) in enumerate(zip(pre.responses, post.responses)):
        change = post_resp.score - pre_resp.score
        total_change += change
        
        if change > 0:
            improvements += 1
            status = "📈 IMPROVED"
        elif change < 0:
            declines += 1
            status = "📉 DECLINED"
        else:
            unchanged += 1
            status = "➡️  UNCHANGED"
        
        print(f"  {i+1:2d}. {status} {change:+2d} - {pre_resp.question[:50]:<50}")
        
        # Show the actual responses for changed questions
        if change != 0:
            print(f"      Pre:  {pre_resp.notes[:80]}...")
            print(f"      Post: {post_resp.notes[:80]}...")
    
    print(f"\n📊 SUMMARY:")
    print(f"  Questions Improved: {improvements}")
    print(f"  Questions Declined: {declines}")
    print(f"  Questions Unchanged: {unchanged}")
    print(f"  Total Score Change: {total_change}")
    print(f"  Average Change: {total_change/20:.3f}")
    
    # Identify the problem
    print(f"\n🎯 DIAGNOSIS:")
    if declines > improvements:
        print("❌ PROBLEM: More questions declined than improved")
        print("   This suggests the dummy is becoming more critical of itself")
        print("   despite acknowledging improvement in some areas.")
    elif improvements > declines:
        print("✅ POSITIVE: More questions improved than declined")
        print("   The coaching is having a positive effect overall.")
    else:
        print("⚠️  MIXED: Equal improvements and declines")
        print("   The coaching has mixed effects on different skills.")
    
    return {
        "improvements": improvements,
        "declines": declines,
        "unchanged": unchanged,
        "total_change": total_change,
        "avg_change": total_change/20
    }

if __name__ == "__main__":
    result = asyncio.run(analyze_score_drop())
    
    print(f"\n🎯 CONCLUSION:")
    if result["declines"] > result["improvements"]:
        print("The dummy is becoming MORE CRITICAL of itself after coaching.")
        print("This could be because:")
        print("1. The dummy is more self-aware and honest about its weaknesses")
        print("2. The coaching made it realize it has more areas to improve")
        print("3. The dummy is being overly critical in its self-assessment")
        print("4. The assessment questions don't align well with the coaching content")
    else:
        print("The coaching is having a positive effect on the dummy's self-assessment.")
