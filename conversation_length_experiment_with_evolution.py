#!/usr/bin/env python3
"""
Conversation Length Experiment WITH Personality Evolution
========================================================

Enhanced version of conversation length experiment that includes personality evolution
tracking. This shows how dummies' personalities evolve during conversations and how
this affects their assessment scores.
"""

import json
import os
import asyncio
import argparse
import aiohttp
from datetime import datetime
from typing import List, Dict, Any, Tuple, Optional
from models import AIDummy, Conversation, ConversationTurn
from conversation_simulator import ConversationSimulator
from config import Config
from personality_materializer import personality_materializer
from personality_evolution_storage import personality_evolution_storage

# Try to import assessment system, but make it optional
try:
    from assessment_system_llm_based import AssessmentSystemLLMBased as AssessmentSystem
    ASSESSMENT_AVAILABLE = True
except ImportError:
    ASSESSMENT_AVAILABLE = False
    print("⚠️  Assessment system not available. Only conversation-only mode will work.")

class ConversationLengthExperimentWithEvolution:
    """Enhanced conversation length experiment with personality evolution tracking"""
    
    def __init__(self):
        self.assessment_system = AssessmentSystem(api_key=Config.DEEPSEEK_API_KEY) if ASSESSMENT_AVAILABLE else None
        self.conversation_simulator = ConversationSimulator()
        
    async def run_experiment(self, 
                           dummies: List[AIDummy], 
                           max_rounds: int = 10, 
                           milestones: List[int] = [2, 5, 8, 10],
                           base_prompt: str = "You are a helpful peer mentor for college students. Be supportive and provide practical advice.",
                           save_details: bool = True,
                           enable_assessments: bool = True) -> Dict[str, Any]:
        """Run conversation length experiment with personality evolution tracking"""
        
        print(f"🧬 Starting Conversation Length Experiment WITH Personality Evolution")
        print(f"📊 Configuration:")
        print(f"   • {len(dummies)} dummies")
        print(f"   • Max rounds: {max_rounds}")
        print(f"   • Milestones: {milestones}")
        print(f"   • Personality evolution: ENABLED")
        print(f"   • Assessments: {'ENABLED' if enable_assessments else 'DISABLED'}")
        print(f"   • Save details: {save_details}")
        print()
        
        results = []
        
        # Run experiments for all dummies
        tasks = []
        for i, dummy in enumerate(dummies):
            task = self.run_dummy_experiment(dummy, max_rounds, milestones, base_prompt, save_details, enable_assessments)
            tasks.append(task)
        
        print(f"🚀 Running {len(dummies)} dummy experiments in parallel...")
        dummy_results = await asyncio.gather(*tasks)
        
        for i, (dummy, result) in enumerate(zip(dummies, dummy_results)):
            print(f"✅ {dummy.name} completed: {result['final_improvement']:+.3f} improvement")
            results.append(result)
        
        # Create experiment summary
        experiment_data = {
            "experiment_info": {
                "timestamp": datetime.now().isoformat(),
                "experiment_type": "conversation_length_with_evolution",
                "num_dummies": len(dummies),
                "max_rounds": max_rounds,
                "enable_assessments": enable_assessments,
                "assessment_milestones": milestones,
                "save_conversation_details": save_details,
                "base_prompt": base_prompt,
                "personality_evolution_enabled": True,
                "dummy_names": [d.name for d in dummies]
            },
            "results": results
        }
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"data/experiments/continuous_conversation_with_evolution_exp_{timestamp}.json"
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        # Custom JSON encoder for datetime objects
        class DateTimeEncoder(json.JSONEncoder):
            def default(self, obj):
                if isinstance(obj, datetime):
                    return obj.isoformat()
                return super().default(obj)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(experiment_data, f, indent=2, ensure_ascii=False, cls=DateTimeEncoder)
        
        print(f"💾 Results saved to: {filename}")
        
        # Analysis
        self.print_analysis(results)
        
        return experiment_data
    
    async def run_dummy_experiment(self, 
                                 dummy: AIDummy, 
                                 max_rounds: int, 
                                 milestones: List[int],
                                 base_prompt: str,
                                 save_details: bool,
                                 enable_assessments: bool) -> Dict[str, Any]:
        """Run experiment for a single dummy with personality evolution tracking"""
        
        # Initialize personality evolution for this dummy
        if not dummy.personality_evolution:
            dummy.initialize_personality_evolution()
        
        # Start new prompt test (resets personality to original)
        dummy.start_new_prompt_test(
            experiment_id="conversation_length_with_evolution",
            prompt_id="conversation_length_test",
            prompt_name="Conversation Length Test"
        )
        
        print(f"🧪 Testing {dummy.name} with personality evolution tracking...")
        
        # Pre-assessment
        pre_assessment = None
        if enable_assessments and self.assessment_system:
            print(f"   📊 Running pre-assessment...")
            pre_assessment = await self.assessment_system.generate_pre_assessment(dummy)
            print(f"   📊 Pre-assessment: {pre_assessment.average_score:.2f}")
        
        # Start conversation with milestone assessments
        print(f"   💬 Starting conversation (up to {max_rounds} rounds)...")
        conversation, milestone_assessments = await self._simulate_conversation_with_milestones(
            dummy=dummy,
            base_prompt=base_prompt,
            max_rounds=max_rounds,
            milestones=milestones,
            enable_assessments=enable_assessments
        )
        
        # Materialize personality evolution from conversation (only if no milestones were processed)
        # If milestones were processed, personality evolution was already materialized at each milestone
        evolution_stage = None
        if not milestones or max_rounds not in milestones:
            print(f"   🧠 Materializing personality evolution...")
            evolution_stage = await personality_materializer.materialize_personality_from_conversation(
                dummy=dummy,
                conversation=conversation,
                prompt_id="conversation_length_test",
                prompt_name="Conversation Length Test",
                generation=0,
                pre_assessment_score=pre_assessment.average_score if pre_assessment else 0.0,
                post_assessment_score=0.0  # Will be updated after post-assessment
            )
            
            if evolution_stage:
                dummy.add_evolution_stage(evolution_stage)
                personality_evolution_storage.save_personality_evolution(dummy)
                print(f"   ✅ Personality evolution captured: {len(dummy.personality_evolution.conversation_profile.evolution_stages)} stages")
        else:
            print(f"   ✅ Personality evolution already captured at milestones: {len(dummy.personality_evolution.conversation_profile.evolution_stages)} stages")
        
        # Post-assessment
        post_assessment = None
        if enable_assessments and self.assessment_system:
            print(f"   📊 Running post-assessment...")
            post_assessment = await self.assessment_system.generate_post_assessment(dummy, pre_assessment, conversation)
            print(f"   📊 Post-assessment: {post_assessment.average_score:.2f}")
            
            # Update the evolution stage with final assessment
            if evolution_stage:
                # We created a new evolution stage, update it with post-assessment
                evolution_stage.post_assessment_score = post_assessment.average_score
                evolution_stage.improvement_score = post_assessment.average_score - (pre_assessment.average_score if pre_assessment else 0.0)
                personality_evolution_storage.save_personality_evolution(dummy)
            elif dummy.personality_evolution and dummy.personality_evolution.conversation_profile.evolution_stages:
                # We used milestone evolution stages, update the last one with final post-assessment
                last_stage = dummy.personality_evolution.conversation_profile.evolution_stages[-1]
                last_stage.post_assessment_score = post_assessment.average_score
                last_stage.improvement_score = post_assessment.average_score - (pre_assessment.average_score if pre_assessment else 0.0)
                personality_evolution_storage.save_personality_evolution(dummy)
        
        # Use real milestone assessments from conversation simulation
        milestone_results = milestone_assessments if enable_assessments else []
        
        # Update milestone assessments with actual pre-assessment scores
        if milestone_results and pre_assessment:
            for milestone in milestone_results:
                milestone["pre_score"] = pre_assessment.average_score
                milestone["improvement"] = round(milestone["milestone_score"] - pre_assessment.average_score, 3)
        
        # Prepare result
        result = {
            "dummy_name": dummy.name,
            "dummy_id": dummy.id,
            "pre_assessment_score": pre_assessment.average_score if pre_assessment else 2.5,
            "final_assessment_score": post_assessment.average_score if post_assessment else 2.5,
            "final_improvement": (post_assessment.average_score if post_assessment else 2.5) - (pre_assessment.average_score if pre_assessment else 2.5),
            "total_conversation_turns": len(conversation.turns),
            "total_duration_seconds": 120.0,  # Estimated
            "milestone_results": milestone_results,
            "personality_evolution": {
                "enabled": True,
                "evolution_stages": len(dummy.personality_evolution.conversation_profile.evolution_stages) if dummy.personality_evolution else 0,
                "final_anxiety_level": dummy.personality_evolution.conversation_profile.current_social_anxiety_level if dummy.personality_evolution else dummy.social_anxiety.anxiety_level,
                "materialized_fears": len(dummy.personality_evolution.conversation_profile.current_fears) if dummy.personality_evolution else 0,
                "materialized_challenges": len(dummy.personality_evolution.conversation_profile.current_challenges) if dummy.personality_evolution else 0
            }
        }
        
        # Add conversation details if requested
        if save_details:
            result["conversation_details"] = {
                "conversation": conversation.model_dump(),
                "pre_assessment": pre_assessment.model_dump() if pre_assessment else None,
                "post_assessment": post_assessment.model_dump() if post_assessment else None,
                "personality_evolution_timeline": dummy.get_evolution_timeline() if dummy.personality_evolution else []
            }
        
        return result
    
    async def _simulate_conversation_with_milestones(self, 
                                                   dummy: AIDummy, 
                                                   base_prompt: str, 
                                                   max_rounds: int,
                                                   milestones: List[int],
                                                   enable_assessments: bool) -> Tuple[Conversation, List[Dict[str, Any]]]:
        """Simulate conversation with OPTIMIZED flow: continuous conversation + parallel milestone processing"""
        
        print(f"   🚀 Starting OPTIMIZED conversation flow...")
        
        # Phase 1: Run continuous conversation without interruptions
        conversation = await self._run_continuous_conversation(dummy, base_prompt, max_rounds)
        
        # Phase 2: Process milestones in parallel (materialization + assessment)
        milestone_assessments = []
        if enable_assessments and milestones:
            print(f"   🔄 Processing {len(milestones)} milestones in parallel...")
            milestone_assessments = await self._process_milestones_parallel(
                dummy, conversation, milestones
            )
        
        return conversation, milestone_assessments
    
    async def _run_continuous_conversation(self, dummy: AIDummy, base_prompt: str, max_rounds: int) -> Conversation:
        """Run conversation continuously with end detection using the latest conversation simulator"""
        
        print(f"   🔄 Running conversation with end detection (max {max_rounds} rounds)...")
        
        # Use the latest conversation simulator with end detection
        conversation = await self.conversation_simulator.simulate_conversation_async(
            dummy=dummy,
            scenario="Social skills coaching session",
            num_rounds=max_rounds,
            custom_system_prompt=base_prompt
        )
        
        # Update conversation metadata for experiment tracking
        conversation.id = f"conv_{dummy.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        conversation.dummy_id = dummy.id
        conversation.system_prompt = base_prompt
        conversation.scenario = "Social skills coaching session"
        conversation.start_time = datetime.now()
        
        print(f"   ✅ Conversation completed: {len(conversation.turns)} turns")
        
        return conversation
    
    async def _process_milestones_parallel(self, dummy: AIDummy, conversation: Conversation, milestones: List[int]) -> List[Dict[str, Any]]:
        """Process all milestones with progressive assessment scoring"""
        
        # Process milestones sequentially to maintain progressive scoring
        # (Each milestone needs the previous milestone's score for comparison)
        valid_milestone_assessments = []
        previous_score = None  # Start with no previous score (will use initial baseline)
        
        for milestone_round in milestones:
            print(f"   🔄 Processing milestone {milestone_round} with progressive scoring...")
            
            try:
                result = await self._process_single_milestone(
                    dummy, conversation, milestone_round, previous_score
                )
                
                if result:
                    valid_milestone_assessments.append(result)
                    previous_score = result['milestone_score']  # Update for next milestone
                    print(f"   ✅ Milestone {milestone_round} completed: {result['milestone_score']:.2f} (improvement: {result['improvement']:+.3f})")
                else:
                    print(f"   ⚠️  Milestone {milestone_round} returned no result")
                    
            except Exception as e:
                print(f"   ❌ Milestone {milestone_round} failed: {e}")
        
        return valid_milestone_assessments
    
    async def _process_single_milestone(self, dummy: AIDummy, conversation: Conversation, milestone_round: int, previous_milestone_score: float = None) -> Optional[Dict[str, Any]]:
        """Process a single milestone: materialization + assessment"""
        
        print(f"   📊 Processing milestone {milestone_round}...")
        
        # Create conversation up to milestone point
        milestone_conversation = Conversation(
            id=f"conv_{dummy.id}_milestone_{milestone_round}",
            dummy_id=dummy.id,
            system_prompt=conversation.system_prompt,
            scenario=conversation.scenario,
            turns=[turn for turn in conversation.turns if turn.metadata.get("round", 0) <= milestone_round],
            start_time=conversation.start_time
        )
        
        try:
            # Determine the baseline score for comparison
            # Use previous milestone score if available, otherwise use default baseline
            baseline_score = previous_milestone_score if previous_milestone_score is not None else 2.5
            print(f"   📈 Using baseline score: {baseline_score:.2f} ({'previous milestone' if previous_milestone_score else 'initial baseline'})")
            
            # Materialize personality evolution at this milestone
            print(f"   🧠 Materializing personality evolution at milestone {milestone_round}...")
            evolution_stage = await personality_materializer.materialize_personality_from_conversation(
                dummy=dummy,
                conversation=milestone_conversation,
                prompt_id="conversation_length_test",
                prompt_name="Conversation Length Test",
                generation=0,
                pre_assessment_score=baseline_score,  # Use progressive baseline
                post_assessment_score=0.0  # Will be updated after milestone assessment
            )
            
            if evolution_stage:
                dummy.add_evolution_stage(evolution_stage)
                personality_evolution_storage.save_personality_evolution(dummy)
                print(f"   ✅ Personality evolution captured at milestone {milestone_round}")
            
            # Run milestone assessment (using current evolved personality)
            if self.assessment_system:
                from assessment_system_llm_based import Assessment, AssessmentResponse
                
                # Create baseline assessment responses using the progressive baseline
                baseline_responses = []
                for i in range(20):
                    baseline_responses.append(AssessmentResponse(
                        question=f"Previous milestone baseline {i+1}",
                        score=int(round(baseline_score)),  # Convert float to int
                        confidence=8,
                        reasoning=f"Previous milestone baseline score: {baseline_score:.2f}"
                    ))
                
                milestone_pre_assessment = Assessment(
                    dummy_id=dummy.id,
                    assessment_type="previous_milestone" if previous_milestone_score else "initial_baseline",
                    responses=baseline_responses,
                    total_score=baseline_score * 20,
                    average_score=baseline_score,
                    improvement_areas=[]
                )
                
                milestone_assessment = await self.assessment_system.generate_post_assessment(
                    dummy, milestone_pre_assessment, milestone_conversation
                )
                
                # Update evolution stage with milestone assessment score
                if evolution_stage:
                    evolution_stage.post_assessment_score = milestone_assessment.average_score
                    evolution_stage.improvement_score = milestone_assessment.average_score - baseline_score
                    personality_evolution_storage.save_personality_evolution(dummy)
                
                # Calculate improvement from progressive baseline
                improvement = milestone_assessment.average_score - baseline_score
                
                milestone_result = {
                    "milestone_rounds": milestone_round,
                    "pre_score": baseline_score,
                    "milestone_score": round(milestone_assessment.average_score, 2),
                    "improvement": round(improvement, 3),
                    "conversation_turns": len(milestone_conversation.turns),
                    "timestamp": datetime.now().isoformat(),
                    "note": f"Progressive assessment: {milestone_assessment.average_score:.2f} vs {baseline_score:.2f} baseline ({'previous milestone' if previous_milestone_score else 'initial'})",
                    "detailed_assessment": {
                        "dummy_id": milestone_assessment.dummy_id,
                        "timestamp": milestone_assessment.timestamp.isoformat(),
                        "total_score": milestone_assessment.total_score,
                        "average_score": milestone_assessment.average_score,
                        "improvement_areas": milestone_assessment.improvement_areas,
                        "responses": [
                            {
                                "question": response.question,
                                "score": response.score,
                                "confidence": response.confidence,
                                "notes": response.notes
                            }
                            for response in milestone_assessment.responses
                        ]
                    }
                }
                
                return milestone_result
            
        except Exception as e:
            print(f"   ❌ Error processing milestone {milestone_round}: {e}")
            return None
        
        return None
    
    def print_analysis(self, results: List[Dict[str, Any]]):
        """Print analysis of results"""
        print("\n📊 ANALYSIS RESULTS:")
        print("=" * 60)
        
        # Basic stats
        total_improvements = [r["final_improvement"] for r in results]
        avg_improvement = sum(total_improvements) / len(total_improvements)
        best_improvement = max(total_improvements)
        worst_improvement = min(total_improvements)
        
        print(f"📈 Overall Performance:")
        print(f"   • Average improvement: +{avg_improvement:.3f} points")
        print(f"   • Best improvement: +{best_improvement:.3f} points")
        print(f"   • Worst improvement: +{worst_improvement:.3f} points")
        
        # Personality evolution stats
        evolution_enabled_count = sum(1 for r in results if r["personality_evolution"]["enabled"])
        avg_evolution_stages = sum(r["personality_evolution"]["evolution_stages"] for r in results) / len(results)
        avg_final_anxiety = sum(r["personality_evolution"]["final_anxiety_level"] for r in results) / len(results)
        
        print(f"\n🧬 Personality Evolution:")
        print(f"   • Dummies with evolution: {evolution_enabled_count}/{len(results)}")
        print(f"   • Average evolution stages: {avg_evolution_stages:.1f}")
        print(f"   • Average final anxiety level: {avg_final_anxiety:.1f}/10")
        
        # Individual results
        print(f"\n👥 Individual Results:")
        for result in results:
            evolution = result["personality_evolution"]
            print(f"   • {result['dummy_name']}: +{result['final_improvement']:.3f} points")
            print(f"     - Evolution stages: {evolution['evolution_stages']}")
            print(f"     - Final anxiety: {evolution['final_anxiety_level']:.1f}/10")
            print(f"     - Materialized traits: {evolution['materialized_fears']} fears, {evolution['materialized_challenges']} challenges")

async def main():
    """Main function to run the experiment"""
    parser = argparse.ArgumentParser(description="Run conversation length experiment with personality evolution")
    parser.add_argument("--dummies", type=int, default=3, help="Number of dummies to test")
    parser.add_argument("--max-rounds", type=int, default=10, help="Maximum conversation rounds")
    parser.add_argument("--milestones", type=str, default="2,5,8,10", help="Assessment milestones (comma-separated)")
    parser.add_argument("--prompt", type=str, help="Custom system prompt to test")
    parser.add_argument("--save-details", action="store_true", help="Save full conversation details")
    parser.add_argument("--no-assessments", action="store_true", help="Disable assessments")
    
    args = parser.parse_args()
    
    # Parse milestones
    milestones = [int(x.strip()) for x in args.milestones.split(",")]
    
    # Default prompt - improved to address response quality issues and prevent conversation degradation
    base_prompt = args.prompt or """You are a helpful peer mentor for college students. Your role is to provide supportive, practical advice to help students with their social skills and personal challenges.

IMPORTANT GUIDELINES:
- Always maintain your role as a peer mentor/advisor, never act like the student
- Provide detailed, helpful responses (not just "Short answer: ...")
- Give specific, actionable advice with examples
- Be encouraging but realistic
- Keep responses conversational and natural
- Address the student's specific concerns and fears
- Offer concrete next steps they can take

CONVERSATION CONTINUITY:
- This is an ongoing coaching session - NEVER end the conversation
- Do NOT use phrases like "[End of conversation]" or suggest the conversation is over
- Always provide helpful follow-up questions or additional guidance
- Continue supporting the student throughout the entire session
- Each response should encourage further discussion and growth

Remember: You are the advisor helping the student, not the student themselves. Keep the conversation flowing naturally."""
    
    # Load dummies
    dummies_file = "data/ai_dummies.json"
    if os.path.exists(dummies_file):
        with open(dummies_file, 'r', encoding='utf-8') as f:
            all_dummies = json.load(f)
        
        # Select dummies
        selected_dummies = all_dummies[:args.dummies]
        dummies = [AIDummy(**dummy_data) for dummy_data in selected_dummies]
        
        print(f"✅ Loaded {len(dummies)} dummies for testing")
    else:
        print("❌ No dummies file found. Please run dummy generation first.")
        return
    
    # Run experiment
    experiment = ConversationLengthExperimentWithEvolution()
    await experiment.run_experiment(
        dummies=dummies,
        max_rounds=args.max_rounds,
        milestones=milestones,
        base_prompt=base_prompt,
        save_details=args.save_details,
        enable_assessments=not args.no_assessments
    )

if __name__ == "__main__":
    asyncio.run(main())
