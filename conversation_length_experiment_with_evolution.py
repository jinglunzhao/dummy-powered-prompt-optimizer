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
import math
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
from prompts.prompt_loader import prompt_loader

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
                           max_turns: int = 31,  # Default: 31 turns
                           milestone_turns: List[int] = [11, 21, 31],  # Turn numbers for assessments
                           base_prompt: str = None,  # Loaded from YAML in main() - see line 467
                           save_details: bool = True,
                           enable_assessments: bool = True) -> Dict[str, Any]:
        """Run conversation length experiment with personality evolution tracking"""
        
        if base_prompt is None:
            raise ValueError("base_prompt is required. Load from YAML using prompt_loader.get_prompt()")
        
        print(f"🧬 Starting Conversation Length Experiment WITH Personality Evolution")
        print(f"📊 Configuration:")
        print(f"   • {len(dummies)} dummies")
        print(f"   • Max turns: {max_turns}")
        print(f"   • Milestones at turns: {milestone_turns}")
        print(f"   • Personality evolution: ENABLED")
        print(f"   • Assessments: {'ENABLED' if enable_assessments else 'DISABLED'}")
        print(f"   • Save details: {save_details}")
        print()
        
        results = []
        
        # Run experiments for all dummies
        tasks = []
        for i, dummy in enumerate(dummies):
            task = self.run_dummy_experiment(dummy, max_turns, milestone_turns, base_prompt, save_details, enable_assessments)
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
                "max_turns": max_turns,
                "enable_assessments": enable_assessments,
                "assessment_milestone_turns": milestone_turns,
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
                                 max_turns: int, 
                                 milestone_turns: List[int],
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
        print(f"   💬 Starting conversation (up to {max_turns} turns)...")
        conversation, milestone_assessments = await self._simulate_conversation_with_milestones(
            dummy=dummy,
            base_prompt=base_prompt,
            max_turns=max_turns,
            milestone_turns=milestone_turns,
            enable_assessments=enable_assessments,
            pre_assessment=pre_assessment
        )
        
        # Materialize personality evolution from conversation (only if enabled and no milestones were processed)
        # If milestones were processed, personality evolution was already materialized at each milestone
        evolution_stage = None
        if Config.ENABLE_PERSONALITY_MATERIALIZATION and (not milestone_turns or max_turns not in milestone_turns):
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
                if dummy.personality_evolution:
                    print(f"   ✅ Personality evolution captured: {len(dummy.personality_evolution.conversation_profile.evolution_stages)} stages")
        elif dummy.personality_evolution:
            print(f"   ✅ Personality evolution already captured at milestones: {len(dummy.personality_evolution.conversation_profile.evolution_stages)} stages")
        
        # Post-assessment
        # Only run if conversation completed all turns; otherwise inherit from last milestone
        post_assessment = None
        conversation_completed_all_turns = (len(conversation.turns) >= max_turns)
        
        if enable_assessments and self.assessment_system:
            if conversation_completed_all_turns:
                # Conversation finished normally - run post-assessment
                # Use last milestone assessment as anchor if available
                last_milestone_assessment = None
                if milestone_assessments:
                    # Get the last valid milestone with detailed_assessment
                    valid_milestones = [m for m in milestone_assessments if m.get('detailed_assessment')]
                    if valid_milestones:
                        last_milestone_result = valid_milestones[-1]
                        # Reconstruct Assessment object from detailed_assessment
                        from assessment_system_llm_based import Assessment, AssessmentResponse
                        last_detailed = last_milestone_result['detailed_assessment']
                        last_milestone_assessment = Assessment(
                            dummy_id=last_detailed['dummy_id'],
                            assessment_type="milestone",
                            responses=[
                                AssessmentResponse(
                                    question=r['question'],
                                    score=r['score'],
                                    confidence=r.get('confidence', 8),
                                    reasoning=r.get('notes', ''),
                                    notes=r.get('notes', '')
                                )
                                for r in last_detailed['responses']
                            ],
                            total_score=last_detailed['total_score'],
                            average_score=last_detailed['average_score'],
                            improvement_areas=last_detailed.get('improvement_areas', [])
                        )
                        print(f"   📊 Anchoring post-assessment to last milestone (turn {last_milestone_result['milestone_turn']}, score {last_milestone_assessment.average_score:.2f})...")
                
                print(f"   📊 Running post-assessment...")
                post_assessment = await self.assessment_system.generate_post_assessment(
                    dummy, pre_assessment, conversation, 
                    conversation_simulator=self.conversation_simulator,
                    previous_milestone_assessment=last_milestone_assessment
                )
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
            else:
                # Conversation ended early - inherit from last milestone
                if milestone_assessments:
                    last_milestone = milestone_assessments[-1]
                    last_score = last_milestone['milestone_score']
                    print(f"   📋 Conversation ended early - inheriting post-assessment from last milestone: {last_score:.2f}")
                    
                    # Create a mock assessment with inherited score
                    from assessment_system_llm_based import Assessment, AssessmentResponse
                    
                    # Inherit responses from last milestone
                    inherited_responses = []
                    if last_milestone.get('detailed_assessment') and last_milestone['detailed_assessment']:
                        for resp in last_milestone['detailed_assessment']['responses']:
                            inherited_responses.append(AssessmentResponse(
                                question=resp['question'],
                                score=resp['score'],
                                confidence=resp['confidence'],
                                notes=resp.get('notes')
                            ))
                    else:
                        # Fallback: create generic responses with inherited score
                        for i in range(20):
                            inherited_responses.append(AssessmentResponse(
                                question=f"Inherited assessment {i+1}",
                                score=int(round(last_score)),
                                confidence=8,
                                notes="Inherited from last milestone"
                            ))
                    
                    # Use the milestone_score directly, not recalculated from responses
                    # (responses might average differently due to rounding)
                    post_assessment = Assessment(
                        dummy_id=dummy.id,
                        timestamp=datetime.now(),
                        responses=inherited_responses,
                        total_score=last_score * 20,  # Use milestone score directly
                        average_score=last_score,  # Use milestone score directly
                        improvement_areas=last_milestone['detailed_assessment'].get('improvement_areas', []) if last_milestone.get('detailed_assessment') else []
                    )
                    print(f"   📊 Post-assessment (inherited): {post_assessment.average_score:.2f}")
                else:
                    print(f"   ⚠️  No milestones to inherit from - using pre-assessment")
                    post_assessment = pre_assessment
        
        # Use real milestone assessments from conversation simulation
        milestone_results = milestone_assessments if enable_assessments else []
        
        # Update milestone assessments with actual pre-assessment scores
        if milestone_results and pre_assessment:
            for milestone in milestone_results:
                milestone["pre_score"] = pre_assessment.average_score
                milestone["improvement"] = round(milestone["milestone_score"] - pre_assessment.average_score, 3)
        
        # Count reached vs unreached milestones
        reached_milestones = [m for m in milestone_results if m.get("reached", True)]
        unreached_milestones = [m for m in milestone_results if not m.get("reached", True)]
        
        # Prepare result
        result = {
            "dummy_name": dummy.name,
            "dummy_id": dummy.id,
            "pre_assessment_score": pre_assessment.average_score if pre_assessment else 2.5,
            "final_assessment_score": post_assessment.average_score if post_assessment else 2.5,
            "post_assessment_inherited": not conversation_completed_all_turns and enable_assessments,
            "final_improvement": (post_assessment.average_score if post_assessment else 2.5) - (pre_assessment.average_score if pre_assessment else 2.5),
            "total_conversation_turns": len(conversation.turns),
            "conversation_ended_early": len(unreached_milestones) > 0,
            "milestones_reached": len(reached_milestones),
            "milestones_total": len(milestone_results),
            "total_duration_seconds": conversation.duration_seconds if hasattr(conversation, 'duration_seconds') else 120.0,
            "milestone_results": milestone_results,
            "personality_evolution": {
                "enabled": Config.ENABLE_PERSONALITY_EVOLUTION,
                "materialization_enabled": Config.ENABLE_PERSONALITY_MATERIALIZATION,
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
                                                   max_turns: int,
                                                   milestone_turns: List[int],
                                                   enable_assessments: bool,
                                                   pre_assessment: 'Assessment' = None) -> Tuple[Conversation, List[Dict[str, Any]]]:
        """Simulate conversation with OPTIMIZED flow: continuous conversation + parallel milestone processing
        
        Args:
            dummy: The AI dummy
            base_prompt: The system prompt for the AI mentor
            max_turns: Maximum conversation turns
            milestone_turns: Turn numbers for assessments
            enable_assessments: Whether to run assessments
            pre_assessment: The baseline pre-assessment (for grounding milestone assessments)
        """
        
        print(f"   🚀 Starting OPTIMIZED conversation flow...")
        
        # Phase 1: Run continuous conversation without interruptions
        conversation = await self._run_continuous_conversation(dummy, base_prompt, max_turns)
        
        # Phase 2: Process milestones sequentially with grounded assessments
        milestone_assessments = []
        if enable_assessments and milestone_turns:
            print(f"   🔄 Processing {len(milestone_turns)} milestones with grounded assessments...")
            milestone_assessments = await self._process_milestones_parallel(
                dummy, conversation, milestone_turns, pre_assessment
            )
        
        return conversation, milestone_assessments
    
    async def _run_continuous_conversation(self, dummy: AIDummy, base_prompt: str, max_turns: int) -> Conversation:
        """Run conversation continuously with end detection using the latest conversation simulator"""
        
        print(f"   🔄 Running conversation with end detection (max {max_turns} turns)...")
        
        # Convert max_turns to num_rounds for the simulator (it still uses rounds internally)
        num_rounds = (max_turns - 1) // 2
        
        # Use the latest conversation simulator with end detection
        conversation = await self.conversation_simulator.simulate_conversation_async(
            dummy=dummy,
            scenario="Social skills coaching session",
            num_rounds=num_rounds,
            custom_system_prompt=base_prompt
        )
        
        # Update conversation metadata for experiment tracking
        conversation.id = f"conv_{dummy.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        conversation.dummy_id = dummy.id
        conversation.system_prompt = base_prompt
        conversation.scenario = "Social skills coaching session"
        conversation.start_time = datetime.now()
        
        actual_turns = len(conversation.turns)
        if actual_turns < max_turns:
            print(f"   ⏹️  Conversation ended early: {actual_turns} turns (expected {max_turns})")
        else:
            print(f"   ✅ Conversation completed: {actual_turns} turns")
        
        return conversation
    
    async def _process_milestones_parallel(self, dummy: AIDummy, conversation: Conversation, 
                                          milestone_turns: List[int],
                                          pre_assessment: 'Assessment') -> List[Dict[str, Any]]:
        """Process all milestones with progressive grounded assessment scoring
        
        Args:
            dummy: The AI dummy being assessed
            conversation: The full conversation
            milestone_turns: List of turn numbers for milestones
            pre_assessment: The baseline pre-assessment to use as first anchor
        """
        
        # Process milestones sequentially to maintain progressive grounded scoring
        # Each milestone anchors to the previous milestone's assessment
        valid_milestone_assessments = []
        previous_result = None  # Start with no previous result (will use pre_assessment)
        
        for milestone_turn in milestone_turns:
            print(f"   🔄 Processing milestone at turn {milestone_turn}...")
            
            try:
                result = await self._process_single_milestone(
                    dummy, conversation, milestone_turn, previous_result, pre_assessment
                )
                
                if result:
                    valid_milestone_assessments.append(result)
                    previous_result = result  # Update for next milestone
                    print(f"   ✅ Milestone at turn {milestone_turn} completed: {result['milestone_score']:.2f} (improvement: {result['improvement']:+.3f})")
                else:
                    print(f"   ⚠️  Milestone at turn {milestone_turn} returned no result")
                    
            except Exception as e:
                print(f"   ❌ Milestone at turn {milestone_turn} failed: {e}")
        
        return valid_milestone_assessments
    
    async def _process_single_milestone(self, dummy: AIDummy, conversation: Conversation, 
                                      milestone_turn: int, 
                                      previous_milestone_result: Dict[str, Any] = None,
                                      pre_assessment: 'Assessment' = None) -> Optional[Dict[str, Any]]:
        """Process a single milestone: materialization + assessment
        
        Args:
            dummy: The AI dummy being assessed
            conversation: The full conversation
            milestone_turn: The turn number for this milestone
            previous_milestone_result: The previous milestone result (for inheritance and anchoring)
            pre_assessment: The baseline pre-assessment (for first milestone anchoring)
        """
        
        # Check if conversation actually reached this milestone turn
        actual_turns = len(conversation.turns)
        
        print(f"   📊 Assessing at turn {milestone_turn}...")
        
        if actual_turns < milestone_turn:
            print(f"   ⏭️  Turn {milestone_turn} not reached (conversation ended at {actual_turns} turns)")
            
            # Inherit from previous milestone
            if previous_milestone_result is not None:
                previous_score = previous_milestone_result['milestone_score']
                print(f"   📋 Inheriting score from previous milestone: {previous_score:.2f}")
                return {
                    "milestone_turn": milestone_turn,
                    "pre_score": previous_score,
                    "milestone_score": previous_score,
                    "improvement": 0.0,
                    "conversation_turns": actual_turns,
                    "timestamp": datetime.now().isoformat(),
                    "note": f"Not reached - inherited from previous milestone",
                    "detailed_assessment": None,
                    "reached": False  # Mark as unreached
                }
            else:
                print(f"   ⚠️  No previous milestone to inherit from - skipping")
                return None
        
        # Create conversation up to milestone point
        # Include all turns up to and including the milestone turn
        milestone_conversation = Conversation(
            id=f"conv_{dummy.id}_milestone_turn{milestone_turn}",
            dummy_id=dummy.id,
            system_prompt=conversation.system_prompt,
            scenario=conversation.scenario,
            turns=conversation.turns[:milestone_turn],  # First N turns
            start_time=conversation.start_time
        )
        
        try:
            # Materialize personality evolution at this milestone (if enabled)
            evolution_stage = None
            if Config.ENABLE_PERSONALITY_MATERIALIZATION:
                print(f"   🧠 Materializing personality evolution at turn {milestone_turn}...")
                
                # Get baseline score for materialization
                baseline_score = previous_milestone_result['milestone_score'] if previous_milestone_result else (pre_assessment.average_score if pre_assessment else 2.5)
                
                evolution_stage = await personality_materializer.materialize_personality_from_conversation(
                    dummy=dummy,
                    conversation=milestone_conversation,
                    prompt_id="conversation_length_test",
                    prompt_name="Conversation Length Test",
                    generation=0,
                    pre_assessment_score=baseline_score,
                    post_assessment_score=0.0  # Will be updated after milestone assessment
                )
                
                if evolution_stage:
                    dummy.add_evolution_stage(evolution_stage)
                    personality_evolution_storage.save_personality_evolution(dummy)
                    print(f"   ✅ Personality evolution captured at turn {milestone_turn}")
            
            # Run milestone assessment with grounded scoring (using current evolved personality)
            if self.assessment_system:
                from assessment_system_llm_based import Assessment, AssessmentResponse
                
                # Get the previous assessment to use as anchor
                # If we have a previous milestone result with detailed assessment, use that
                # Otherwise, use pre_assessment (baseline)
                if previous_milestone_result and previous_milestone_result.get('detailed_assessment'):
                    # Reconstruct Assessment object from previous milestone
                    prev_detailed = previous_milestone_result['detailed_assessment']
                    previous_assessment = Assessment(
                        dummy_id=prev_detailed['dummy_id'],
                        assessment_type="milestone",
                        responses=[
                            AssessmentResponse(
                                question=r['question'],
                                score=r['score'],
                                confidence=r.get('confidence', 8),
                                reasoning=r.get('notes', ''),
                                notes=r.get('notes', '')
                            )
                            for r in prev_detailed['responses']
                        ],
                        total_score=prev_detailed['total_score'],
                        average_score=prev_detailed['average_score'],
                        improvement_areas=prev_detailed.get('improvement_areas', [])
                    )
                    print(f"   📊 Anchoring to previous milestone assessment (score: {previous_assessment.average_score:.2f})")
                else:
                    # Use baseline pre-assessment as anchor
                    previous_assessment = pre_assessment
                    print(f"   📊 Anchoring to baseline pre-assessment (score: {previous_assessment.average_score:.2f})")
                
                # Use new milestone assessment method with previous assessment as anchor
                milestone_assessment = await self.assessment_system.generate_milestone_assessment(
                    dummy=dummy,
                    previous_assessment=previous_assessment,
                    conversation=milestone_conversation,
                    conversation_simulator=self.conversation_simulator,
                    turns_so_far=milestone_turn
                )
                
                # Update evolution stage with milestone assessment score
                if evolution_stage:
                    evolution_stage.post_assessment_score = milestone_assessment.average_score
                    evolution_stage.improvement_score = milestone_assessment.average_score - previous_assessment.average_score
                    personality_evolution_storage.save_personality_evolution(dummy)
                
                # Calculate improvement from previous assessment (grounded comparison)
                improvement = milestone_assessment.average_score - previous_assessment.average_score
                
                milestone_result = {
                    "milestone_turn": milestone_turn,
                    "pre_score": previous_assessment.average_score,
                    "milestone_score": round(milestone_assessment.average_score, 2),
                    "improvement": round(improvement, 3),
                    "conversation_turns": len(milestone_conversation.turns),
                    "timestamp": datetime.now().isoformat(),
                    "note": f"Grounded assessment: {milestone_assessment.average_score:.2f} (anchored to previous {previous_assessment.average_score:.2f})",
                    "reached": True,  # Mark as actually reached
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
            print(f"   ❌ Error processing milestone at turn {milestone_turn}: {e}")
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
        
        # Conversation completion stats
        early_endings = sum(1 for r in results if r.get("conversation_ended_early", False))
        avg_turns = sum(r["total_conversation_turns"] for r in results) / len(results)
        
        print(f"\n💬 Conversation Completion:")
        print(f"   • Early endings: {early_endings}/{len(results)} conversations")
        print(f"   • Average turns: {avg_turns:.1f}")
        
        # Personality evolution stats
        evolution_enabled_count = sum(1 for r in results if r["personality_evolution"]["enabled"])
        avg_evolution_stages = sum(r["personality_evolution"]["evolution_stages"] for r in results) / len(results)
        avg_final_anxiety = sum(r["personality_evolution"]["final_anxiety_level"] for r in results) / len(results)
        
        print(f"\n🧬 Personality Evolution:")
        print(f"   • Evolution enabled: {evolution_enabled_count}/{len(results)}")
        print(f"   • Materialization enabled: {results[0]['personality_evolution']['materialization_enabled']}")
        print(f"   • Average evolution stages: {avg_evolution_stages:.1f}")
        print(f"   • Average final anxiety level: {avg_final_anxiety:.1f}/10")
        
        # Individual results
        print(f"\n👥 Individual Results:")
        for result in results:
            evolution = result["personality_evolution"]
            early_marker = " 🔚" if result.get("conversation_ended_early", False) else ""
            inherited_marker = " (inherited)" if result.get("post_assessment_inherited", False) else ""
            print(f"   • {result['dummy_name']}: +{result['final_improvement']:.3f} points ({result['total_conversation_turns']} turns){early_marker}")
            if result.get("conversation_ended_early"):
                print(f"     - Milestones reached: {result['milestones_reached']}/{result['milestones_total']}")
            if result.get("post_assessment_inherited"):
                print(f"     - Post-assessment: inherited from last milestone")
            print(f"     - Evolution stages: {evolution['evolution_stages']}")
            print(f"     - Final anxiety: {evolution['final_anxiety_level']:.1f}/10")
            if evolution['materialization_enabled']:
                print(f"     - Materialized traits: {evolution['materialized_fears']} fears, {evolution['materialized_challenges']} challenges")

async def main():
    """Main function to run the experiment"""
    parser = argparse.ArgumentParser(description="Run conversation length experiment with personality evolution")
    parser.add_argument("--dummies", type=int, default=3, help="Number of dummies to test")
    parser.add_argument("--max-turns", type=int, default=31, help="Maximum conversation turns (default: 31 = ~15 exchanges)")
    parser.add_argument("--max-rounds", type=int, default=None, help="[DEPRECATED] Use --max-turns instead")
    parser.add_argument("--milestones", type=str, default="11,21,31", help="Assessment milestone turn numbers (comma-separated). Example: '11,21,31' = assess at turns 11, 21, 31")
    parser.add_argument("--prompt", type=str, help="Custom system prompt to test")
    parser.add_argument("--save-details", action="store_true", help="Save full conversation details")
    parser.add_argument("--no-assessments", action="store_true", help="Disable assessments")
    
    args = parser.parse_args()
    
    # Parse milestones as turn numbers directly (no conversion needed!)
    milestone_turns = [int(x.strip()) for x in args.milestones.split(",")]
    print(f"✅ Milestones configured: assess at turns {milestone_turns}")
    
    # Default prompt - load from YAML for better maintainability
    base_prompt = args.prompt or prompt_loader.get_prompt(
        'default_prompts.yaml',
        'default_peer_mentor_prompt'
    )
    
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
    
    # Handle backward compatibility: --max-rounds → --max-turns
    if args.max_rounds is not None:
        print(f"⚠️  Warning: --max-rounds is deprecated, use --max-turns instead")
        max_turns = 1 + args.max_rounds * 2  # Convert rounds to turns
    else:
        max_turns = args.max_turns
    
    # Run experiment
    experiment = ConversationLengthExperimentWithEvolution()
    await experiment.run_experiment(
        dummies=dummies,
        max_turns=max_turns,
        milestone_turns=milestone_turns,
        base_prompt=base_prompt,
        save_details=args.save_details,
        enable_assessments=not args.no_assessments
    )

if __name__ == "__main__":
    asyncio.run(main())
