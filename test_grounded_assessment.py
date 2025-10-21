#!/usr/bin/env python3
"""
Quick test to verify grounded assessment implementation.
"""

import asyncio
import json
from models import AIDummy
from assessment_system_llm_based import AssessmentSystemLLMBased, Assessment, AssessmentResponse
from config import Config

async def test_grounding():
    """Test that previous scores are properly passed to the LLM"""
    
    # Load a dummy
    with open('data/ai_dummies.json') as f:
        dummies_data = json.load(f)
    
    dummy_data = dummies_data[0]
    dummy = AIDummy(**dummy_data)
    
    # Initialize assessment system
    assessment_system = AssessmentSystemLLMBased(api_key=Config.DEEPSEEK_API_KEY)
    
    print("="*80)
    print("GROUNDED ASSESSMENT TEST")
    print("="*80)
    print(f"\nTesting with: {dummy.name}")
    
    # Generate pre-assessment
    print("\n1️⃣ Generating pre-assessment (baseline)...")
    pre_assessment = await assessment_system.generate_pre_assessment(dummy)
    print(f"   ✅ Pre-assessment score: {pre_assessment.average_score:.2f}")
    print(f"   Sample scores: Q1={pre_assessment.responses[0].score}, Q2={pre_assessment.responses[1].score}, Q3={pre_assessment.responses[2].score}")
    
    # Create a mock conversation
    from models import Conversation, ConversationTurn
    from datetime import datetime
    
    mock_conversation = Conversation(
        id="test_conv_001",
        dummy_id=dummy.id,
        system_prompt="Test prompt",
        scenario="Test scenario",
        turns=[
            ConversationTurn(speaker="dummy", message="I'm nervous about presentations.", timestamp=datetime.now()),
            ConversationTurn(speaker="ai", message="Let's work on that together. Start with breathing exercises.", timestamp=datetime.now()),
            ConversationTurn(speaker="dummy", message="Okay, I'll try that.", timestamp=datetime.now()),
            ConversationTurn(speaker="ai", message="Great! Practice makes progress.", timestamp=datetime.now()),
        ],
        start_time=datetime.now()
    )
    
    # Test milestone assessment with grounding
    print("\n2️⃣ Generating milestone assessment (grounded to pre-assessment)...")
    print(f"   📊 Anchoring to pre-assessment scores...")
    
    # Import ConversationSimulator for memo generation
    from conversation_simulator import ConversationSimulator
    conv_sim = ConversationSimulator()
    
    milestone_assessment = await assessment_system.generate_milestone_assessment(
        dummy=dummy,
        previous_assessment=pre_assessment,
        conversation=mock_conversation,
        conversation_simulator=conv_sim,
        turns_so_far=4
    )
    
    print(f"   ✅ Milestone assessment score: {milestone_assessment.average_score:.2f}")
    print(f"   Sample scores: Q1={milestone_assessment.responses[0].score}, Q2={milestone_assessment.responses[1].score}, Q3={milestone_assessment.responses[2].score}")
    print(f"   Change from pre: {milestone_assessment.average_score - pre_assessment.average_score:+.2f}")
    
    # Check if scores are grounded
    print("\n3️⃣ Checking grounding effectiveness:")
    changes = []
    for i in range(min(20, len(milestone_assessment.responses))):
        pre_score = pre_assessment.responses[i].score
        milestone_score = milestone_assessment.responses[i].score
        change = milestone_score - pre_score
        if change != 0:
            changes.append((i+1, pre_score, milestone_score, change))
    
    print(f"   Questions changed: {len(changes)}/20")
    if changes:
        print(f"   Changes:")
        for q_num, pre, post, delta in changes[:5]:  # Show first 5
            print(f"      Q{q_num}: {pre} → {post} ({delta:+d})")
    else:
        print(f"   ✅ Perfect grounding - no changes!")
    
    # Test post-assessment with milestone grounding
    print("\n4️⃣ Generating post-assessment (grounded to milestone)...")
    print(f"   📊 Anchoring to milestone assessment...")
    
    post_assessment = await assessment_system.generate_post_assessment(
        dummy=dummy,
        pre_assessment=pre_assessment,
        conversation=mock_conversation,
        conversation_simulator=conv_sim,
        previous_milestone_assessment=milestone_assessment
    )
    
    print(f"   ✅ Post-assessment score: {post_assessment.average_score:.2f}")
    print(f"   Sample scores: Q1={post_assessment.responses[0].score}, Q2={post_assessment.responses[1].score}, Q3={post_assessment.responses[2].score}")
    print(f"   Change from milestone: {post_assessment.average_score - milestone_assessment.average_score:+.2f}")
    print(f"   Change from baseline: {post_assessment.average_score - pre_assessment.average_score:+.2f}")
    
    print("\n" + "="*80)
    print("✅ GROUNDED ASSESSMENT TEST COMPLETE")
    print("="*80)
    print(f"\nExpected behavior:")
    print(f"  • Pre → Milestone: Small changes only (grounded to pre)")
    print(f"  • Milestone → Post: Small changes only (grounded to milestone)")
    print(f"  • Total drift should be minimal")
    print(f"\nActual results:")
    print(f"  • Pre → Milestone: {milestone_assessment.average_score - pre_assessment.average_score:+.2f}")
    print(f"  • Milestone → Post: {post_assessment.average_score - milestone_assessment.average_score:+.2f}")
    print(f"  • Total change: {post_assessment.average_score - pre_assessment.average_score:+.2f}")

if __name__ == "__main__":
    asyncio.run(test_grounding())

