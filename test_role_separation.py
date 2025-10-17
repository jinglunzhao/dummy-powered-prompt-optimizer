#!/usr/bin/env python3
"""
Comprehensive Test for Role Separation in Conversations
Tests that AI mentor and student maintain separate roles without confusion
"""

import asyncio
import json
import re
from datetime import datetime
from models import AIDummy
from conversation_simulator import ConversationSimulator
from config import Config

class RoleSeparationTester:
    """Test conversation role separation"""
    
    def __init__(self):
        self.simulator = ConversationSimulator()
        self.test_results = []
    
    async def test_single_conversation(self, dummy: AIDummy, prompt: str, num_rounds: int = 5) -> dict:
        """Test a single conversation for role confusion"""
        print(f"\n{'='*70}")
        print(f"Testing conversation with: {dummy.name}")
        print(f"{'='*70}")
        
        try:
            # Simulate conversation
            conversation = await self.simulator.simulate_conversation_async(
                dummy=dummy,
                num_rounds=num_rounds,
                custom_system_prompt=prompt
            )
            
            # Analyze for role confusion
            issues = []
            for i, turn in enumerate(conversation.turns, 1):
                speaker = turn.speaker
                message = turn.message
                
                # Check for role confusion indicators
                if speaker == "ai":
                    # AI should not include student dialogue
                    if self._contains_student_dialogue(message, dummy.name):
                        issues.append({
                            'turn': i,
                            'speaker': speaker,
                            'issue': 'AI generating student dialogue',
                            'message': message[:200]
                        })
                
                elif speaker == "dummy":
                    # Student should not include mentor dialogue
                    if self._contains_mentor_dialogue(message):
                        issues.append({
                            'turn': i,
                            'speaker': speaker,
                            'issue': 'Student generating mentor dialogue',
                            'message': message[:200]
                        })
            
            # Display results
            if issues:
                print(f"\n❌ FOUND {len(issues)} ROLE CONFUSION ISSUES:")
                for issue in issues:
                    print(f"\n  Turn {issue['turn']} ({issue['speaker']}):")
                    print(f"  Issue: {issue['issue']}")
                    print(f"  Message preview: {issue['message'][:150]}...")
            else:
                print(f"\n✅ NO ROLE CONFUSION DETECTED")
            
            # Print conversation summary
            print(f"\nConversation Summary:")
            print(f"  Total turns: {len(conversation.turns)}")
            print(f"  Duration: {conversation.duration_seconds:.1f}s")
            
            return {
                'dummy_name': dummy.name,
                'total_turns': len(conversation.turns),
                'issues_found': len(issues),
                'issues': issues,
                'passed': len(issues) == 0
            }
            
        except Exception as e:
            print(f"\n❌ ERROR during conversation: {e}")
            return {
                'dummy_name': dummy.name,
                'error': str(e),
                'passed': False
            }
    
    def _contains_student_dialogue(self, message: str, student_name: str) -> bool:
        """Check if AI response contains student dialogue"""
        # Look for patterns like "Student:", "**StudentName:**", etc.
        patterns = [
            rf'\b{re.escape(student_name)}:',  # "Sarah:"
            rf'\*\*{re.escape(student_name)}\*\*:',  # "**Sarah**:"
            r'\bStudent:',  # "Student:"
            r'\*\*Student\*\*:',  # "**Student**:"
            r'\*\*You\*\*:',  # "**You**:" (referring to student)
        ]
        
        for pattern in patterns:
            if re.search(pattern, message, re.IGNORECASE):
                return True
        return False
    
    def _contains_mentor_dialogue(self, message: str) -> bool:
        """Check if student response contains mentor dialogue"""
        # Look for patterns like "Mentor:", "Coach:", "**You:**" (from mentor perspective)
        patterns = [
            r'\bMentor:',
            r'\bCoach:',
            r'\*\*Mentor\*\*:',
            r'\*\*Coach\*\*:',
            # Less common but check anyway
            r'\[.*?(mentor|coach).*?\]:',
        ]
        
        for pattern in patterns:
            if re.search(pattern, message, re.IGNORECASE):
                return True
        return False
    
    async def run_comprehensive_tests(self):
        """Run tests with multiple dummies and scenarios"""
        print("\n" + "="*70)
        print("  COMPREHENSIVE ROLE SEPARATION TEST")
        print("="*70)
        
        # Load test dummies
        with open('data/ai_dummies.json', 'r') as f:
            all_dummies_data = json.load(f)
        
        # Select diverse test dummies (5 different personalities)
        test_dummy_names = ['Sarah Wright', 'Marcus Johnson', 'Emily Chen', 'Jordan Lee', 'Alex Martinez']
        test_dummies = []
        
        for dummy_data in all_dummies_data:
            if dummy_data['name'] in test_dummy_names:
                test_dummies.append(AIDummy.model_validate(dummy_data))
                if len(test_dummies) >= 5:
                    break
        
        # Test prompts
        test_prompts = [
            "You are a helpful peer mentor for college students. Provide supportive, practical advice.",
            "You are an empathetic coach specializing in social skills. Help students overcome their challenges with specific, actionable guidance."
        ]
        
        # Run tests
        all_results = []
        for dummy in test_dummies[:3]:  # Test with 3 dummies
            for i, prompt in enumerate(test_prompts):  # Test with both prompts
                print(f"\n[Test {len(all_results)+1}] {dummy.name} with Prompt {i+1}")
                result = await self.test_single_conversation(dummy, prompt, num_rounds=5)
                all_results.append(result)
                
                # Small delay between tests
                await asyncio.sleep(2)
        
        # Summary
        print("\n" + "="*70)
        print("  TEST SUMMARY")
        print("="*70)
        
        passed = sum(1 for r in all_results if r.get('passed', False))
        total = len(all_results)
        
        print(f"\nResults: {passed}/{total} tests passed")
        
        if passed == total:
            print("\n✅ ALL TESTS PASSED - No role confusion detected!")
        else:
            print(f"\n❌ {total - passed} tests failed - Role confusion detected")
            print("\nFailed tests:")
            for result in all_results:
                if not result.get('passed', False):
                    print(f"  - {result['dummy_name']}: {result.get('issues_found', 0)} issues")
        
        # Save detailed results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = f"data/test_results/role_separation_test_{timestamp}.json"
        with open(results_file, 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'total_tests': total,
                'passed': passed,
                'failed': total - passed,
                'detailed_results': all_results
            }, f, indent=2)
        
        print(f"\nDetailed results saved to: {results_file}")
        
        return passed == total

async def main():
    """Run the comprehensive test"""
    tester = RoleSeparationTester()
    success = await tester.run_comprehensive_tests()
    
    if not success:
        exit(1)

if __name__ == '__main__':
    asyncio.run(main())

