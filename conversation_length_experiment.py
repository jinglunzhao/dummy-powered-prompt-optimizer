#!/usr/bin/env python3
"""
Conversation Length Experiment

Tests how different conversation lengths affect personality evolution and assessment scores.
This is a focused experiment to validate the personality evolution system before scaling up.
"""

import asyncio
import json
import os
from datetime import datetime
from typing import List, Dict, Any
from models import AIDummy, PersonalityProfile, SocialAnxietyProfile
from prompt_optimizer import PromptOptimizer, OptimizedPrompt
from config import Config

class ConversationLengthExperiment:
    """Experiment to test conversation length effects on personality evolution"""
    
    def __init__(self):
        self.optimizer = PromptOptimizer()
        self.results = []
        self.experiment_id = f"conversation_length_exp_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        print(f"🧪 Conversation Length Experiment Initialized")
        print(f"📋 Experiment ID: {self.experiment_id}")
    
    async def run_experiment(self):
        """Run the conversation length experiment"""
        print("🚀 Starting Conversation Length Experiment...")
        print("=" * 60)
        
        # Test different conversation lengths
        conversation_lengths = [3, 5, 7, 10]
        
        # Create a test dummy
        test_dummy = self._create_test_dummy()
        
        # Create a test prompt
        test_prompt = self._create_test_prompt()
        
        print(f"📝 Test Dummy: {test_dummy.name}")
        print(f"🤖 Test Prompt: {test_prompt.name}")
        print(f"📊 Testing conversation lengths: {conversation_lengths}")
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
                    'evolution_stages': len(test_dummy.personality_evolution.conversation_profile.evolution_stages) if test_dummy.personality_evolution else 0
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
            name='LengthTestStudent',
            age=20,
            gender='non-binary',
            major='Psychology',
            university='Test University',
            student_type='undergraduate',
            personality=PersonalityProfile(
                extraversion=4,
                agreeableness=7,
                conscientiousness=6,
                neuroticism=7,
                openness=6
            ),
            social_anxiety=SocialAnxietyProfile(
                anxiety_level=7,
                communication_style='hesitant',
                triggers=['large groups', 'presentations', 'new people'],
                social_comfort=3
            ),
            fears=['being ignored', 'saying wrong things', 'looking foolish'],
            challenges=['joining group discussions', 'asking questions in class', 'making small talk'],
            behaviors=['sitting in back', 'avoiding eye contact', 'leaving early'],
            goals=['participate more', 'build confidence', 'make friends']
        )
    
    def _create_test_prompt(self) -> OptimizedPrompt:
        """Create a test prompt for the experiment"""
        return OptimizedPrompt(
            id='conversation_length_test_prompt',
            name='G0L00',  # Generation 0, Length test
            prompt_text="""You are a supportive social skills coach helping a college student build confidence and improve their social interactions. 

Your approach:
- Listen actively and validate their feelings
- Break down social challenges into manageable steps
- Provide specific, actionable advice
- Encourage gradual exposure to social situations
- Help them identify their strengths and build on them
- Create a safe, non-judgmental space for them to share

Focus on helping them understand that social skills can be learned and improved with practice. Be patient, encouraging, and supportive throughout the conversation.""",
            generation=0,
            components=[],  # Empty components list for test prompt
            performance_metrics={},
            pareto_rank=0,
            created_at=datetime.now(),
            last_tested=None
        )
    
    def _save_results(self):
        """Save experiment results to file"""
        os.makedirs('data/experiments', exist_ok=True)
        
        experiment_data = {
            'experiment_id': self.experiment_id,
            'experiment_type': 'conversation_length',
            'timestamp': datetime.now().isoformat(),
            'config': {
                'enable_personality_evolution': Config.ENABLE_PERSONALITY_EVOLUTION,
                'test_prompt': 'G0L00 - Social Skills Coach',
                'test_dummy': 'LengthTestStudent'
            },
            'results': self.results
        }
        
        filename = f"data/experiments/{self.experiment_id}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(experiment_data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Results saved to: {filename}")
    
    def _print_summary(self):
        """Print experiment summary"""
        print("\n" + "=" * 60)
        print("📊 CONVERSATION LENGTH EXPERIMENT SUMMARY")
        print("=" * 60)
        
        if not self.results:
            print("❌ No results to summarize")
            return
        
        # Sort by conversation length
        sorted_results = sorted(self.results, key=lambda x: x['conversation_length'])
        
        print(f"📋 Experiment: {self.experiment_id}")
        print(f"🧪 Test Dummy: {sorted_results[0]['dummy_name']}")
        print(f"🤖 Test Prompt: {sorted_results[0]['prompt_name']}")
        print()
        
        print("📈 Results by Conversation Length:")
        print("-" * 50)
        
        for result in sorted_results:
            length = result['conversation_length']
            pre = result['pre_score']
            post = result['post_score']
            improvement = result['improvement']
            evolution_stages = result['evolution_stages']
            
            print(f"  {length:2d} rounds: {pre:.2f} → {post:.2f} = {improvement:+.3f} ({evolution_stages} evolution stages)")
        
        # Find best performing length
        best_result = max(sorted_results, key=lambda x: x['improvement'])
        print()
        print(f"🏆 Best performing length: {best_result['conversation_length']} rounds")
        print(f"   Improvement: {best_result['improvement']:.3f}")
        print(f"   Evolution stages: {best_result['evolution_stages']}")
        
        # Analysis
        print()
        print("🔍 Analysis:")
        improvements = [r['improvement'] for r in sorted_results]
        avg_improvement = sum(improvements) / len(improvements)
        print(f"   Average improvement: {avg_improvement:.3f}")
        print(f"   Improvement range: {min(improvements):.3f} to {max(improvements):.3f}")
        
        # Check if personality evolution is working
        total_evolution_stages = sum(r['evolution_stages'] for r in sorted_results)
        print(f"   Total evolution stages created: {total_evolution_stages}")
        
        if total_evolution_stages > 0:
            print("   ✅ Personality evolution is working!")
        else:
            print("   ⚠️  No personality evolution stages created")
        
        print("=" * 60)

async def main():
    """Run the conversation length experiment"""
    experiment = ConversationLengthExperiment()
    results = await experiment.run_experiment()
    return results

if __name__ == "__main__":
    print("🧪 Conversation Length Experiment")
    print("Testing how conversation length affects personality evolution")
    print()
    
    results = asyncio.run(main())
    
    print("\n🎉 Experiment completed!")
    print("Check the results in the data/experiments/ directory")
    print("You can also view the evolution data in the web interface at /evolution")
