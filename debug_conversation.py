#!/usr/bin/env python3
"""
Debug script to examine FULL EXPERIMENT WORKFLOW step-by-step.

USAGE:
    python debug_conversation.py --dummy "Greg Moore"
    python debug_conversation.py --dummy "Sarah" --file data/experiments/continuous_conversation_with_evolution_exp_20251021_120000.json

WHAT THIS DOES:
    1. Loads a specific dummy from the latest experiment results
    2. Re-runs the EXACT SAME workflow: pre-assessment → conversation → milestones → post-assessment
    3. Shows EVERY prompt sent to the LLM and EVERY response received
    4. Pauses after each LLM call so you can examine the interaction

KEY FEATURES:
    - Uses the REAL ConversationLengthExperimentWithEvolution.run_dummy_experiment() method
    - Debug wrappers intercept LLM calls to display prompts/responses without changing logic
    - Matches the exact experiment workflow including memo generation, milestone assessments, etc.

WHY USE THIS:
    - Understand why a conversation produced unexpected results (e.g., negative improvement scores)
    - See exactly what prompts are being sent to the LLM at each step
    - Debug assessment scoring logic
    - Verify conversation quality and turn-taking behavior

IMPORTANT: Debug wrappers reimplement LLM-calling methods to add visibility.
They MUST be kept in sync with the parent classes (ConversationSimulator, AssessmentSystemLLMBased).
"""

import asyncio
import json
import re
import glob
import aiohttp
from datetime import datetime
from typing import Optional, Dict, Any

from models import AIDummy, PersonalityProfile, SocialAnxietyProfile, Conversation, Assessment
from config import Config
from conversation_simulator import ConversationSimulator
from assessment_system_llm_based import AssessmentSystemLLMBased
from personality_materializer import PersonalityMaterializer
from prompts.prompt_loader import prompt_loader


# Global counter for all LLM calls
step_counter = {"count": 0}


async def debug_api_call(url: str, headers: dict, json_data: dict, role: str):
    """Make API call with debug output."""
    step_counter["count"] += 1
    
    print("\n" + "="*80)
    print(f"STEP {step_counter['count']}: {role}")
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
        if len(content) > 2000:
            print(content[:800])
            print(f"\n... [{len(content) - 1600} characters omitted] ...\n")
            print(content[-800:])
        else:
            print(content)
        print()
    
    print("-" * 80)
    print("⏳ Sending request...")
    
    # Make actual API call
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=json_data) as response:
            result = await response.json()
    
    # Show response
    response_text = result['choices'][0]['message']['content'].strip()
    
    print("\n📥 RESPONSE:")
    print("-" * 80)
    if len(response_text) > 1500:
        print(response_text[:700])
        print(f"\n... [{len(response_text) - 1400} characters omitted] ...\n")
        print(response_text[-700:])
    else:
        print(response_text)
    print("-" * 80)
    
    # Token usage
    if 'usage' in result:
        usage = result['usage']
        print(f"\n📊 Tokens: {usage.get('prompt_tokens', 0)} in + {usage.get('completion_tokens', 0)} out = {usage.get('total_tokens', 0)} total")
    
    # Wait for user
    print("\n" + "="*80)
    input("Press Enter to continue...")
    print()
    
    return result


class DebugConversationSimulator(ConversationSimulator):
    """
    Debug wrapper for conversation simulator.
    
    IMPORTANT: This class reimplements the LLM-calling methods to add debug output.
    The logic MUST be kept in sync with ConversationSimulator in conversation_simulator.py.
    Any changes to the parent class methods should be reflected here.
    """
    
    def __init__(self, api_key: str):
        """Initialize with memo tracking."""
        super().__init__(api_key=api_key)
        self.current_memo = None
        self.last_memo_at_turn = 0
    
    async def _generate_character_driven_opening(self, dummy: AIDummy) -> str:
        """Override with debug output."""
        character_context = self._get_character_context(dummy)
        prompt = prompt_loader.get_prompt(
            'conversation_prompts.yaml', 'student_opening_prompt',
            student_name=dummy.name, age=dummy.age, student_type=dummy.student_type,
            university=dummy.university, character_context=character_context
        )
        
        result = await debug_api_call(
            "https://api.lkeap.cloud.tencent.com/v1/chat/completions",
            {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
            {"model": "deepseek-v3-0324", "messages": [{"role": "user", "content": prompt}],
             "max_tokens": 300, "temperature": 0.8},
            "DUMMY - Opening Message"
        )
        return self._clean_name_prefixes(result['choices'][0]['message']['content'].strip())
    
    async def _generate_conversation_memo(self, conversation: Conversation, dummy: AIDummy) -> str:
        """Override with debug output."""
        conversation_text = ""
        for turn in conversation.turns:
            speaker_label = "Assistant" if turn.speaker == "ai" else dummy.name
            conversation_text += f"{speaker_label}: {turn.message}\n"
        
        memo_prompt = prompt_loader.get_prompt(
            'conversation_prompts.yaml', 'conversation_memo_generation_prompt',
            conversation_text=conversation_text
        )
        
        try:
            result = await debug_api_call(
                "https://api.lkeap.cloud.tencent.com/v1/chat/completions",
                {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
                {"model": Config.OPENAI_MODEL, "messages": [{"role": "user", "content": memo_prompt}],
                 "max_tokens": 200, "temperature": 0.3},
                "MEMO GENERATION"
            )
            return result['choices'][0]['message']['content'].strip()
        except Exception as e:
            print(f"⚠️ Memo failed: {e}")
            return "No memo available."
    
    async def _generate_ai_response_async(self, conversation: Conversation, system_prompt: str, dummy: AIDummy) -> str:
        """Override with debug output."""
        # Memo is now generated in main loop after turn 6, 12, 18... are added
        # This method just uses the memo if it exists
        
        system_addition = prompt_loader.get_prompt('conversation_prompts.yaml', 'ai_coach_system_addition')
        messages = [{"role": "system", "content": system_prompt + system_addition}]
        
        user_content = f"You are meeting with {dummy.name}, a student seeking help with social skills.\n\n"
        
        if self.current_memo:
            user_content += f"Key Points from Earlier Conversation:\n{self.current_memo}\n\n"
        
        if conversation.turns:
            user_content += "Recent Conversation:\n"
            for turn in conversation.turns[-Config.CONVERSATION_WINDOW_SIZE:]:
                speaker_label = "Assistant" if turn.speaker == "ai" else dummy.name
                user_content += f"{speaker_label}: {turn.message}\n"
            user_content += f"\nProvide your next response to {dummy.name}."
        
        messages.append({"role": "user", "content": user_content})
        
        result = await debug_api_call(
            "https://api.lkeap.cloud.tencent.com/v1/chat/completions",
            {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
            {"model": "deepseek-v3-0324", "messages": messages, "max_tokens": 500, "temperature": 0.6},
            "AI COACH - Response"
        )
        return self._clean_name_prefixes(result['choices'][0]['message']['content'].strip())
    
    async def _generate_character_response_async(self, conversation: Conversation, dummy: AIDummy, round_num: int) -> str:
        """Override with debug output."""
        character_context = self._get_character_context(dummy)
        system_content = prompt_loader.get_prompt(
            'conversation_prompts.yaml', 'student_response_system',
            student_name=dummy.name, age=dummy.age, major=dummy.major,
            university=dummy.university, character_context=character_context
        )
        
        messages = [{"role": "system", "content": system_content}]
        
        user_content = "Recent conversation:\n"
        for turn in conversation.turns[-Config.CONVERSATION_WINDOW_SIZE:]:
            speaker_label = "Assistant" if turn.speaker == "ai" else dummy.name
            user_content += f"{speaker_label}: {turn.message}\n"
        user_content += f"\nRespond naturally as {dummy.name}."
        
        messages.append({"role": "user", "content": user_content})
        
        result = await debug_api_call(
            "https://api.lkeap.cloud.tencent.com/v1/chat/completions",
            {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
            {"model": "deepseek-v3-0324", "messages": messages, "max_tokens": 300, "temperature": 0.7},
            f"DUMMY - Round {round_num}"
        )
        return self._clean_name_prefixes(result['choices'][0]['message']['content'].strip())


class DebugAssessmentSystem(AssessmentSystemLLMBased):
    """
    Debug wrapper for assessment system.
    
    IMPORTANT: This class reimplements _get_llm_assessment to add debug output.
    The logic MUST match AssessmentSystemLLMBased in assessment_system_llm_based.py.
    """
    
    async def _get_llm_assessment(self, system_prompt: str, user_prompt: str, dummy: AIDummy) -> str:
        """Override with debug output - matches parent implementation exactly."""
        
        # Extract a short description for the step label
        step_label = "ASSESSMENT"
        
        # Check for different assessment types
        user_lower = user_prompt.lower()
        system_lower = system_prompt.lower()
        
        if "baseline assessment" in user_lower or "baseline assessment" in system_lower:
            step_label = "PRE-ASSESSMENT (Baseline)"
        elif "post-conversation" in user_lower or "post-conversation" in system_lower:
            if "inherited" in user_lower:
                step_label = "POST-ASSESSMENT (Inherited)"
            else:
                step_label = "POST-ASSESSMENT"
        elif "milestone" in user_lower or "at round" in user_lower:
            # Try to extract milestone number
            match = re.search(r'round (\d+)', user_lower)
            if match:
                step_label = f"MILESTONE {match.group(1)} ASSESSMENT"
            else:
                step_label = "MILESTONE ASSESSMENT"
        elif "baseline" in user_lower or "baseline" in system_lower:
            step_label = "PRE-ASSESSMENT"
        
        result = await debug_api_call(
            "https://api.lkeap.cloud.tencent.com/v1/chat/completions",
            {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
            {
                "model": "deepseek-v3-0324",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "max_tokens": 2000,
                "temperature": 0.3
            },
            step_label
        )
        
        return result['choices'][0]['message']['content'].strip()


async def debug_dummy_full_workflow(dummy_name: str = None, experiment_file: str = None):
    """Debug a specific dummy with FULL experiment workflow including assessments."""
    
    print("\n" + "="*80)
    print(f"FULL EXPERIMENT WORKFLOW DEBUG - {dummy_name or 'Dummy'}")
    print("="*80)
    print("\nThis uses the EXACT SAME workflow as conversation_length_experiment_with_evolution.py:")
    print("\n🔄 WORKFLOW:")
    print("  1. Pre-assessment (baseline)")
    print("  2. Full conversation run:")
    print("     - Opening message (character-driven) = turn 1")
    print("     - Back-and-forth (AI → Dummy → AI → Dummy...)")
    print("     - ⚡ Memo generation DURING conversation at turns 6, 12, 18, etc.")
    print("     - Natural ending detection")
    print("  3. AFTER conversation completes:")
    print("     - Process milestone at turn 11 (~5 exchanges) if reached")
    print("     - Process milestone at turn 21 (~10 exchanges) if reached, else inherit")
    print("     - Process milestone at turn 31 (~15 exchanges) if reached, else inherit")
    print("  4. Post-assessment (or inherit if ended early)")
    print("\n⏸️  Press Enter after each LLM call to continue.\n")
    
    input("Press Enter to start...")
    
    # Find the experiment file to load
    if not experiment_file:
        files = glob.glob('/home/zhaojinglun/edu_chatbot/data/experiments/continuous_conversation_with_evolution_exp_*.json')
        if not files:
            print("❌ No experiment files found!")
            return
        experiment_file = max(files)  # Get the latest one
        print(f"📁 Using latest experiment: {experiment_file}")
    
    # Load experiment data
    with open(experiment_file, 'r') as f:
        exp_data = json.load(f)
    
    # Find the dummy
    dummy_data = None
    if dummy_name:
        for result in exp_data['results']:
            if dummy_name.lower() in result['dummy_name'].lower():
                dummy_data = result
                break
    
    if not dummy_data:
        print(f"\n❌ Dummy '{dummy_name}' not found in experiment!")
        print("\nAvailable dummies:")
        for result in exp_data['results']:
            print(f"   - {result['dummy_name']}")
        return
    
    print(f"\n✅ Found {dummy_data['dummy_name']}")
    print(f"   Original result: {dummy_data['total_conversation_turns']} turns")
    print(f"   Pre-assessment: {dummy_data['pre_assessment_score']:.2f}")
    print(f"   Post-assessment: {dummy_data['final_assessment_score']:.2f}")
    print(f"   Improvement: {dummy_data['final_improvement']:+.3f}")
    
    # Load the full dummy from ai_dummies.json
    try:
        with open('data/ai_dummies.json', 'r') as f:
            dummies_data = json.load(f)
            all_dummies = [AIDummy(**d) for d in dummies_data]
    except FileNotFoundError:
        print(f"❌ Could not find data/ai_dummies.json")
        return
    
    dummy = None
    for d in all_dummies:
        if d.id == dummy_data['dummy_id']:
            dummy = d
            break
    
    if not dummy:
        print(f"❌ Could not find dummy {dummy_data['dummy_id']} in ai_dummies.json")
        print(f"   Looking for ID: {dummy_data['dummy_id']}")
        return
    
    print(f"   Anxiety: {dummy.social_anxiety.anxiety_level}/10")
    print(f"   Communication: {dummy.social_anxiety.communication_style}")
    
    system_prompt = exp_data['experiment_info']['base_prompt']
    
    print(f"\n⚙️ Configuration:")
    print(f"   Max turns: 31 (15 exchanges), Milestones at turns: [11, 21, 31]")
    print(f"   Window: {Config.CONVERSATION_WINDOW_SIZE} turns, Memo: every {Config.MEMO_UPDATE_INTERVAL} turns")
    
    print("\n" + "="*80)
    input("Press Enter to begin full workflow...")
    
    # Import experiment class
    from conversation_length_experiment_with_evolution import ConversationLengthExperimentWithEvolution
    
    # Create experiment with debug components
    experiment = ConversationLengthExperimentWithEvolution()
    experiment.conversation_simulator = DebugConversationSimulator(api_key=Config.OPENAI_API_KEY)
    experiment.assessment_system = DebugAssessmentSystem(api_key=Config.DEEPSEEK_API_KEY)
    
    print("\n🎬 Starting FULL experiment workflow...")
    print("="*80)
    
    # Run experiment
    result = await experiment.run_dummy_experiment(
        dummy=dummy, max_rounds=15, milestones=[5, 10, 15],
        base_prompt=system_prompt, save_details=True, enable_assessments=True
    )
    
    print("\n" + "="*80)
    print("COMPLETE")
    print("="*80)
    
    print(f"\n📊 Results:")
    print(f"   Turns: {result['total_conversation_turns']}")
    print(f"   Ended early: {'Yes 🔚' if result.get('conversation_ended_early') else 'No ✅'}")
    print(f"   Milestones: {result.get('milestones_reached', '?')}/{result.get('milestones_total', '?')}")
    print(f"   Pre: {result['pre_assessment_score']:.2f}")
    print(f"   Post: {result['final_assessment_score']:.2f} {'(inherited)' if result.get('post_assessment_inherited') else ''}")
    print(f"   Improvement: {result['final_improvement']:+.3f}")
    
    print("\n📋 Milestones:")
    for m in result['milestone_results']:
        marker = "✅" if m.get('reached', True) else "⏭️"
        milestone_turns = 1 + m['milestone_rounds'] * 2
        print(f"   {marker} Turn {milestone_turns}: {m['milestone_score']:.2f} (Δ{m['improvement']:+.3f}) - {m['note']}")
    
    # Save
    output_file = f"data/experiments/debug_sarah_brooks_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2, default=str)
    print(f"\n💾 Saved to: {output_file}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Debug a specific dummy's conversation flow step-by-step")
    parser.add_argument("--dummy", "-d", type=str, help="Dummy name to debug (e.g., 'Greg Moore', 'Sarah Brooks')")
    parser.add_argument("--file", "-f", type=str, help="Experiment file to load (default: latest)")
    args = parser.parse_args()
    
    if not args.dummy:
        print("❌ Please specify a dummy name with --dummy")
        print("\nExample:")
        print("  python debug_conversation.py --dummy 'Greg Moore'")
        print("  python debug_conversation.py --dummy 'Sarah' --file data/experiments/continuous_conversation_with_evolution_exp_20251021_120000.json")
        exit(1)
    
    asyncio.run(debug_dummy_full_workflow(dummy_name=args.dummy, experiment_file=args.file))
