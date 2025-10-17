#!/usr/bin/env python3
"""
Test Conversation Quality - Verify conversations stay grounded and professional
"""

import asyncio
import json
from datetime import datetime
from models import AIDummy
from conversation_simulator import ConversationSimulator

async def test_conversation_quality():
    """Test that conversations maintain quality and don't derail"""
    print("="*70)
    print("  CONVERSATION QUALITY TEST")
    print("="*70)
    
    # Load test dummy
    with open('data/ai_dummies.json', 'r') as f:
        dummies_data = json.load(f)
    
    # Use Gregory Moore (was problematic before)
    test_dummy = None
    for d in dummies_data:
        if d['name'] == 'Gregory Moore':
            test_dummy = AIDummy.model_validate(d)
            break
    
    if not test_dummy:
        print("❌ Could not find Gregory Moore in dummies")
        return False
    
    print(f"\n🧪 Testing with: {test_dummy.name}")
    print(f"   Personality: {test_dummy.personality}")
    print(f"   Anxiety: {test_dummy.social_anxiety.anxiety_level}/10")
    
    # Test prompt
    test_prompt = """You are a helpful peer mentor for college students. 
Provide supportive, practical advice to help students with their social skills 
and personal challenges. Stay professional and focused on real issues."""
    
    # Run conversation
    simulator = ConversationSimulator()
    print(f"\n💬 Running conversation (up to 15 rounds)...")
    
    conversation = await simulator.simulate_conversation_async(
        dummy=test_dummy,
        num_rounds=15,
        custom_system_prompt=test_prompt
    )
    
    print(f"\n📊 Results:")
    print(f"   Total turns: {len(conversation.turns)}")
    print(f"   Duration: {conversation.duration_seconds:.1f}s")
    
    # Analyze conversation quality
    print(f"\n🔍 Quality Analysis:")
    
    # Check first few turns
    print(f"\n   First 3 turns:")
    for i in range(min(3, len(conversation.turns))):
        turn = conversation.turns[i]
        msg = turn.message[:100]
        print(f"      {i+1}. [{turn.speaker}]: {msg}...")
    
    # Check last few turns
    if len(conversation.turns) > 6:
        print(f"\n   Last 3 turns:")
        for i in range(max(0, len(conversation.turns) - 3), len(conversation.turns)):
            turn = conversation.turns[i]
            msg = turn.message[:100]
            print(f"      {i+1}. [{turn.speaker}]: {msg}...")
    
    # Run quality check
    quality_ok, reason = simulator._check_conversation_quality(conversation)
    
    print(f"\n   Quality Check: {'✅ PASSED' if quality_ok else '❌ FAILED'}")
    print(f"   Reason: {reason}")
    
    # Check for derailment indicators
    all_text = " ".join([t.message.lower() for t in conversation.turns])
    
    derailment_signs = {
        "cookie forensics": "cookie forensics" in all_text,
        "squirrel conspiracy": "squirrel" in all_text and "conspiracy" in all_text,
        "llc/ceo/startup": any(word in all_text for word in ["llc", "ceo of"]),
        "excessive roleplay": all_text.count("*dramatic") + all_text.count("*theatrical") > 5,
    }
    
    print(f"\n   Derailment Indicators:")
    for sign, detected in derailment_signs.items():
        status = "❌ DETECTED" if detected else "✅ None"
        print(f"      {sign}: {status}")
    
    # Overall assessment
    print(f"\n{'='*70}")
    has_derailment = any(derailment_signs.values())
    
    if quality_ok and not has_derailment:
        print("✅ TEST PASSED: Conversation maintained quality")
        return True
    else:
        print("❌ TEST FAILED: Conversation quality issues detected")
        if has_derailment:
            print("   Specific issues:")
            for sign, detected in derailment_signs.items():
                if detected:
                    print(f"      - {sign}")
        return False

async def main():
    """Run the test"""
    success = await test_conversation_quality()
    
    # Save test results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = f"data/test_results/conversation_quality_test_{timestamp}.json"
    
    with open(results_file, 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'test': 'conversation_quality',
            'passed': success
        }, f, indent=2)
    
    print(f"\nResults saved to: {results_file}")
    
    if not success:
        exit(1)

if __name__ == '__main__':
    asyncio.run(main())

