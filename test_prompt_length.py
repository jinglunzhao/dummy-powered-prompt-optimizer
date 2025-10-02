#!/usr/bin/env python3
"""
Test the actual prompt length being sent to the API
"""

import json
from models import AIDummy, Conversation, ConversationTurn
from datetime import datetime
from personality_materializer import personality_materializer

def test_prompt_length():
    """Test the actual prompt length"""
    
    print("🧪 Testing Personality Materializer Prompt Length...")
    
    # Load a dummy
    with open('data/ai_dummies.json', 'r') as f:
        dummy_data = json.load(f)[0]
    dummy = AIDummy(**dummy_data)
    print(f"✅ Loaded dummy: {dummy.name}")
    
    # Create a test conversation
    conversation = Conversation(
        id="test_conv_length",
        dummy_id=dummy.id,
        system_prompt="You are a helpful peer mentor.",
        scenario="Test scenario",
        turns=[
            ConversationTurn(
                speaker="dummy",
                message="Hi, I'm struggling with social anxiety in large classes.",
                timestamp=datetime.now(),
                metadata={}
            ),
            ConversationTurn(
                speaker="ai",
                message="I understand that can be really challenging. Let's talk about some strategies that might help.",
                timestamp=datetime.now(),
                metadata={}
            ),
            ConversationTurn(
                speaker="dummy",
                message="I feel like everyone is judging me when I speak up.",
                timestamp=datetime.now(),
                metadata={}
            ),
            ConversationTurn(
                speaker="ai",
                message="That's a very common fear. Most people are focused on themselves, not judging you.",
                timestamp=datetime.now(),
                metadata={}
            )
        ]
    )
    
    # Create the materialization prompt
    prompt = personality_materializer._create_materialization_prompt(dummy, conversation)
    
    print(f"📏 Prompt length: {len(prompt)} characters")
    print(f"📊 Estimated tokens: {len(prompt) // 4} (rough estimate)")
    print(f"🔍 First 500 chars: {prompt[:500]}...")
    print(f"🔍 Last 500 chars: {prompt[-500:]}...")

if __name__ == "__main__":
    test_prompt_length()
