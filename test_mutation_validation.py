#!/usr/bin/env python3
"""
Test script for mutation prompt generation and validation
This isolates the mutation/validation logic to debug the issue
"""

import asyncio
import json
import sys
import os
from config import Config

# Import the mutation logic from prompt_optimizer
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from prompt_optimizer import PromptOptimizer, OptimizedPrompt
from prompt_naming import genealogy_tracker
from datetime import datetime

# Mock conversation storage to avoid JSON parsing issues
class MockConversationStorage:
    def get_conversations_by_prompt(self, prompt_id):
        return [
            {
                "conversation_id": "test_conv_1",
                "dummy_id": "test_dummy_1", 
                "conversation": [
                    {"turn": 1, "speaker": "dummy", "content": "Hi, I need help with social anxiety."},
                    {"turn": 2, "speaker": "ai", "content": "I'm here to help! What specific situations make you anxious?"},
                    {"turn": 3, "speaker": "dummy", "content": "Public speaking and group discussions."},
                    {"turn": 4, "speaker": "ai", "content": "Let's work on some strategies together."}
                ],
                "performance_metrics": {"improvement": 0.5}
            }
        ]

class MutationTester:
    def __init__(self):
        self.optimizer = PromptOptimizer()
        # Replace conversation storage with mock
        self.optimizer.conversation_storage = MockConversationStorage()
        
    async def test_mutation_validation(self):
        """Test the mutation prompt generation and validation process"""
        
        print("🧪 Testing Mutation Prompt Generation and Validation")
        print("=" * 60)
        
        # Create a test parent prompt through genealogy tracker
        parent_text = "You are a helpful peer mentor for college students. Be supportive and provide practical advice."
        parent_node = genealogy_tracker.create_initial_prompt(parent_text)
        
        parent_prompt = OptimizedPrompt(
            id=parent_node.id,
            name=parent_node.name,
            prompt_text=parent_text,
            components=["test_component"],
            generation=0,
            performance_metrics={"avg_improvement": 0.467},
            pareto_rank=1,
            created_at=datetime.now(),
            last_tested=None
        )
        
        print(f"📝 Parent Prompt: {parent_prompt.prompt_text}")
        print(f"📊 Parent Performance: {parent_prompt.performance_metrics}")
        print()
        
        # Test the mutation process
        print("🔄 Testing mutation process...")
        try:
            mutated_prompt = self.optimizer._mutate_prompt(parent_prompt, max_retries=2)
            
            if mutated_prompt:
                print(f"✅ Mutation successful!")
                print(f"📝 Mutated Prompt: {mutated_prompt.prompt_text}")
                print(f"📊 Length: {len(mutated_prompt.prompt_text)} characters")
                print(f"🆔 ID: {mutated_prompt.id}")
                print(f"🏷️  Name: {mutated_prompt.name}")
                return True
            else:
                print("❌ Mutation failed - returned None")
                return False
                
        except Exception as e:
            print(f"❌ Mutation process failed with error: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    async def test_validation_logic(self, test_prompts):
        """Test the validation logic with various prompt formats"""
        
        print("\n🧪 Testing Validation Logic")
        print("=" * 40)
        
        for i, prompt_text in enumerate(test_prompts):
            print(f"\nTest {i+1}: {prompt_text[:50]}...")
            
            # Simulate the validation logic from the mutation function
            mutated_prompt_text = prompt_text.strip()
            
            # More robust validation - check for "you are" anywhere in first 50 chars, handle quotes
            first_part = mutated_prompt_text[:50].lower()
            has_you_are = "you are" in first_part
            has_proper_length = len(mutated_prompt_text) >= 20
            
            print(f"   - Contains 'you are': {has_you_are}")
            print(f"   - Length >= 20: {has_proper_length} (actual: {len(mutated_prompt_text)})")
            print(f"   - First 50 chars: '{first_part}'")
            
            if not has_you_are or not has_proper_length:
                print(f"   ❌ VALIDATION FAILED")
            else:
                print(f"   ✅ VALIDATION PASSED")

async def main():
    """Main test function"""
    
    # Test prompts with various formats that might cause issues
    test_prompts = [
        "You are a supportive peer mentor for college students who combines practical advice with emotional support.",
        "\"You are a supportive peer mentor for college students who combines practical advice with emotional support.\"",
        "  You are a supportive peer mentor for college students who combines practical advice with emotional support.  ",
        "You are a deeply attentive social skills mentor who helps college students build confidence through personalized guidance and practical strategies.",
        "You are a thoughtful social skills mentor who actively listens before responding, using strategic questioning to help students discover their own solutions.",
        "You are a supportive peer mentor for college students who combines practical advice with deep emotional understanding to help them navigate social challenges effectively.",
        "You are a helpful mentor",  # Too short
        "I am a supportive peer mentor",  # Wrong format
        "You help college students",  # Wrong format
    ]
    
    tester = MutationTester()
    
    # Test validation logic first
    await tester.test_validation_logic(test_prompts)
    
    # Test actual mutation process
    print("\n" + "=" * 60)
    success = await tester.test_mutation_validation()
    
    if success:
        print("\n🎉 All tests completed successfully!")
    else:
        print("\n❌ Tests failed - check the output above for details")

if __name__ == "__main__":
    asyncio.run(main())
