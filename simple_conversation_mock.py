#!/usr/bin/env python3
"""
Simple conversation mock for manual testing using REAL conversation modules
Allows step-by-step conversation flow to observe natural ending patterns
"""

import asyncio
import json
import os
import sys
import random
import argparse
from typing import List, Dict, Any

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from conversation_simulator import ConversationSimulator
from models import AIDummy
from config import Config
from prompts.prompt_loader import prompt_loader

class SimpleConversationMock:
    def __init__(self):
        """Initialize using real conversation simulator"""
        self.simulator = ConversationSimulator()
        self.conversation = None
        self.dummy = None
        
    async def start_conversation(self, dummy: AIDummy, num_rounds: int = 10):
        """Start a conversation using the real conversation simulator"""
        self.dummy = dummy
        # Load prompt from YAML instead of hardcoding
        system_prompt = prompt_loader.get_prompt('default_prompts.yaml', 'default_peer_mentor_prompt')
        self.conversation = await self.simulator.simulate_conversation_async(
            dummy=dummy,
            scenario="Social skills coaching session",
            num_rounds=num_rounds,
            custom_system_prompt=system_prompt
        )
        
        print(f"\n🎯 Started conversation with {dummy.name}")
        print(f"📊 Character: {dummy.age}-year-old {dummy.major} student")
        print(f"🎭 Fears: {', '.join(dummy.fears[:3])}")
        print(f"🎯 Goals: {', '.join(dummy.goals[:3])}")
        print(f"⚡ Challenges: {', '.join(dummy.challenges[:3])}")
        print("=" * 60)
        
        # Show initial conversation
        self._display_conversation()
        
    def _display_conversation(self):
        """Display the current conversation"""
        if not self.conversation or not self.conversation.turns:
            print("No conversation to display")
            return
            
        print(f"\n📝 Conversation ({len(self.conversation.turns)} turns):")
        print("-" * 40)
        
        for i, turn in enumerate(self.conversation.turns, 1):
            speaker = "AI Coach" if turn.speaker == "ai" else self.dummy.name
            print(f"{i}. {speaker}: {turn.message}")
            
    async def continue_conversation(self, additional_rounds: int = 1):
        """Continue the conversation with additional rounds"""
        if not self.conversation or not self.dummy:
            print("❌ No active conversation to continue")
            return
            
        print(f"\n🔄 Adding {additional_rounds} more rounds...")
        
        # Remember starting turn count
        start_turns = len(self.conversation.turns)
        
        # Continue the conversation using the real simulator
        for round_num in range(additional_rounds):
            try:
                # Generate next AI response
                ai_response = await self.simulator._generate_ai_response_async(
                    self.conversation, self.conversation.system_prompt, self.dummy
                )
                self.conversation.add_turn("ai", ai_response)
                
                # Generate next student response
                student_response = await self.simulator._generate_character_response_async(
                    self.conversation, self.dummy, len(self.conversation.turns) // 2 + 1
                )
                self.conversation.add_turn("dummy", student_response)
                
                print(f"✓ Added round {round_num + 1} (turns {len(self.conversation.turns) - 1} & {len(self.conversation.turns)})")
                
            except Exception as e:
                print(f"❌ Error adding turn: {e}")
                break
        
        # Show only the newly added turns
        new_turns = len(self.conversation.turns) - start_turns
        if new_turns > 0:
            print(f"\n📝 New turns ({new_turns} added):")
            print("-" * 30)
            for i in range(start_turns, len(self.conversation.turns)):
                turn = self.conversation.turns[i]
                speaker = "AI Coach" if turn.speaker == "ai" else self.dummy.name
                print(f"{i + 1}. {speaker}: {turn.message}")
        
    async def check_natural_ending(self) -> bool:
        """Check if conversation has reached a natural ending using the real system"""
        if not self.conversation:
            return False
            
        try:
            # Use the new simple end detection from conversation simulator
            should_end = await self.simulator.check_conversation_should_end(self.conversation)
            
            current_rounds = len(self.conversation.turns) // 2  # Each round = 2 turns
            
            print(f"🔍 Natural ending check:")
            print(f"   • Current rounds: {current_rounds}")
            print(f"   • Should end: {should_end}")
            
            return should_end
                
        except Exception as e:
            print(f"❌ Error checking natural ending: {e}")
            return False
            
    def get_conversation_summary(self):
        """Get a summary of the conversation"""
        if not self.conversation:
            return "No conversation available"
            
        turns = len(self.conversation.turns)
        rounds = turns // 2
        
        return {
            "total_turns": turns,
            "total_rounds": rounds,
            "dummy_name": self.dummy.name if self.dummy else "Unknown",
            "scenario": self.conversation.scenario,
            "last_ai_message": self.conversation.turns[-2].message if turns >= 2 else "N/A",
            "last_student_message": self.conversation.turns[-1].message if turns >= 1 else "N/A"
        }
        
    async def start_new_random_conversation(self):
        """Start a new conversation with a random dummy"""
        import json
        
        try:
            with open("data/ai_dummies.json", 'r') as f:
                dummies_data = json.load(f)
            
            # Select a new random dummy
            dummy_data = random.choice(dummies_data)
            new_dummy = AIDummy(**dummy_data)
            
            print(f"\n🎲 Starting new conversation with: {new_dummy.name}")
            
            # Start new conversation with 3 rounds
            await self.start_conversation(new_dummy, num_rounds=3)
            
        except Exception as e:
            print(f"❌ Error starting new conversation: {e}")
        
    async def run_interactive_test(self, dummy: AIDummy, max_rounds: int = 8):
        """Run an interactive test session"""
        
        # Start with a few rounds
        initial_rounds = 3
        await self.start_conversation(dummy, num_rounds=initial_rounds)
        
        print(f"\n🎮 Interactive Test Session")
        print("=" * 40)
        print("Commands:")
        print("  [Enter] - Add 1 more round")
        print("  'c' + [Enter] - Add 3 more rounds") 
        print("  'e' + [Enter] - Check for natural ending")
        print("  's' + [Enter] - Show conversation summary")
        print("  'n' + [Enter] - Start new conversation with random dummy")
        print("  'q' + [Enter] - Quit")
        print("=" * 40)
        
        while True:
            try:
                command = input("\n⏸️  Enter command (or just Enter for +1 round): ").strip().lower()
                
                if command == 'q':
                    print("👋 Ending test session")
                    break
                elif command == 'e':
                    should_end = await self.check_natural_ending()
                    if should_end:
                        print("✅ Conversation should end naturally!")
                    else:
                        print("🔄 Conversation should continue")
                elif command == 's':
                    summary = self.get_conversation_summary()
                    print(f"\n📊 Summary:")
                    for key, value in summary.items():
                        print(f"   • {key}: {value}")
                elif command == 'n':
                    # Start new conversation with random dummy
                    await self.start_new_random_conversation()
                elif command == 'c':
                    await self.continue_conversation(3)
                else:
                    # Default: add 1 round
                    await self.continue_conversation(1)
                    
                # Check if we've hit max rounds
                current_rounds = len(self.conversation.turns) // 2
                if current_rounds >= max_rounds:
                    print(f"\n⚠️  Reached maximum rounds ({max_rounds})")
                    break
                    
            except KeyboardInterrupt:
                print("\n👋 Interrupted by user")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                
        # Final summary
        summary = self.get_conversation_summary()
        print(f"\n🏁 Final Summary:")
        print(f"   • Total rounds: {summary['total_rounds']}")
        print(f"   • Total turns: {summary['total_turns']}")
        print("=" * 60)
        
    async def run_auto_mode(self, max_rounds: int = 15):
        """Run auto mode - continuously start new conversations with random dummies"""
        print(f"\n🤖 AUTO MODE ACTIVATED")
        print(f"📊 Max rounds per conversation: {max_rounds}")
        print("=" * 60)
        print("Press Ctrl+C to stop")
        print("=" * 60)
        
        conversation_count = 0
        total_turns = 0
        
        try:
            while True:
                conversation_count += 1
                
                # Load dummies for each conversation
                try:
                    with open("data/ai_dummies.json", 'r') as f:
                        dummies_data = json.load(f)
                    
                    # Select a random dummy
                    dummy_data = random.choice(dummies_data)
                    dummy = AIDummy(**dummy_data)
                    
                    print(f"\n🎲 Conversation #{conversation_count}: {dummy.name}")
                    print(f"📊 Character: {dummy.age}-year-old {dummy.major} student")
                    
                    # Start conversation with auto-ending
                    await self.start_conversation(dummy, num_rounds=max_rounds)
                    
                    # Count turns
                    turns = len(self.conversation.turns)
                    total_turns += turns
                    
                    # Show conversation summary
                    summary = self.get_conversation_summary()
                    print(f"\n📊 Conversation #{conversation_count} Summary:")
                    print(f"   • Rounds: {summary['total_rounds']}")
                    print(f"   • Turns: {summary['total_turns']}")
                    print(f"   • Ended naturally: {'Yes' if turns < (max_rounds * 2 + 1) else 'No (hit max rounds)'}")
                    
                    # Show overall stats
                    avg_turns = total_turns / conversation_count
                    print(f"\n📈 Overall Stats:")
                    print(f"   • Total conversations: {conversation_count}")
                    print(f"   • Average turns per conversation: {avg_turns:.1f}")
                    print(f"   • Total turns: {total_turns}")
                    
                    print("\n" + "=" * 60)
                    
                    # Wait for user input to continue
                    input("⏸️  Press Enter for next conversation (Ctrl+C to stop)...")
                    
                except KeyboardInterrupt:
                    print(f"\n👋 Auto mode stopped by user")
                    break
                except Exception as e:
                    print(f"❌ Error in conversation #{conversation_count}: {e}")
                    continue
                    
        except KeyboardInterrupt:
            print(f"\n👋 Auto mode stopped")
        
        # Final statistics
        print(f"\n🏁 Final Auto Mode Statistics:")
        print(f"   • Total conversations: {conversation_count}")
        print(f"   • Total turns: {total_turns}")
        if conversation_count > 0:
            print(f"   • Average turns per conversation: {total_turns/conversation_count:.1f}")
        print("=" * 60)

async def main():
    """Main function to run the conversation mock"""
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Simple Conversation Mock - Test conversation flow with real modules')
    parser.add_argument('--auto', action='store_true', help='Run in auto mode - continuously test conversations with random dummies')
    parser.add_argument('--max-rounds', type=int, default=15, help='Maximum rounds per conversation (default: 15)')
    args = parser.parse_args()
    
    # Load dummies for testing
    try:
        with open("data/ai_dummies.json", 'r') as f:
            dummies_data = json.load(f)
    except FileNotFoundError:
        print("❌ Could not find data/ai_dummies.json")
        return
    
    # Create conversation mock
    mock = SimpleConversationMock()
    
    if args.auto:
        # Auto mode - continuously run conversations
        await mock.run_auto_mode(max_rounds=args.max_rounds)
    else:
        # Interactive mode - single conversation
        dummy_data = random.choice(dummies_data)
        dummy = AIDummy(**dummy_data)
        
        print(f"🎲 Randomly selected: {dummy.name}")
        await mock.run_interactive_test(dummy, max_rounds=args.max_rounds)

if __name__ == "__main__":
    print("🧪 Simple Conversation Mock - Using REAL Conversation Modules")
    print("=" * 60)
    print("This script uses the actual conversation simulator and models")
    print("to provide authentic conversation testing.")
    print("")
    print("Usage:")
    print("  python simple_conversation_mock.py           # Interactive mode")
    print("  python simple_conversation_mock.py --auto    # Auto mode")
    print("  python simple_conversation_mock.py --auto --max-rounds 20  # Auto mode with custom max rounds")
    print("=" * 60)
    
    asyncio.run(main())