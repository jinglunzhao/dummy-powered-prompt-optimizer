#!/usr/bin/env python3
"""
Quick Conversation Length Test

A faster version of the conversation length experiment that tests just 3 and 5 rounds
to quickly validate the personality evolution system.
"""

import asyncio
import json
import os
from datetime import datetime
from typing import List, Dict, Any
from models import AIDummy, PersonalityProfile, SocialAnxietyProfile
from prompt_optimizer import PromptOptimizer, OptimizedPrompt
from config import Config

class QuickConversationTest:
    """Quick test of conversation length effects on personality evolution"""
    
    def __init__(self):
        self.optimizer = PromptOptimizer()
        self.results = []
        self.experiment_id = f"quick_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        print(f"⚡ Quick Conversation Test Initialized")
        print(f"📋 Test ID: {self.experiment_id}")
    
    async def run_test(self):
        """Run the quick conversation test"""
        print("🚀 Starting Quick Conversation Test...")
        print("=" * 50)
        
        # Test just 3 and 5 rounds for speed
        conversation_lengths = [3, 5]
        
        # Create a test dummy
        test_dummy = self._create_test_dummy()
        
        # Create a test prompt
        test_prompt = self._create_test_prompt()
        
        print(f"📝 Test Dummy: {test_dummy.name}")
        print(f"🤖 Test Prompt: {test_prompt.name}")
        print(f"📊 Testing lengths: {conversation_lengths} rounds")
        print()
        
        # Test each conversation length
        for length in conversation_lengths:
            print(f"🔄 Testing {length} rounds...")
            
            try:
                # Reset dummy personality for fair comparison
                test_dummy.start_new_prompt_test(
                    self.experiment_id, 
                    test_prompt.id, 
                    f"{test_prompt.name}_{length}r"
                )
                
                # Run the test
                result = await self.optimizer.test_prompt_with_dummy_async(
                    prompt=test_prompt,
                    dummy=test_dummy,
                    num_rounds=length
                )
                
                # Collect results
                experiment_result = {
                    'conversation_length': length,
                    'dummy_name': test_dummy.name,
                    'prompt_name': test_prompt.name,
                    'pre_score': result.pre_score,
                    'post_score': result.post_score,
                    'improvement': result.improvement,
                    'conversation_id': getattr(result, 'conversation_id', 'unknown'),
                    'timestamp': datetime.now().isoformat(),
                    'evolution_stages': len(test_dummy.personality_evolution.conversation_profile.evolution_stages) if test_dummy.personality_evolution else 0,
                    'personality_evolution_working': test_dummy.personality_evolution is not None
                }
                
                self.results.append(experiment_result)
                
                print(f"   ✅ {length} rounds: {result.improvement:.3f} improvement")
                
            except Exception as e:
                print(f"   ❌ {length} rounds failed: {e}")
                continue
        
        # Save results
        self._save_results()
        
        # Print summary
        self._print_summary()
        
        return self.results
    
    def _create_test_dummy(self) -> AIDummy:
        """Create a test dummy for the experiment"""
        return AIDummy(
            name='QuickTestStudent',
            age=19,
            gender='female',
            major='Computer Science',
            university='Test University',
            student_type='undergraduate',
            personality=PersonalityProfile(
                extraversion=3,
                agreeableness=8,
                conscientiousness=7,
                neuroticism=8,
                openness=5
            ),
            social_anxiety=SocialAnxietyProfile(
                anxiety_level=8,
                communication_style='avoidant',
                triggers=['crowded rooms', 'public speaking', 'group work'],
                social_comfort=2
            ),
            fears=['being judged', 'saying wrong things', 'looking stupid'],
            challenges=['asking questions', 'joining discussions', 'making friends'],
            behaviors=['staying quiet', 'avoiding eye contact', 'sitting alone'],
            goals=['build confidence', 'participate more', 'make connections']
        )
    
    def _create_test_prompt(self) -> OptimizedPrompt:
        """Create a test prompt for the experiment"""
        return OptimizedPrompt(
            id='quick_test_prompt',
            name='G0Q00',  # Generation 0, Quick test
            prompt_text="""You are an empathetic social skills coach helping a college student overcome social anxiety and build confidence.

Your coaching approach:
- Create a safe, supportive environment
- Validate their feelings and experiences
- Provide practical, step-by-step guidance
- Focus on small, achievable goals
- Help them identify and build on their strengths
- Encourage gradual exposure to social situations

Be patient, understanding, and encouraging. Help them see that social skills can be learned and that they're not alone in their struggles.""",
            generation=0,
            components=[],
            performance_metrics={},
            pareto_rank=0,
            created_at=datetime.now(),
            last_tested=None
        )
    
    def _save_results(self):
        """Save test results to file"""
        os.makedirs('data/experiments', exist_ok=True)
        
        experiment_data = {
            'experiment_id': self.experiment_id,
            'experiment_type': 'quick_conversation_test',
            'timestamp': datetime.now().isoformat(),
            'config': {
                'enable_personality_evolution': Config.ENABLE_PERSONALITY_EVOLUTION,
                'test_prompt': 'G0Q00 - Empathetic Social Skills Coach',
                'test_dummy': 'QuickTestStudent',
                'conversation_lengths': [3, 5]
            },
            'results': self.results
        }
        
        filename = f"data/experiments/{self.experiment_id}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(experiment_data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Results saved to: {filename}")
    
    def _print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 50)
        print("📊 QUICK CONVERSATION TEST SUMMARY")
        print("=" * 50)
        
        if not self.results:
            print("❌ No results to summarize")
            return
        
        # Sort by conversation length
        sorted_results = sorted(self.results, key=lambda x: x['conversation_length'])
        
        print(f"📋 Test: {self.experiment_id}")
        print(f"🧪 Test Dummy: {sorted_results[0]['dummy_name']}")
        print(f"🤖 Test Prompt: {sorted_results[0]['prompt_name']}")
        print()
        
        print("📈 Results:")
        print("-" * 30)
        
        for result in sorted_results:
            length = result['conversation_length']
            pre = result['pre_score']
            post = result['post_score']
            improvement = result['improvement']
            evolution_working = result['personality_evolution_working']
            
            print(f"  {length} rounds: {pre:.2f} → {post:.2f} = {improvement:+.3f}")
            print(f"    Evolution: {'✅ Working' if evolution_working else '❌ Not working'}")
        
        # Analysis
        print()
        print("🔍 Analysis:")
        improvements = [r['improvement'] for r in sorted_results]
        if len(improvements) >= 2:
            improvement_difference = improvements[1] - improvements[0]
            print(f"   Improvement from 3→5 rounds: {improvement_difference:+.3f}")
        
        # Check personality evolution
        evolution_working = all(r['personality_evolution_working'] for r in sorted_results)
        print(f"   Personality Evolution: {'✅ Working' if evolution_working else '❌ Issues detected'}")
        
        # Check if longer conversations help
        if len(sorted_results) >= 2:
            longer_better = sorted_results[-1]['improvement'] > sorted_results[0]['improvement']
            print(f"   Longer conversations help: {'✅ Yes' if longer_better else '❌ No'}")
        
        print("=" * 50)

async def main():
    """Run the quick conversation test"""
    test = QuickConversationTest()
    results = await test.run_test()
    return results

if __name__ == "__main__":
    print("⚡ Quick Conversation Length Test")
    print("Fast validation of personality evolution system")
    print()
    
    results = asyncio.run(main())
    
    print("\n🎉 Quick test completed!")
    print("Check results in data/experiments/ and web interface at /evolution")
