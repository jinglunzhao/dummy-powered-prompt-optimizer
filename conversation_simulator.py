"""
Clean Conversation Simulator - Character-Driven Social Skills Testing
Removes hardcoded scenarios and fallback templates in favor of AI-generated conversations
"""
import json
import os
import asyncio
import aiohttp
from typing import List, Dict, Any, Optional
from datetime import datetime
from models import AIDummy, Conversation, ConversationTurn
from config import Config
from prompts.prompt_loader import prompt_loader

class ConversationSimulator:
    """Simplified conversation simulator that relies on AI and character data"""
    
    def __init__(self, api_key: str = None):
        """Initialize the conversation simulator"""
        self.api_key = api_key or Config.OPENAI_API_KEY
        if not self.api_key:
            raise ValueError("API key is required for conversation simulator")
        
        print("✅ Conversation Simulator initialized")
    
    async def simulate_conversation_async(self, dummy: AIDummy, 
                                        scenario: str = None, 
                                        num_rounds: int = 5,
                                        custom_system_prompt: str = None) -> Conversation:
        """Simulate a character-driven conversation between dummy and AI"""
        
        # Create conversation with rich character context
        system_prompt_text = custom_system_prompt or Config.SYSTEM_PROMPT
        conversation = Conversation(
            dummy_id=dummy.id,
            scenario=scenario or "Social skills coaching session",  # Use provided scenario or default
            system_prompt=system_prompt_text,
            turns=[]
        )
        
        # Generate initial message based on character's actual concerns
        print("Starting conversation", end="", flush=True)
        initial_message = await self._generate_character_driven_opening(dummy)
        conversation.add_turn("dummy", initial_message, {
            "character_context": self._get_character_context(dummy)
        })
        print(" ✓", flush=True)  # Show initial message is ready
        
        # Simulate conversation rounds
        for round_num in range(num_rounds):
            # AI response
            print(".", end="", flush=True)  # Show progress dot
            ai_response = await self._generate_ai_response_async(conversation, system_prompt_text, dummy)
            conversation.add_turn("ai", ai_response, {"round": round_num + 1})
            
            # Dummy response based on character
            print(".", end="", flush=True)  # Show progress dot
            dummy_response = await self._generate_character_response_async(conversation, dummy, round_num + 1)
            conversation.add_turn("dummy", dummy_response, {"round": round_num + 1})
            
            # Check for natural ending after each complete round (AI + dummy)
            # Only check after we have at least 2 rounds (4 turns total)
            if len(conversation.turns) >= 6:  # Initial turn + 2 complete rounds
                should_end = await self.check_conversation_should_end(conversation)
                if should_end:
                    print(f"\n✅ Natural ending detected at round {round_num + 1}")
                    break
        
        print()  # New line after conversation progress
        
        # End conversation
        conversation.end_time = datetime.now()
        conversation.duration_seconds = (conversation.end_time - conversation.start_time).total_seconds()
        
        return conversation
    
    async def _generate_character_driven_opening(self, dummy: AIDummy) -> str:
        """Generate opening message based on dummy's actual fears, goals, and challenges"""
        
        character_context = self._get_character_context(dummy)
        
        # Load student opening prompt from YAML
        prompt_template = prompt_loader.get_prompt(
            'conversation_prompts.yaml',
            'student_opening_prompt',
            student_name=dummy.name,
            age=dummy.age,
            student_type=dummy.student_type,
            university=dummy.university,
            character_context=character_context
        )
        
        prompt = f"""{prompt_template}

Be authentic to your character:
- Express your real concerns and fears
- Mention specific goals you want to work on
- Show your personality traits naturally
- Be honest about your challenges

Start with a natural opening message (1-2 sentences)."""

        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.lkeap.cloud.tencent.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "deepseek-v3-0324",
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 300,
                    "temperature": 0.8
                }
            ) as response:
                result = await response.json()
                return result['choices'][0]['message']['content'].strip()
    
    async def _generate_ai_response_async(self, conversation: Conversation, system_prompt: str, dummy: AIDummy) -> str:
        """Generate AI response using the custom system prompt"""
        
        # Load AI coach system addition from YAML
        system_addition = prompt_loader.get_prompt(
            'conversation_prompts.yaml',
            'ai_coach_system_addition'
        )
        
        # Prepare conversation history
        messages = [
            {"role": "system", "content": system_prompt + system_addition},
            {"role": "user", "content": f"Student Profile: {dummy.get_character_summary()}"}
        ]
        
        # Add conversation history - properly label who said what
        # DeepSeek API: student messages = "user", AI responses = "assistant"
        for turn in conversation.turns[-6:]:  # Last 6 turns for context
            if turn.speaker == "dummy":
                # Student's message
                messages.append({"role": "user", "content": f"{dummy.name}: {turn.message}"})
            else:
                # AI coach's previous response
                messages.append({"role": "assistant", "content": turn.message})
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.lkeap.cloud.tencent.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "deepseek-v3-0324",
                    "messages": messages,
                    "max_tokens": 150,
                    "temperature": 0.7
                }
            ) as response:
                    result = await response.json()
            return result['choices'][0]['message']['content'].strip()
    
    async def _generate_character_response_async(self, conversation: Conversation, dummy: AIDummy, round_num: int) -> str:
        """Generate character-authentic response based on dummy's profile"""
        
        character_context = self._get_character_context(dummy)
        
        # Load student response system prompt from YAML
        system_content = prompt_loader.get_prompt(
            'conversation_prompts.yaml',
            'student_response_system',
            student_name=dummy.name,
            age=dummy.age,
            major=dummy.major,
            university=dummy.university,
            character_context=character_context
        )
        
        # Prepare conversation history (same as AI - last 6 turns for context)
        messages = [
            {"role": "system", "content": system_content},
            {"role": "user", "content": f"Student Profile: {dummy.get_character_summary()}"}
        ]
        
        # Add conversation history - properly label who said what
        # Student's own messages = "assistant" (what they said before)
        # AI mentor's messages = "user" (what they're responding to)
        for turn in conversation.turns[-6:]:  # Last 6 turns for context
            if turn.speaker == "dummy":
                # Student's own previous message
                messages.append({"role": "assistant", "content": turn.message})
            else:
                # AI mentor's message that student is responding to
                messages.append({"role": "user", "content": f"Mentor: {turn.message}"})
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.lkeap.cloud.tencent.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "deepseek-v3-0324",
                    "messages": messages,
                    "max_tokens": 150,
                    "temperature": 0.8
                }
            ) as response:
                result = await response.json()
                return result['choices'][0]['message']['content'].strip()
    
    def _get_character_context(self, dummy: AIDummy) -> str:
        """Create comprehensive character context from dummy data"""
        
        # Personality description
        personality = dummy.personality
        personality_desc = f"""Personality:
- Extraversion: {personality.extraversion}/10 ({'Very outgoing' if personality.extraversion >= 7 else 'Moderately social' if personality.extraversion >= 4 else 'Introverted'})
- Agreeableness: {personality.agreeableness}/10 ({'Very cooperative' if personality.agreeableness >= 7 else 'Moderately agreeable' if personality.agreeableness >= 4 else 'More competitive'})
- Conscientiousness: {personality.conscientiousness}/10 ({'Very organized' if personality.conscientiousness >= 7 else 'Moderately organized' if personality.conscientiousness >= 4 else 'More spontaneous'})
- Neuroticism: {personality.neuroticism}/10 ({'Very sensitive to stress' if personality.neuroticism >= 7 else 'Moderately sensitive' if personality.neuroticism >= 4 else 'Very emotionally stable'})
- Openness: {personality.openness}/10 ({'Very creative and curious' if personality.openness >= 7 else 'Moderately open' if personality.openness >= 4 else 'More traditional'})"""
        
        # Social anxiety description
        anxiety = dummy.social_anxiety
        anxiety_desc = f"""Social Anxiety:
- Level: {anxiety.anxiety_level}/10 ({'Severe' if anxiety.anxiety_level >= 7 else 'Moderate' if anxiety.anxiety_level >= 5 else 'Low'})
- Communication style: {anxiety.communication_style}
- Triggers: {', '.join(anxiety.triggers)}
- Social comfort: {anxiety.social_comfort}/10"""
        
        # Personal details
        personal_desc = f"""Personal Details:
- Major: {dummy.major}
- Fears: {', '.join(dummy.fears)}
- Goals: {', '.join(dummy.goals)}
- Challenges: {', '.join(dummy.challenges)}
- Behaviors: {', '.join(dummy.behaviors)}"""
        
        return f"{personality_desc}\n\n{anxiety_desc}\n\n{personal_desc}"
    
    async def check_conversation_should_end(self, conversation: Conversation) -> bool:
        """Simple, lightweight check if conversation has reached a natural ending"""
        if len(conversation.turns) < 4:  # Need at least 2 rounds
            return False
            
        # Get recent conversation context for LLM-based detection
        recent_turns = conversation.turns[-4:]  # Last 4 turns (2 rounds)
        conversation_text = "\n".join([f"{turn.speaker}: {turn.message}" for turn in recent_turns])
        
        headers = {
            "Authorization": f"Bearer {Config.DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }
        
        # Load end detection prompts from YAML
        prompt = prompt_loader.get_prompt(
            'conversation_prompts.yaml',
            'conversation_end_detection_prompt',
            conversation_text=conversation_text
        )
        
        system_content = prompt_loader.get_prompt(
            'conversation_prompts.yaml',
            'end_detection_system'
        )
        
        messages = [
            {"role": "system", "content": system_content},
            {"role": "user", "content": prompt}
        ]
        
        payload = {
            "model": "deepseek-v3-0324",
            "messages": messages,
            "temperature": 0.2,  # Slightly higher for better sensitivity
            "max_tokens": 10
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post("https://api.lkeap.cloud.tencent.com/v1/chat/completions", headers=headers, json=payload) as response:
                    result = await response.json()
                    if "choices" in result:
                        response_text = result["choices"][0]["message"]["content"].strip().upper()
                        is_ending = "YES" in response_text  # More flexible matching
                        if is_ending:
                            print(f"🎯 LLM detected ending: {response_text}")
                        return is_ending
        except Exception as e:
            print(f"⚠️  End detection API error: {e}")
            
        return False  # Default to continuing conversation

def main():
    """Test the clean conversation simulator"""
    print("Testing Clean Conversation Simulator...")
    
    # Load a dummy for testing
    with open("data/ai_dummies.json", 'r') as f:
        dummies_data = json.load(f)
    
    dummy_data = dummies_data[0]  # Get first dummy
    dummy = AIDummy(**dummy_data)
    
    print(f"Testing with dummy: {dummy.name}")
    print(f"Fears: {', '.join(dummy.fears[:2])}")
    print(f"Goals: {', '.join(dummy.goals[:2])}")
    
    # Create simulator
    simulator = ConversationSimulator()
    
    # Simulate conversation
    async def test_conversation():
        conversation = await simulator.simulate_conversation_async(dummy, num_rounds=3)
        
        print(f"\nConversation with {len(conversation.turns)} turns:")
    for turn in conversation.turns:
        speaker = "AI Coach" if turn.speaker == "ai" else dummy.name
        print(f"{speaker}: {turn.message}")
    
    asyncio.run(test_conversation())
    print("\nClean conversation simulation test complete!")

if __name__ == "__main__":
    main()
