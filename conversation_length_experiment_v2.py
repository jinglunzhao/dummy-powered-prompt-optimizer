#!/usr/bin/env python3
"""
Controlled Experiment: Conversation Length vs Assessment Scores (Continuous Version)
================================================================================

This script tests whether longer conversations lead to better assessment scores
by running ONE continuous conversation per dummy and taking assessments at 
different conversation milestones (5, 10, 15, 20 rounds).

This approach is more realistic as it simulates actual coaching sessions where
progress is measured over time within the same conversation.
"""

import json
import os
import asyncio
import argparse
import aiohttp
from datetime import datetime
from typing import List, Dict, Any, Tuple
from models import AIDummy, Conversation, ConversationTurn
from conversation_simulator import ConversationSimulator
from assessment_system import AssessmentSystem
from config import Config

class ContinuousConversationExperiment:
    """Experiment to test conversation length impact using continuous conversations"""
    
    def __init__(self):
        self.assessment_system = AssessmentSystem()
        self.conversation_simulator = ConversationSimulator()
        
    async def run_experiment(self, 
                           num_dummies: int = 5,
                           max_rounds: int = 20,
                           assessment_milestones: List[int] = None,
                           base_prompt: str = None,
                           save_conversation_details: bool = False) -> Dict[str, Any]:
        """Run the continuous conversation experiment"""
        
        if assessment_milestones is None:
            assessment_milestones = [5, 10, 15, 20]
        
        if base_prompt is None:
            base_prompt = "You are a helpful peer mentor for college students. Be supportive and provide practical advice."
        
        print(f"🧪 Starting Continuous Conversation Length Experiment")
        print(f"📊 Configuration:")
        print(f"   • {num_dummies} dummies (same batch for all tests)")
        print(f"   • Max conversation rounds: {max_rounds}")
        print(f"   • Assessment milestones: {assessment_milestones}")
        print(f"   • Save conversation details: {save_conversation_details}")
        print(f"   • Base prompt: {base_prompt[:50]}...")
        print()
        
        # Load and select dummies (same batch for all tests)
        dummies = self._load_dummies(num_dummies)
        print(f"✅ Selected {len(dummies)} dummies for consistent testing")
        for i, dummy in enumerate(dummies):
            print(f"   {i+1}. {dummy.name} ({dummy.major})")
        print()
        
        # Run continuous conversation experiments in parallel
        print(f"🚀 Running {len(dummies)} dummy tests in parallel...")
        
        # Create tasks for all dummy tests
        tasks = []
        for i, dummy in enumerate(dummies):
            task = self._test_continuous_conversation_parallel(
                dummy, max_rounds, assessment_milestones, base_prompt, i+1, len(dummies), save_conversation_details
            )
            tasks.append(task)
        
        # Run all dummy tests in parallel
        results = await asyncio.gather(*tasks)
        
        print(f"✅ All {len(dummies)} dummy tests completed in parallel!")
        
        # Analyze results across all dummies
        analysis = self._analyze_continuous_results(results, assessment_milestones)
        
        # Save results
        experiment_data = {
            "experiment_info": {
                "timestamp": datetime.now().isoformat(),
                "experiment_type": "continuous_conversation",
                "num_dummies": num_dummies,
                "max_rounds": max_rounds,
                "assessment_milestones": assessment_milestones,
                "save_conversation_details": save_conversation_details,
                "base_prompt": base_prompt,
                "dummy_names": [d.name for d in dummies]
            },
            "results": results,
            "analysis": analysis
        }
        
        # Save to file
        os.makedirs("data/experiments", exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"data/experiments/continuous_conversation_exp_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(experiment_data, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"💾 Results saved to: {filename}")
        
        return experiment_data
    
    def _load_dummies(self, num_dummies: int) -> List[AIDummy]:
        """Load and select dummies for consistent testing"""
        
        with open("data/ai_dummies.json", 'r', encoding='utf-8') as f:
            all_dummies_data = json.load(f)
        
        # Select first N dummies for consistency
        selected_dummies = []
        for dummy_data in all_dummies_data[:num_dummies]:
            try:
                dummy = AIDummy(**dummy_data)
                selected_dummies.append(dummy)
            except Exception as e:
                print(f"⚠️  Error loading dummy: {e}")
                continue
        
        return selected_dummies
    
    async def _test_continuous_conversation_parallel(self, 
                                                   dummy: AIDummy, 
                                                   max_rounds: int,
                                                   assessment_milestones: List[int],
                                                   base_prompt: str,
                                                   dummy_num: int,
                                                   total_dummies: int,
                                                   save_conversation_details: bool = False) -> Dict[str, Any]:
        """Test one dummy with continuous conversation and milestone assessments (parallel version)"""
        
        print(f"   [{dummy_num}/{total_dummies}] Starting continuous conversation for {dummy.name}...")
        
        # Generate initial pre-assessment
        pre_assessment = self.assessment_system.generate_pre_assessment(dummy)
        print(f"   [{dummy_num}/{total_dummies}] 📊 Pre-assessment: {pre_assessment.average_score:.2f}")
        
        # Create conversation
        conversation = Conversation(
            dummy_id=dummy.id,
            scenario="Social skills coaching session",
            system_prompt=base_prompt,
            turns=[]
        )
        
        # Generate initial message
        print(f"   [{dummy_num}/{total_dummies}] Starting conversation", end="", flush=True)
        initial_message = await self._generate_character_driven_opening(dummy)
        conversation.add_turn("dummy", initial_message, {
            "character_context": self._get_character_context(dummy)
        })
        print(" ✓", flush=True)
        
        # Track milestone results
        milestone_results = []
        current_milestone_idx = 0
        
        # Run conversation rounds up to max_rounds
        for round_num in range(max_rounds):
            # AI response
            print(".", end="", flush=True)
            ai_response = await self._generate_ai_response_async(conversation, base_prompt, dummy)
            conversation.add_turn("ai", ai_response, {"round": round_num + 1})
            
            # Dummy response
            print(".", end="", flush=True)
            dummy_response = await self._generate_character_response_async(conversation, dummy, round_num + 1)
            conversation.add_turn("dummy", dummy_response, {"round": round_num + 1})
            
            # Check if we've reached a milestone
            current_rounds = round_num + 1
            if (current_milestone_idx < len(assessment_milestones) and 
                current_rounds == assessment_milestones[current_milestone_idx]):
                
                print(f" [M{dummy_num}:{current_rounds}]", end="", flush=True)
                
                # Generate post-assessment at this milestone
                milestone_assessment = self.assessment_system.generate_post_assessment(dummy, pre_assessment)
                improvement = milestone_assessment.average_score - pre_assessment.average_score
                
                milestone_results.append({
                    "milestone_rounds": current_rounds,
                    "pre_score": pre_assessment.average_score,
                    "milestone_score": milestone_assessment.average_score,
                    "improvement": improvement,
                    "conversation_turns": len(conversation.turns),
                    "timestamp": datetime.now().isoformat()
                })
                
                print(f" +{improvement:.3f}", end="", flush=True)
                current_milestone_idx += 1
        
        print()  # New line after conversation progress
        
        # End conversation
        conversation.end_time = datetime.now()
        conversation.duration_seconds = (conversation.end_time - conversation.start_time).total_seconds()
        
        # Final post-assessment
        final_assessment = self.assessment_system.generate_post_assessment(dummy, pre_assessment)
        final_improvement = final_assessment.average_score - pre_assessment.average_score
        
        print(f"   [{dummy_num}/{total_dummies}] 📊 Final assessment: {final_assessment.average_score:.2f} (+{final_improvement:.3f})")
        print(f"   [{dummy_num}/{total_dummies}] ⏱️  Total duration: {conversation.duration_seconds:.1f}s")
        
        result = {
            "dummy_name": dummy.name,
            "dummy_id": dummy.id,
            "pre_assessment_score": pre_assessment.average_score,
            "final_assessment_score": final_assessment.average_score,
            "final_improvement": final_improvement,
            "total_conversation_turns": len(conversation.turns),
            "total_duration_seconds": conversation.duration_seconds,
            "milestone_results": milestone_results,
            "conversation": {
                "scenario": conversation.scenario,
                "system_prompt": conversation.system_prompt,
                "start_time": conversation.start_time.isoformat(),
                "end_time": conversation.end_time.isoformat(),
                "total_turns": len(conversation.turns)
            }
        }
        
        # Add conversation details if requested
        if save_conversation_details:
            result["conversation_details"] = {
                "turns": [
                    {
                        "turn_number": i + 1,
                        "speaker": turn.speaker,
                        "message": turn.message,
                        "timestamp": turn.timestamp.isoformat() if turn.timestamp else None,
                        "metadata": turn.metadata
                    }
                    for i, turn in enumerate(conversation.turns)
                ],
                "pre_assessment": {
                    "dummy_id": pre_assessment.dummy_id,
                    "timestamp": pre_assessment.timestamp.isoformat(),
                    "total_score": pre_assessment.total_score,
                    "average_score": pre_assessment.average_score,
                    "improvement_areas": pre_assessment.improvement_areas,
                    "responses": [
                        {
                            "question": response.question,
                            "score": response.score,
                            "confidence": response.confidence,
                            "notes": response.notes
                        }
                        for response in pre_assessment.responses
                    ]
                },
                "final_assessment": {
                    "dummy_id": final_assessment.dummy_id,
                    "timestamp": final_assessment.timestamp.isoformat(),
                    "total_score": final_assessment.total_score,
                    "average_score": final_assessment.average_score,
                    "improvement_areas": final_assessment.improvement_areas,
                    "responses": [
                        {
                            "question": response.question,
                            "score": response.score,
                            "confidence": response.confidence,
                            "notes": response.notes
                        }
                        for response in final_assessment.responses
                    ]
                }
            }
        
        return result
    
    def _analyze_continuous_results(self, 
                                  results: List[Dict], 
                                  assessment_milestones: List[int]) -> Dict[str, Any]:
        """Analyze the continuous conversation results"""
        
        print("📊 Analysis Results:")
        print("=" * 60)
        
        # Group milestone results by round count
        milestone_analysis = {}
        for milestone in assessment_milestones:
            milestone_analysis[milestone] = {
                "improvements": [],
                "avg_improvement": 0,
                "dummy_count": 0
            }
        
        # Collect data from all dummies
        for result in results:
            for milestone_result in result["milestone_results"]:
                rounds = milestone_result["milestone_rounds"]
                improvement = milestone_result["improvement"]
                milestone_analysis[rounds]["improvements"].append(improvement)
        
        # Calculate averages for each milestone
        for milestone, data in milestone_analysis.items():
            if data["improvements"]:
                data["avg_improvement"] = sum(data["improvements"]) / len(data["improvements"])
                data["dummy_count"] = len(data["improvements"])
        
        # Display results
        print("Continuous Conversation Milestone Analysis:")
        print("-" * 50)
        for milestone in assessment_milestones:
            data = milestone_analysis[milestone]
            if data["improvements"]:
                avg_improvement = data["avg_improvement"]
                print(f"   {milestone:2d} rounds: +{avg_improvement:.3f} points (n={data['dummy_count']})")
        
        # Calculate trends
        improvements = [milestone_analysis[m]["avg_improvement"] for m in assessment_milestones 
                       if milestone_analysis[m]["improvements"]]
        
        if len(improvements) >= 2:
            trend = "increasing" if improvements[-1] > improvements[0] else "decreasing"
            total_change = improvements[-1] - improvements[0]
            
            print(f"\n📈 Overall trend: {trend}")
            print(f"📊 Total change: {total_change:+.3f} points")
            
            # Find best milestone
            best_milestone = max(milestone_analysis.keys(), 
                               key=lambda x: milestone_analysis[x]["avg_improvement"])
            best_improvement = milestone_analysis[best_milestone]["avg_improvement"]
            print(f"🏆 Best milestone: {best_milestone} rounds (+{best_improvement:.3f} points)")
        
        return {
            "milestone_analysis": milestone_analysis,
            "assessment_milestones": assessment_milestones,
            "improvements": improvements,
            "trend": trend if len(improvements) >= 2 else "insufficient_data",
            "total_change": total_change if len(improvements) >= 2 else 0,
            "best_milestone": best_milestone if len(improvements) >= 2 else None,
            "best_improvement": best_improvement if len(improvements) >= 2 else 0
        }
    
    # Helper methods (copied from ConversationSimulator)
    async def _generate_character_driven_opening(self, dummy: AIDummy) -> str:
        """Generate opening message based on dummy's actual concerns"""
        
        character_context = self._get_character_context(dummy)
        
        prompt = f"""You are {dummy.name}, a {dummy.age}-year-old {dummy.student_type} at {dummy.university}.

{character_context}

You're meeting with a social skills coach. Based on your actual personality, fears, goals, and challenges, start the conversation naturally. 

Be authentic to your character:
- Express your real concerns and fears
- Mention specific goals you want to work on
- Show your personality traits naturally
- Be honest about your challenges

Start with a natural opening message (1-2 sentences)."""

        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.deepseek.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.conversation_simulator.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "deepseek-chat",
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 80,
                    "temperature": 0.8
                }
            ) as response:
                result = await response.json()
                return result['choices'][0]['message']['content'].strip()
    
    async def _generate_ai_response_async(self, conversation: Conversation, system_prompt: str, dummy: AIDummy) -> str:
        """Generate AI response using the custom system prompt"""
        
        # Prepare conversation history
        messages = [
            {"role": "system", "content": system_prompt + "\n\nIMPORTANT: Keep your response concise and under 150 words. Focus on being helpful and encouraging without being overly long."},
            {"role": "user", "content": f"Student Profile: {dummy.get_character_summary()}"}
        ]
        
        # Add conversation history
        for turn in conversation.turns[-6:]:  # Last 6 turns for context
            role = "assistant" if turn.speaker == "ai" else "user"
            messages.append({"role": role, "content": turn.message})
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.deepseek.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.conversation_simulator.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "deepseek-chat",
                    "messages": messages,
                    "max_tokens": 150,
                    "temperature": 0.7
                }
            ) as response:
                result = await response.json()
                return result['choices'][0]['message']['content'].strip()
    
    async def _generate_character_response_async(self, conversation: Conversation, dummy: AIDummy, round_num: int) -> str:
        """Generate character-authentic response based on dummy's profile"""
        
        # Get the last AI message
        last_ai_message = None
        for turn in reversed(conversation.turns):
            if turn.speaker == "ai":
                last_ai_message = turn.message
                break
        
        if not last_ai_message:
            return "Thank you for your help. I'm not sure what to say next."
        
        character_context = self._get_character_context(dummy)
        
        prompt = f"""You are {dummy.name}, responding authentically to your social skills coach.

{character_context}

Your coach just said: "{last_ai_message}"

Respond naturally as your character would:
- Stay true to your personality traits and anxiety level
- Express your real fears, goals, and challenges
- Show your communication style
- Be honest about your feelings and thoughts

Keep your response conversational and authentic (1-2 sentences). Be concise and natural."""

        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.deepseek.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.conversation_simulator.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "deepseek-chat",
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 80,
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

def main():
    """Main function to run the continuous experiment"""
    parser = argparse.ArgumentParser(description="Test conversation length impact using continuous conversations")
    parser.add_argument("--dummies", type=int, default=3, help="Number of dummies to test (default: 3)")
    parser.add_argument("--max-rounds", type=int, default=20, help="Maximum conversation rounds (default: 20)")
    parser.add_argument("--milestones", type=str, default="5,10,15,20", help="Assessment milestones (comma-separated, default: 5,10,15,20)")
    parser.add_argument("--prompt", type=str, default=None, help="Custom system prompt to test")
    parser.add_argument("--save-details", action="store_true", help="Save full conversation details in JSON output (makes files larger)")
    
    args = parser.parse_args()
    
    # Parse milestones
    try:
        assessment_milestones = [int(m.strip()) for m in args.milestones.split(",")]
        # Validate milestones are within max_rounds
        assessment_milestones = [m for m in assessment_milestones if m <= args.max_rounds]
    except ValueError:
        print("❌ Error: Invalid milestone sequence. Use comma-separated integers (e.g., 5,10,15,20)")
        return
    
    # Run experiment
    experiment = ContinuousConversationExperiment()
    
    async def run():
        try:
            await experiment.run_experiment(
                num_dummies=args.dummies,
                max_rounds=args.max_rounds,
                assessment_milestones=assessment_milestones,
                base_prompt=args.prompt,
                save_conversation_details=args.save_details
            )
            print("\n✅ Continuous conversation experiment completed successfully!")
        except Exception as e:
            print(f"\n❌ Experiment failed: {e}")
            import traceback
            traceback.print_exc()
    
    asyncio.run(run())

if __name__ == "__main__":
    main()
