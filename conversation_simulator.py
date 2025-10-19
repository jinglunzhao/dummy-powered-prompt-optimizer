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
            # Add grounding reminder every 5 rounds to keep conversation focused
            if round_num > 0 and round_num % 5 == 0:
                # Inject a reminder into the system context (will be seen by next AI response)
                print(f"\n🎯 Grounding checkpoint at round {round_num}", flush=True)
            
            # AI response
            print(".", end="", flush=True)  # Show progress dot
            ai_response = await self._generate_ai_response_async(conversation, system_prompt_text, dummy)
            conversation.add_turn("ai", ai_response, {"round": round_num + 1})
            
            # Dummy response based on character
            print(".", end="", flush=True)  # Show progress dot
            dummy_response = await self._generate_character_response_async(conversation, dummy, round_num + 1)
            conversation.add_turn("dummy", dummy_response, {"round": round_num + 1})
            
            # Check conversation quality every 3 rounds
            if round_num > 0 and round_num % 3 == 0:
                quality_ok, reason = self._check_conversation_quality(conversation)
                if not quality_ok:
                    print(f"\n⚠️  Conversation quality issue detected: {reason}")
                    print(f"   Ending conversation early at round {round_num + 1}")
                    break
            
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
        
        # Load student opening prompt from YAML (now includes all instructions)
        prompt = prompt_loader.get_prompt(
            'conversation_prompts.yaml',
            'student_opening_prompt',
            student_name=dummy.name,
            age=dummy.age,
            student_type=dummy.student_type,
            university=dummy.university,
            character_context=character_context
        )

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
    
    async def _generate_conversation_memo(self, conversation: Conversation, dummy: AIDummy) -> str:
        """Generate a memo of key points from conversation for AI coach's reference"""
        
        # Get conversation text
        conversation_text = ""
        for turn in conversation.turns:
            speaker_label = "Assistant" if turn.speaker == "ai" else dummy.name
            conversation_text += f"{speaker_label}: {turn.message}\n"
        
        # Load memo generation prompt
        memo_prompt = prompt_loader.get_prompt(
            'conversation_prompts.yaml',
            'conversation_memo_generation_prompt',
            conversation_text=conversation_text
        )
        
        try:
            from config import Config
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "https://api.lkeap.cloud.tencent.com/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": Config.OPENAI_MODEL,
                        "messages": [{"role": "user", "content": memo_prompt}],
                        "max_tokens": 200,
                        "temperature": 0.3
                    }
                ) as response:
                    result = await response.json()
                    return result['choices'][0]['message']['content'].strip()
        except Exception as e:
            print(f"   ⚠️ Memo generation failed: {e}")
            return "No previous conversation memo available."
    
    async def _generate_ai_response_async(self, conversation: Conversation, system_prompt: str, dummy: AIDummy) -> str:
        """Generate AI response - AI only knows what student has shared in conversation"""
        
        # Load AI coach system addition from YAML
        system_addition = prompt_loader.get_prompt(
            'conversation_prompts.yaml',
            'ai_coach_system_addition'
        )
        
        # Prepare conversation context - all in "user" role
        messages = [
            {"role": "system", "content": system_prompt + system_addition}
        ]
        
        # Build user message - NO detailed personality profile for AI
        # AI should only know what student shares in conversation
        user_content = f"You are meeting with {dummy.name}, a student seeking help with social skills.\n\n"
        
        # Add conversation memo if conversation has progressed enough
        if len(conversation.turns) >= 6:  # After 6+ turns, generate memo
            memo = await self._generate_conversation_memo(conversation, dummy)
            user_content += f"{memo}\n\n"
        
        # Add recent conversation history as formatted transcript
        if conversation.turns:
            user_content += "Recent Conversation:\n"
            for turn in conversation.turns[-6:]:  # Last 6 turns for context
                if turn.speaker == "dummy":
                    user_content += f"{dummy.name}: {turn.message}\n"
                else:
                    user_content += f"Assistant: {turn.message}\n"
            user_content += f"\nProvide your next response to {dummy.name}."
        else:
            user_content += f"{dummy.name} is about to speak with you. Prepare to listen and help."
        
        messages.append({"role": "user", "content": user_content})
        
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
                    "max_tokens": 200,  # Allow slightly longer for complete thoughts
                    "temperature": 0.6  # Reduced from 0.7 to be more focused and less creative
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
        
        # Prepare conversation context - all in "user" role
        messages = [
            {"role": "system", "content": system_content}
        ]
        
        # Build user message with profile and conversation history
        user_content = f"Student Profile: {dummy.get_character_summary()}\n\n"
        
        # Add conversation history as formatted transcript if exists
        if conversation.turns:
            user_content += "Conversation History:\n"
            for turn in conversation.turns[-6:]:  # Last 6 turns for context
                if turn.speaker == "dummy":
                    user_content += f"{dummy.name}: {turn.message}\n"
                else:
                    user_content += f"Mentor: {turn.message}\n"
        
        messages.append({"role": "user", "content": user_content})
        
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
                    "max_tokens": 150,  # Keep student responses concise
                    "temperature": 0.7  # Reduced from 0.8 to be more focused
                }
            ) as response:
                result = await response.json()
                return result['choices'][0]['message']['content'].strip()
    
    def _check_conversation_quality(self, conversation: Conversation) -> tuple[bool, str]:
        """Check if conversation is maintaining quality and staying on-topic"""
        if len(conversation.turns) < 6:
            return True, "Conversation too short to evaluate"
        
        # Get recent turns
        recent_turns = conversation.turns[-4:]
        recent_text = " ".join([turn.message.lower() for turn in recent_turns])
        
        # Check for signs of derailment
        derailment_indicators = [
            # Absurd scenarios
            ("forensics", "investigation", "detective"),
            ("conspiracy", "whistleblow", "secret agent"),
            ("llc", "ceo", "startup", "business plan"),
            ("tax", "irs", "audit", "expense"),
            # Excessive roleplay
            ("*dramatic", "*theatrical", "*playful"),
            ("*chuckles", "*grins", "*winks"),
            ("*whispers", "*gasps", "*nervous"),
            # Nonsensical elements
            ("squirrel", "cookie forensics", "noodle packet"),
            ("imaginary", "pretend", "fake"),
        ]
        
        derailment_count = 0
        for indicators in derailment_indicators:
            if any(indicator in recent_text for indicator in indicators):
                derailment_count += 1
        
        # Check for professional tone
        professional_indicators = ["advice", "suggest", "recommend", "try", "practice", "improve", "work on"]
        professional_count = sum(1 for word in professional_indicators if word in recent_text)
        
        # Determine quality
        if derailment_count >= 3:
            return False, f"High derailment detected ({derailment_count} indicators)"
        elif derailment_count >= 2 and professional_count < 2:
            return False, f"Conversation drifting off-topic"
        
        return True, "Conversation quality acceptable"
    
    def _get_character_context(self, dummy: AIDummy) -> str:
        """Create comprehensive character context from dummy data using YAML template"""
        
        personality = dummy.personality
        anxiety = dummy.social_anxiety
        
        # Load character context template from YAML - using numeric values only
        return prompt_loader.get_prompt(
            'conversation_prompts.yaml',
            'character_context_template',
            # Personality traits (numeric only)
            extraversion=personality.extraversion,
            agreeableness=personality.agreeableness,
            conscientiousness=personality.conscientiousness,
            neuroticism=personality.neuroticism,
            openness=personality.openness,
            # Social anxiety (numeric only)
            anxiety_level=anxiety.anxiety_level,
            communication_style=anxiety.communication_style,
            triggers=', '.join(anxiety.triggers),
            social_comfort=anxiety.social_comfort,
            # Personal details
            major=dummy.major,
            fears=', '.join(dummy.fears),
            goals=', '.join(dummy.goals),
            challenges=', '.join(dummy.challenges),
            behaviors=', '.join(dummy.behaviors)
        )
    
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
