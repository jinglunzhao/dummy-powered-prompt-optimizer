#!/usr/bin/env python3
"""
Debug script to examine conversation step-by-step.
Shows prompts sent to LLM and responses received.
Press Enter to continue to next step.

This uses the REAL conversation simulator implementation, not simplified prompts.
"""

import asyncio
import json
import aiohttp
from datetime import datetime
from typing import Optional

from models import AIDummy, PersonalityProfile, SocialAnxietyProfile, Conversation
from config import Config
from conversation_simulator import ConversationSimulator
from prompts.prompt_loader import prompt_loader


class DebugConversationSimulator(ConversationSimulator):
    """Wraps real ConversationSimulator to show all API calls."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.step_number = 0
        # Memo caching inherited from parent (self.current_memo, self.last_memo_at_turn)
    
    async def _debug_post(self, session, url: str, headers: dict, json_data: dict, role: str):
        """Make API call and show debug information."""
        self.step_number += 1
        
        print("\n" + "="*80)
        print(f"STEP {self.step_number}: {role}")
        print("="*80)
        
        # Show request details
        messages = json_data.get('messages', [])
        
        print("\n📤 REQUEST TO LLM:")
        print("-" * 80)
        print(f"Model: {json_data.get('model', 'N/A')}")
        print(f"Max tokens: {json_data.get('max_tokens', 'N/A')}")
        print(f"Temperature: {json_data.get('temperature', 'N/A')}")
        print()
        
        for i, msg in enumerate(messages, 1):
            print(f"Message {i} ({msg['role']}):")
            print("-" * 40)
            content = msg['content']
            # Show full content without truncation for small messages
            if len(content) > 2000:
                print(content[:800])
                print(f"\n... [{len(content) - 1600} characters omitted for display] ...\n")
                print(content[-800:])
            else:
                print(content)
            print()
        
        print("-" * 80)
        print("⏳ Sending request to LLM...")
        
        # Make the actual API call
        async with session.post(url, headers=headers, json=json_data) as response:
            result = await response.json()
        
        # Show response
        response_text = result['choices'][0]['message']['content'].strip()
        
        print("\n📥 RESPONSE FROM LLM:")
        print("-" * 80)
        print(response_text)
        print("-" * 80)
        
        # Token usage
        if 'usage' in result:
            usage = result['usage']
            print(f"\n📊 Token Usage:")
            print(f"   Prompt tokens: {usage.get('prompt_tokens', 'N/A')}")
            print(f"   Completion tokens: {usage.get('completion_tokens', 'N/A')}")
            print(f"   Total tokens: {usage.get('total_tokens', 'N/A')}")
        
        # Wait for user
        print("\n" + "="*80)
        input("Press Enter to continue to next step...")
        print()
        
        return result
    
    async def _generate_character_driven_opening(self, dummy: AIDummy) -> str:
        """Override to add debug output."""
        character_context = self._get_character_context(dummy)
        
        # Load student opening prompt from YAML (includes all instructions)
        prompt = prompt_loader.get_prompt(
            'conversation_prompts.yaml',
            'student_opening_prompt',
            student_name=dummy.name,
            age=dummy.age,
            student_type=dummy.student_type,
            university=dummy.university,
            character_context=character_context
        )
        
        # Make API call with debug
        async with aiohttp.ClientSession() as session:
            result = await self._debug_post(
                session=session,
                url="https://api.lkeap.cloud.tencent.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json_data={
                    "model": "deepseek-v3-0324",
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 300,
                    "temperature": 0.8
                },
                role="DUMMY - Opening Message"
            )
        
        response_text = result['choices'][0]['message']['content'].strip()
        return self._clean_name_prefixes(response_text)
    
    async def _generate_conversation_memo(self, conversation: Conversation, dummy: AIDummy) -> str:
        """Override to add debug output."""
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
            async with aiohttp.ClientSession() as session:
                result = await self._debug_post(
                    session=session,
                    url="https://api.lkeap.cloud.tencent.com/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json_data={
                        "model": Config.OPENAI_MODEL,
                        "messages": [{"role": "user", "content": memo_prompt}],
                        "max_tokens": 200,
                        "temperature": 0.3
                    },
                    role="MEMO GENERATION"
                )
            return result['choices'][0]['message']['content'].strip()
        except Exception as e:
            print(f"   ⚠️ Memo generation failed: {e}")
            return "No previous conversation memo available."
    
    async def _generate_ai_response_async(self, conversation: Conversation, system_prompt: str, dummy: AIDummy) -> str:
        """Override to add debug output."""
        # Load AI coach system addition from YAML
        system_addition = prompt_loader.get_prompt(
            'conversation_prompts.yaml',
            'ai_coach_system_addition'
        )
        
        # Prepare conversation context
        messages = [
            {"role": "system", "content": system_prompt + system_addition}
        ]
        
        # Build user message
        user_content = f"You are meeting with {dummy.name}, a student seeking help with social skills.\n\n"
        
        # Milestone-based memo generation (at turns 6, 12, 18, etc.)
        num_turns = len(conversation.turns)
        memo_interval = Config.MEMO_UPDATE_INTERVAL
        window_size = Config.CONVERSATION_WINDOW_SIZE
        
        # Check if we should generate/update memo
        if num_turns >= memo_interval and num_turns % memo_interval == 0:
            # We're at a memo milestone - generate new memo
            print(f"\n📝 At memo milestone (turn {num_turns}) - generating memo...")
            self.current_memo = await self._generate_conversation_memo(conversation, dummy)
            self.last_memo_at_turn = num_turns
        
        # Add cached memo if it exists (covers earlier context)
        if self.current_memo:
            user_content += f"Key Points from Earlier Conversation:\n{self.current_memo}\n\n"
        
        # Always add recent conversation (last N turns based on window size)
        # If memo exists, this avoids duplication since memo covers earlier parts
        if conversation.turns:
            user_content += "Recent Conversation:\n"
            for turn in conversation.turns[-window_size:]:  # Configurable window size
                if turn.speaker == "dummy":
                    user_content += f"{dummy.name}: {turn.message}\n"
                else:
                    user_content += f"Assistant: {turn.message}\n"
            user_content += f"\nProvide your next response to {dummy.name}."
        else:
            user_content += f"{dummy.name} is about to speak with you. Prepare to listen and help."
        
        messages.append({"role": "user", "content": user_content})
        
        # Make API call with debug
        async with aiohttp.ClientSession() as session:
            result = await self._debug_post(
                session=session,
                url="https://api.lkeap.cloud.tencent.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json_data={
                    "model": "deepseek-v3-0324",
                    "messages": messages,
                    "max_tokens": 500,
                    "temperature": 0.6
                },
                role="AI COACH - Response"
            )
        
        response_text = result['choices'][0]['message']['content'].strip()
        return self._clean_name_prefixes(response_text)
    
    async def _generate_character_response_async(self, conversation: Conversation, dummy: AIDummy, round_num: int) -> str:
        """Override to add debug output."""
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
        
        # Prepare conversation context
        messages = [
            {"role": "system", "content": system_content}
        ]
        
        # Build user message with conversation history (profile already in system message)
        window_size = Config.CONVERSATION_WINDOW_SIZE
        user_content = "Recent conversation:\n"
        for turn in conversation.turns[-window_size:]:  # Use configurable window size
            speaker_label = "Assistant" if turn.speaker == "ai" else dummy.name
            user_content += f"{speaker_label}: {turn.message}\n"
        
        user_content += f"\nRespond naturally as {dummy.name}."
        
        messages.append({"role": "user", "content": user_content})
        
        # Make API call with debug
        async with aiohttp.ClientSession() as session:
            result = await self._debug_post(
                session=session,
                url="https://api.lkeap.cloud.tencent.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json_data={
                    "model": "deepseek-v3-0324",
                    "messages": messages,
                    "max_tokens": 300,
                    "temperature": 0.7
                },
                role=f"DUMMY - Round {round_num}"
            )
        
        response_text = result['choices'][0]['message']['content'].strip()
        return self._clean_name_prefixes(response_text)


async def debug_sarah_brooks():
    """Debug Sarah Brooks's conversation step by step using REAL implementation."""
    
    print("\n" + "="*80)
    print("CONVERSATION DEBUG TOOL - Sarah Brooks")
    print("="*80)
    print("\nThis script runs the REAL conversation simulator implementation.")
    print("You'll see exactly what the actual system sends to the LLM.")
    print("Press Enter after each step to continue.\n")
    
    input("Press Enter to start...")
    
    # Load the experiment data to get Sarah Brooks's details
    with open('/home/zhaojinglun/edu_chatbot/data/experiments/continuous_conversation_with_evolution_exp_20251020_230620.json', 'r') as f:
        exp_data = json.load(f)
    
    # Find Sarah Brooks
    sarah_data = None
    for result in exp_data['results']:
        if result['dummy_name'] == 'Sarah Brooks':
            sarah_data = result
            break
    
    if not sarah_data:
        print("❌ Sarah Brooks not found in experiment data!")
        return
    
    print(f"\n✅ Found Sarah Brooks (ID: {sarah_data['dummy_id']})")
    print(f"   Original conversation: {sarah_data['total_conversation_turns']} turns")
    print(f"   Pre-assessment: {sarah_data['pre_assessment_score']}")
    print(f"   Final assessment: {sarah_data['final_assessment_score']}")
    print(f"   Final improvement: {sarah_data['final_improvement']}")
    
    # Create the dummy with proper fields
    dummy = AIDummy(
        id=sarah_data['dummy_id'],
        name=sarah_data['dummy_name'],
        age=20,
        gender="Female",
        university="State University",
        major="Mathematics",
        student_type="Undergraduate",
        personality=PersonalityProfile(
            extraversion=3,
            agreeableness=8,
            conscientiousness=4,
            neuroticism=8,
            openness=5
        ),
        social_anxiety=SocialAnxietyProfile(
            anxiety_level=8,
            communication_style="Indirect",
            triggers=["Networking events", "Campus social events", "Office hours"],
            social_comfort=6
        ),
        goals=["Learn about different cultures", "Learn a new language"],
        fears=["Choosing the right career path", "Social anxiety in large lecture halls"],
        challenges=["Preparing for presentations", "Developing effective study habits", 
                   "Overcoming procrastination", "Making friends in a new environment"],
        behaviors=["Exercises regularly", "Uses social media for networking", "Stays up late studying"]
    )
    
    print(f"\n✅ Dummy recreated: {dummy.name}")
    print(f"   Major: {dummy.major}")
    print(f"   Age: {dummy.age}")
    print(f"   Anxiety level: {dummy.social_anxiety.anxiety_level}/10")
    print(f"   Communication: {dummy.social_anxiety.communication_style}")
    
    # Get system prompt from experiment
    system_prompt = exp_data['experiment_info']['base_prompt']
    
    print(f"\n📝 System Prompt:")
    print("-" * 80)
    print(system_prompt)
    print("-" * 80)
    
    print("\n⚙️ Initializing DEBUG conversation simulator...")
    simulator = DebugConversationSimulator(api_key=Config.OPENAI_API_KEY)
    
    print("\n" + "="*80)
    print("READY TO START CONVERSATION")
    print("="*80)
    print("\nUsing the REAL conversation simulator implementation.")
    print("All prompts are generated from YAML templates.\n")
    
    input("Press Enter to start the conversation...")
    
    # Run conversation
    print("\n🎬 Starting conversation with debug mode enabled...")
    print("="*80)
    
    conversation = await simulator.simulate_conversation_async(
        dummy=dummy,
        scenario="Social skills coaching session",
        num_rounds=15,  # Run 15 rounds to match experiment
        custom_system_prompt=system_prompt
    )
    
    print("\n" + "="*80)
    print("DEBUGGING SESSION COMPLETE")
    print("="*80)
    print(f"\nCompleted {len(conversation.turns)} conversation turns")
    print(f"Duration: {conversation.duration_seconds:.1f} seconds")
    
    print("\n📊 Full Conversation Summary:")
    print("-" * 80)
    for i, turn in enumerate(conversation.turns, 1):
        print(f"\n{i}. {turn.speaker.upper()}:")
        print(turn.message[:200] + "..." if len(turn.message) > 200 else turn.message)


if __name__ == "__main__":
    asyncio.run(debug_sarah_brooks())
