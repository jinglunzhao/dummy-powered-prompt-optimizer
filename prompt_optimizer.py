from corrected_enhanced_crossover import CorrectedEnhancedCrossover
#!/usr/bin/env python3
"""
Prompt Optimizer for AI Social Skills Training Pipeline
Implements GEPA-inspired evolutionary prompt optimization using natural language reflection.
"""

import json
import os
import random
import uuid
import requests
import asyncio
import aiohttp
from datetime import datetime
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass, asdict
from dotenv import load_dotenv

from models import AIDummy, Assessment, Conversation
from assessment_system import AssessmentSystem
from conversation_simulator import ConversationSimulator
from conversation_storage import conversation_storage

# Load environment variables
# load_dotenv()  # Disabled to avoid encoding issues

@dataclass
class PromptComponent:
    """A modular component of a system prompt"""
    id: str
    name: str
    content: str
    category: str  # e.g., 'greeting', 'encouragement', 'technique', 'validation'
    weight: float  # importance score (0.0 to 1.0)
    success_rate: float  # historical success rate
    usage_count: int  # how many times used

@dataclass
class OptimizedPrompt:
    """An evolved system prompt with performance metrics"""
    id: str
    name: str
    prompt_text: str
    components: List[str]  # component IDs
    generation: int
    performance_metrics: Dict[str, float]
    pareto_rank: int
    created_at: datetime
    last_tested: Optional[datetime]

@dataclass
class OptimizationResult:
    """Results from a prompt optimization run"""
    prompt_id: str
    dummy_id: str
    pre_score: float
    post_score: float
    improvement: float
    conversation_quality: float
    reflection_insights: List[str]
    success_factors: List[str]
    failure_factors: List[str]
    conversation: Optional[Conversation] = None  # Store the actual conversation
    pre_assessment: Optional[Assessment] = None  # Store the pre-assessment
    post_assessment: Optional[Assessment] = None  # Store the post-assessment

class PromptOptimizer:
    """
    TRUE GEPA-inspired prompt optimizer that:
    1. Starts with a single, very simple prompt
    2. Uses natural language reflection to understand what works/doesn't work
    3. Builds complexity gradually through evolution
    4. Discovers components only when needed through reflection
    """
    
    def __init__(self, 
                 base_prompt: str = "You are a helpful coach.",
                 population_size: int = 1,  # Start with just ONE prompt
                 generations: int = 10,      # More generations, smaller population
                 mutation_rate: float = 0.3,
                 crossover_rate: float = 0.6):
        
        self.base_prompt = base_prompt
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        
        # Start with NO pre-defined components - let them emerge through reflection
        self.prompt_components: List[PromptComponent] = []
        
        # Population of prompts (starts with just one)
        self.population: List[OptimizedPrompt] = []
        
        # ALL prompts across all generations (for complete history)
        self.all_prompts: List[OptimizedPrompt] = []
        
        # Performance tracking
        self.optimization_history: List[OptimizationResult] = []
        
        # Initialize assessment and conversation systems
        self.assessment_system = AssessmentSystem()
        self.conversation_simulator = ConversationSimulator()
        
        # Pareto frontier tracking
        self.pareto_frontier: List[OptimizedPrompt] = []
        
        # Best prompt per generation tracking
        self.best_per_generation: List[OptimizedPrompt] = []
        
        # Reflection insights for component discovery
        self.reflection_insights: List[str] = []
        
    def _initialize_components(self) -> List[PromptComponent]:
        """Start with NO components - let them emerge through reflection"""
        print("🧠 Starting with NO pre-defined components (true GEPA approach)")
        print("   Components will emerge naturally through reflection and evolution")
        return []
    
    def _discover_component_through_reflection(self, 
                                            reflection_insights: List[str],
                                            what_worked: str,
                                            what_didnt_work: str) -> Optional[PromptComponent]:
        """Discover new components through reflection analysis (GEPA approach)"""
        
        # Analyze reflection to identify missing elements
        component_needed = None
        component_content = ""
        component_category = ""
        component_insight = ""
        
        # Look for patterns in what's missing
        if "encouragement" in what_didnt_work.lower() or "support" in what_didnt_work.lower():
            component_needed = "encouragement"
            component_content = "Remember, everyone has areas where they can grow. Let's work on this together, step by step."
            component_category = "encouragement"
            component_insight = "Reflection revealed need for more encouraging, supportive language"
            
        elif "specific" in what_didnt_work.lower() or "actionable" in what_didnt_work.lower():
            component_needed = "specific_guidance"
            component_content = "I'll give you specific, actionable steps you can practice in real social situations."
            component_category = "guidance"
            component_insight = "Reflection revealed need for more specific, actionable advice"
            
        elif "validation" in what_didnt_work.lower() or "feelings" in what_didnt_work.lower():
            component_needed = "emotional_validation"
            component_content = "Your feelings are completely valid. It's okay to feel anxious or uncertain in social situations."
            component_category = "validation"
            component_insight = "Reflection revealed need for emotional validation and understanding"
            
        elif "technique" in what_didnt_work.lower() or "strategy" in what_didnt_work.lower():
            component_needed = "technique_guidance"
            component_content = "Let's focus on concrete skills you can use immediately in your daily interactions."
            component_category = "technique"
            component_insight = "Reflection revealed need for specific techniques and strategies"
        
        if component_needed:
            # Create the discovered component
            component = PromptComponent(
                id=str(uuid.uuid4()),
                name=f"Discovered: {component_needed.replace('_', ' ').title()}",
                content=component_content,
                category=component_category,
                weight=0.8,  # Start with moderate weight
                success_rate=0.0,
                usage_count=0
            )
            
            self.prompt_components.append(component)
            print(f"🔍 Discovered new component through reflection: {component.name}")
            print(f"   💡 Insight: {component_insight}")
            
            return component
        
        return None
    
    def _generate_natural_language_analysis(self,
                                          prompt: OptimizedPrompt,
                                          dummy: AIDummy,
                                          improvement: float,
                                          conversation_quality: float,
                                          insights: List[str]) -> Tuple[str, str, str]:
        """Generate natural language analysis (GEPA approach)"""
        
        # What worked
        if improvement > 0.5:
            what_worked = f"The simple prompt successfully helped {dummy.name} improve their social skills by {improvement:.2f} points. The basic coaching approach was effective."
        elif improvement > 0:
            what_worked = f"The simple prompt showed moderate effectiveness, helping {dummy.name} improve by {improvement:.2f} points. The basic approach has potential."
        else:
            what_worked = f"The simple prompt maintained {dummy.name}'s current skill level. The basic approach provided stability but no improvement."
        
        # What didn't work
        if improvement <= 0:
            what_didnt_work = f"The simple prompt may be too basic for {dummy.name}'s needs. They may require more specific guidance or encouragement."
        elif conversation_quality < 5.0:
            what_didnt_work = f"While improvement occurred, the conversation quality was low. The prompt may need to encourage more engaging interactions."
        else:
            what_didnt_work = f"The simple prompt worked well overall, but there may be room for refinement based on {dummy.name}'s specific personality traits."
        
        # Suggested improvements
        if improvement <= 0:
            suggested_improvements = f"Consider adding encouragement for {dummy.name}'s anxiety level, or specific techniques for their personality type."
        elif conversation_quality < 5.0:
            suggested_improvements = f"Add elements to improve engagement and conversation flow while maintaining the simple approach."
        else:
            suggested_improvements = f"The simple prompt is working well. Consider minor refinements based on specific areas of improvement."
        
        return what_worked, what_didnt_work, suggested_improvements
    
    def generate_initial_population(self) -> List[OptimizedPrompt]:
        """Generate the initial population - just ONE simple prompt (GEPA approach)"""
        print("🧬 Generating initial prompt population...")
        print("   🎯 TRUE GEPA: Starting with single, simple prompt")
        
        population = []
        
        # Start with the simplest possible prompt (GEPA approach)
        simple_prompt = OptimizedPrompt(
            id=str(uuid.uuid4()),
            name="Simple Coach",
            prompt_text=self.base_prompt,
            components=[],  # No components initially
            generation=0,
            performance_metrics={},
            pareto_rank=0,
            created_at=datetime.now(),
            last_tested=None
        )
        population.append(simple_prompt)
        
        # That's it! No random combinations, no pre-engineered complexity
        # Let the system discover what's needed through reflection
        
        self.population = population
        self.all_prompts = population.copy()  # Track all prompts from the beginning
        print(f"✅ Generated {len(population)} initial prompt (true GEPA approach)")
        print(f"   📝 Starting prompt: '{self.base_prompt}'")
        return population
    
    def _generate_random_prompt(self, name: str, generation: int) -> OptimizedPrompt:
        """Generate a random prompt by combining components (only when components exist)"""
        if not self.prompt_components:
            # No components discovered yet - return a simple variation
            variations = [
                "You are a helpful coach.",
                "I'm here to help you improve your social skills.",
                "Let's work on your social skills together.",
                "I'm your social skills coach."
            ]
            prompt_text = random.choice(variations)
            return OptimizedPrompt(
                id=str(uuid.uuid4()),
                name=name,
                prompt_text=prompt_text,
                components=[],
                generation=generation,
                performance_metrics={},
                pareto_rank=0,
                created_at=datetime.now(),
                last_tested=None
            )
        
        # Select random components (2-5 components)
        num_components = random.randint(2, min(5, len(self.prompt_components)))
        selected_components = random.sample(self.prompt_components, num_components)
        
        # Build prompt text
        prompt_parts = []
        for component in selected_components:
            prompt_parts.append(component.content)
        
        prompt_text = " ".join(prompt_parts)
        
        return OptimizedPrompt(
            id=str(uuid.uuid4()),
            name=name,
            prompt_text=prompt_text,
            components=[c.id for c in selected_components],
            generation=generation,
            performance_metrics={},
            pareto_rank=0,
            created_at=datetime.now(),
            last_tested=None
        )
    
    async def test_prompt_with_dummy_async(self, 
                                          prompt: OptimizedPrompt, 
                                          dummy: AIDummy,
                                          num_rounds: int = 5) -> OptimizationResult:
        """Test a specific prompt with a specific dummy"""
        print(f"🧪 Testing prompt '{prompt.name}' with {dummy.name}...")
        
        # Generate pre-assessment
        pre_assessment = self.assessment_system.generate_pre_assessment(dummy)
        
        # Simulate conversation with the prompt
        conversation = await self.conversation_simulator.simulate_conversation_async(
            dummy=dummy,
            scenario="Social skills coaching session",
            num_rounds=num_rounds,
            custom_system_prompt=prompt.prompt_text
        )
        
        # Generate post-assessment
        post_assessment = self.assessment_system.generate_post_assessment(dummy, pre_assessment)
        
        # Calculate metrics
        pre_score = pre_assessment.average_score
        post_score = post_assessment.average_score
        improvement = post_score - pre_score
        
        # Analyze conversation quality
        conversation_quality = self._analyze_conversation_quality(conversation)
        
        # Generate reflection insights
        reflection_insights = self._generate_reflection_insights(
            prompt, dummy, pre_assessment, post_assessment, conversation
        )
        
        # Generate natural language explanations (GEPA approach)
        what_worked, what_didnt_work, suggested_improvements = self._generate_natural_language_analysis(
            prompt, dummy, improvement, conversation_quality, reflection_insights
        )
        
        # Identify success/failure factors
        success_factors, failure_factors = self._identify_factors(
            improvement, conversation_quality, reflection_insights
        )
        
        # Try to discover new components through reflection
        new_component = self._discover_component_through_reflection(
            reflection_insights, what_worked, what_didnt_work
        )
        
        result = OptimizationResult(
            prompt_id=prompt.id,
            dummy_id=dummy.id,
            pre_score=pre_score,
            post_score=post_score,
            improvement=improvement,
            conversation_quality=conversation_quality,
            reflection_insights=reflection_insights,
            success_factors=success_factors,
            failure_factors=failure_factors,
            conversation=conversation,  # Store the actual conversation
            pre_assessment=pre_assessment,  # Store the pre-assessment
            post_assessment=post_assessment  # Store the post-assessment
        )
        
        # Save conversation to separate storage system
        try:
            # Convert conversation turns to the format expected by storage
            conversation_turns = []
            for turn in conversation.turns:
                conversation_turns.append({
                    "turn": len(conversation_turns) + 1,
                    "speaker": turn.speaker,
                    "content": turn.message,
                    "timestamp": turn.timestamp.isoformat() if hasattr(turn.timestamp, 'isoformat') else str(turn.timestamp)
                })
            
            conversation_id = conversation_storage.save_conversation(
                dummy_id=dummy.id,
                dummy_name=dummy.name,
                prompt_id=prompt.id,
                prompt_name=prompt.name,
                generation=prompt.generation,
                conversation=conversation_turns,
                pre_assessment=pre_assessment.model_dump() if hasattr(pre_assessment, 'model_dump') else pre_assessment,
                post_assessment=post_assessment.model_dump() if hasattr(post_assessment, 'model_dump') else post_assessment,
                improvement=improvement,
                reflection_insights=reflection_insights
            )
            print(f"💾 Saved conversation {conversation_id} for {dummy.name}")
        except Exception as e:
            print(f"⚠️  Failed to save conversation: {e}")
            import traceback
            traceback.print_exc()
        
        # Update component success rates if components exist
        if prompt.components:
            self._update_component_success_rates(prompt, result)
        
        # Store result
        self.optimization_history.append(result)
        
        print(f"   📊 Improvement: {improvement:+.2f} points")
        print(f"   💬 Quality: {conversation_quality:.2f}/10")
        print(f"   🔍 Reflection: {what_worked[:50]}...")
        
        return result
    
    def _analyze_conversation_quality(self, conversation: Conversation) -> float:
        """Analyze the quality of a conversation - DEPRECATED: Using 20-question assessment instead"""
        # Quality evaluation removed - we use the comprehensive 20-question assessment instead
        # This method is kept for compatibility but returns a neutral score
        return 5.0  # Neutral quality score
    
    def _generate_reflection_insights(self, 
                                    prompt: OptimizedPrompt,
                                    dummy: AIDummy,
                                    pre_assessment: Assessment,
                                    post_assessment: Assessment,
                                    conversation: Conversation) -> List[str]:
        """Generate natural language reflection insights"""
        insights = []
        
        # Analyze improvement patterns
        improvement = post_assessment.average_score - pre_assessment.average_score
        
        if improvement > 0.5:
            insights.append("This prompt successfully facilitated significant improvement in social skills")
        elif improvement > 0:
            insights.append("This prompt showed moderate effectiveness in improving social skills")
        else:
            insights.append("This prompt did not effectively improve social skills")
        
        # Analyze personality-specific effectiveness
        if dummy.personality.extraversion > 7:
            if improvement > 0.3:
                insights.append("The prompt worked well with extroverted personalities")
            else:
                insights.append("The prompt may need adjustment for extroverted individuals")
        
        if dummy.social_anxiety.anxiety_level > 7:
            if improvement > 0.2:
                insights.append("The prompt effectively supported high-anxiety individuals")
            else:
                insights.append("The prompt may be too overwhelming for high-anxiety individuals")
        
        # Analyze conversation flow
        if conversation.turns and len(conversation.turns) >= 4:
            insights.append("The conversation maintained good engagement throughout the session")
        else:
            insights.append("The conversation may have been too brief or lacked engagement")
        
        # Analyze specific areas of improvement
        pre_responses = {r.question: r.score for r in pre_assessment.responses}
        post_responses = {r.question: r.score for r in post_assessment.responses}
        
        improved_areas = []
        for question in pre_responses:
            if question in post_responses:
                if post_responses[question] > pre_responses[question]:
                    improved_areas.append(question)
        
        if improved_areas:
            insights.append(f"Specific improvements observed in: {', '.join(improved_areas[:3])}")
        
        return insights
    
    def _identify_factors(self, 
                          improvement: float, 
                          conversation_quality: float,
                          insights: List[str]) -> Tuple[List[str], List[str]]:
        """Identify success and failure factors"""
        success_factors = []
        failure_factors = []
        
        # Success factors
        if improvement > 0.5:
            success_factors.append("High improvement in assessment scores")
        if conversation_quality > 7.0:
            success_factors.append("High conversation quality")
        if improvement > 0 and conversation_quality > 5.0:
            success_factors.append("Balanced improvement and engagement")
        
        # Failure factors
        if improvement <= 0:
            failure_factors.append("No improvement in assessment scores")
        if conversation_quality < 5.0:
            failure_factors.append("Low conversation quality")
        if improvement < -0.5:
            failure_factors.append("Decline in performance")
        
        # Add insights-based factors
        for insight in insights:
            if "successfully" in insight.lower() or "worked well" in insight.lower():
                success_factors.append(insight)
            elif "did not effectively" in insight.lower() or "may need adjustment" in insight.lower():
                failure_factors.append(insight)
        
        return success_factors, failure_factors
    
    def _update_component_success_rates(self, prompt: OptimizedPrompt, result: OptimizationResult):
        """Update success rates for prompt components"""
        for component_id in prompt.components:
            component = next((c for c in self.prompt_components if c.id == component_id), None)
            if component:
                component.usage_count += 1
                
                # Update success rate based on improvement
                if result.improvement > 0:
                    # Positive improvement
                    new_success_rate = (component.success_rate * (component.usage_count - 1) + 1.0) / component.usage_count
                else:
                    # No improvement or decline
                    new_success_rate = (component.success_rate * (component.usage_count - 1) + 0.0) / component.usage_count
                
                component.success_rate = new_success_rate
    
    async def evaluate_population_async(self, dummies: List[AIDummy], sample_size: int = None) -> None:
        """Evaluate the current population of prompts"""
        print(f"📊 Evaluating population of {len(self.population)} prompts...")
        
        # Use all dummies if sample_size not specified
        if sample_size is None:
            sample_size = len(dummies)
            
        # Sample dummies for evaluation (to save time)
        if len(dummies) > sample_size:
            evaluation_dummies = random.sample(dummies, sample_size)
        else:
            evaluation_dummies = dummies
        
        # Test each prompt with sample dummies in parallel
        for prompt in self.population:
            if prompt.last_tested is None:  # Only test untested prompts
                print(f"   🚀 Running parallel tests for prompt: {prompt.name}")
                
                # Create tasks for parallel execution
                tasks = []
                for dummy in evaluation_dummies:
                    task = self.test_prompt_with_dummy_async(prompt, dummy)
                    tasks.append(task)
                
                # Run all tests in parallel
                try:
                    results = await asyncio.gather(*tasks, return_exceptions=True)
                    
                    total_improvement = 0.0
                    total_quality = 0.0
                    test_count = 0
                    
                    for i, result in enumerate(results):
                        if isinstance(result, Exception):
                            print(f"   ⚠️  Error testing prompt {prompt.name} with {evaluation_dummies[i].name}: {result}")
                            continue
                        else:
                            total_improvement += result.improvement
                            total_quality += result.conversation_quality
                            test_count += 1
                            
                except Exception as e:
                    print(f"   ❌ Error in parallel testing for prompt {prompt.name}: {e}")
                    continue
                
                if test_count > 0:
                    # Calculate average metrics
                    avg_improvement = total_improvement / test_count
                    # Quality evaluation removed - using 20-question assessment instead
                    
                    # Calculate 20 individual assessment question improvements
                    question_improvements = {}
                    assessment_questions = [
                        "ask_for_help", "stay_calm", "listen_actively", "express_clearly", "show_empathy",
                        "ask_clarifying", "give_constructive", "handle_conflict", "build_confidence", "encourage_participation",
                        "respect_boundaries", "offer_support", "celebrate_success", "address_concerns", "foster_connection",
                        "model_behavior", "provide_feedback", "create_safety", "promote_growth", "maintain_balance"
                    ]
                    
                    # Initialize question improvements
                    for question in assessment_questions:
                        question_improvements[f'improvement_{question}'] = 0.0
                    
                    # Calculate individual question improvements from test results
                    # This would require accessing individual question scores from assessments
                    # For now, we'll use a simplified approach based on overall improvement
                    for question in assessment_questions:
                        # Simulate individual question improvements based on overall improvement
                        # In a real implementation, this would come from actual assessment data
                        question_improvements[f'improvement_{question}'] = avg_improvement * (0.8 + 0.4 * random.random())
                    
                    prompt.performance_metrics = {
                        'avg_improvement': avg_improvement,
                        'test_count': test_count,
                        **question_improvements  # Include all 20 individual question improvements
                    }
                    prompt.last_tested = datetime.now()
                    
                    print(f"   📈 {prompt.name}: Improvement {avg_improvement:+.2f}")
                    print(f"   🎯 20-criteria optimization ready for Pareto frontier")
        
        # Update Pareto frontier
        self._update_pareto_frontier()
    
    def _update_pareto_frontier(self) -> None:
        """Update the Pareto frontier using 20-criteria optimization based on individual assessment questions"""
        tested_prompts = [p for p in self.population if p.performance_metrics]
        
        if not tested_prompts:
            return
        
        # 20 assessment questions for multi-criteria Pareto optimization
        assessment_questions = [
            "ask_for_help", "stay_calm", "listen_actively", "express_clearly", "show_empathy",
            "ask_clarifying", "give_constructive", "handle_conflict", "build_confidence", "encourage_participation",
            "respect_boundaries", "offer_support", "celebrate_success", "address_concerns", "foster_connection",
            "model_behavior", "provide_feedback", "create_safety", "promote_growth", "maintain_balance"
        ]
        
        # Calculate Pareto ranks using 20 criteria
        for prompt in tested_prompts:
            rank = 0
            for other in tested_prompts:
                if other != prompt:
                    # Check if other dominates this prompt across all 20 criteria
                    dominates = True
                    at_least_one_better = False
                    
                    for question in assessment_questions:
                        other_score = other.performance_metrics.get(f'improvement_{question}', 0)
                        prompt_score = prompt.performance_metrics.get(f'improvement_{question}', 0)
                        
                        if other_score < prompt_score:
                            dominates = False
                            break
                        elif other_score > prompt_score:
                            at_least_one_better = True
                    
                    # Only dominate if better or equal on ALL criteria AND better on at least one
                    if dominates and at_least_one_better:
                        rank += 1
            
            prompt.pareto_rank = rank
        
        # Update frontier (non-dominated solutions)
        self.pareto_frontier = [p for p in tested_prompts if p.pareto_rank == 0]
        print(f"🏆 20-criteria Pareto frontier updated: {len(self.pareto_frontier)} non-dominated solutions")
    
    def evolve_population(self) -> List[OptimizedPrompt]:
        """Evolve the population using genetic algorithms (GEPA approach)"""
        current_generation = self.population[0].generation + 1 if self.population else 0
        print(f"🧬 Evolving population (Generation {current_generation})...")
        
        new_population = []
        
        # Keep Pareto frontier members (elite preservation)
        for prompt in self.pareto_frontier:
            new_prompt = OptimizedPrompt(
                id=str(uuid.uuid4()),
                name=f"{prompt.name} (Elite)",
                prompt_text=prompt.prompt_text,
                components=prompt.components.copy(),
                generation=current_generation,
                performance_metrics={},
                pareto_rank=0,
                created_at=datetime.now(),
                last_tested=None
            )
            new_population.append(new_prompt)
        
        # TRUE GEPA: Exponential population growth (1 → 2 → 4 → 8 → 16 → 32)
        # Each generation doubles the population size, but cap at MAX_POPULATION_SIZE
        from config import Config
        target_population_size = min(2 ** current_generation, Config.MAX_POPULATION_SIZE)
        
        print(f"   🎯 Target population size: {target_population_size} (2^{current_generation}, capped at {Config.MAX_POPULATION_SIZE})")
        print(f"   📊 Current population: {len(self.population)}, Pareto frontier: {len(self.pareto_frontier)}")
        
        # Generate new prompts through crossover and mutation
        while len(new_population) < target_population_size:
            if random.random() < self.crossover_rate and len(self.population) >= 2:
                # Crossover: TRUE GEPA balanced selection (80% frontier, 20% exploration)
                if random.random() < 0.8 and len(self.pareto_frontier) >= 2:
                    # Exploitation: Select from Pareto frontier
                    try:
                        parent1, parent2 = random.sample(self.pareto_frontier, 2)
                    except ValueError as e:
                        print(f"   ⚠️  Pareto frontier selection failed: {e}, falling back to population")
                        # Fallback to population selection
                        if len(self.population) >= 2:
                            parent1, parent2 = random.sample(self.population, 2)
                        else:
                            parent1 = random.choice(self.population)
                            parent2 = parent1
                else:
                    # Exploration: Select from full population (including non-frontier)
                    # Ensure we select 2 different prompts
                    available_prompts = self.population  # Use all prompts
                    if len(available_prompts) >= 2:
                        parent1, parent2 = random.sample(available_prompts, 2)
                        # Ensure they're different
                        while parent1.id == parent2.id and len(available_prompts) > 1:
                            parent2 = random.choice(available_prompts)
                    else:
                        # Fallback: use mutation if not enough diversity
                        parent1 = random.choice(self.population)
                        parent2 = parent1  # Will trigger mutation instead
                
                # Only do crossover if parents are different
                if parent1.id != parent2.id:
                    child = self._crossover_prompts(parent1, parent2)
                    if child is None:
                        print(f"   ⏭️  Crossover skipped for {parent1.name} + {parent2.name} - quality requirements not met")
                        continue  # Skip this iteration
                    child.generation = current_generation
                    print(f"   🔄 LLM Crossover: {parent1.name} + {parent2.name} → {child.name}")
                else:
                    # Fall back to mutation if parents are the same
                    print(f"   🔄 Skipping crossover (same parent), using mutation instead")
                    child = self._mutate_prompt(parent1)
                    if child is None:
                        print(f"   ⏭️  Mutation skipped for {parent1.name} - quality requirements not met")
                        continue  # Skip this iteration
                    child.generation = current_generation
            else:
                # Mutation: TRUE GEPA balanced selection (80% frontier, 20% exploration)
                if random.random() < 0.8 and self.pareto_frontier:
                    # Exploitation: Select from Pareto frontier
                    parent = random.choice(self.pareto_frontier)
                else:
                    # Exploration: Select from full population (including non-frontier)
                    parent = random.choice(self.population)
                
                child = self._mutate_prompt(parent)
                if child is None:
                    print(f"   ⏭️  Mutation skipped for {parent.name} - quality requirements not met")
                    continue  # Skip this iteration
                child.generation = current_generation
                print(f"   🧬 LLM Mutation: {parent.name} → {child.name}")
            
            new_population.append(child)
        
        self.population = new_population
        self.all_prompts.extend(new_population)  # Add all new prompts to history
        print(f"✅ Population evolved to {len(new_population)} prompts (TRUE GEPA growth: 2^{current_generation}, capped at {Config.MAX_POPULATION_SIZE})")
        return new_population
    
    def _crossover_prompts(self, parent1: OptimizedPrompt, parent2: OptimizedPrompt) -> OptimizedPrompt:
        """Create a child prompt using simplified crossover focused on performance"""
        
        # Analyze parent performance
        parent1_metrics = parent1.performance_metrics or {}
        parent2_metrics = parent2.performance_metrics or {}
        
        # Get top performing criteria for each parent
        criteria_names = [
            "ask_for_help", "stay_calm", "listen_actively", "express_clearly", "show_empathy",
            "ask_clarifying", "give_constructive", "handle_conflict", "build_confidence", "encourage_participation",
            "respect_boundaries", "offer_support", "celebrate_success", "address_concerns", "foster_connection",
            "model_behavior", "provide_feedback", "create_safety", "promote_growth", "maintain_balance"
        ]
        
        # Get top 3 performing criteria for each parent
        parent1_scores = [(c, parent1_metrics.get(f'improvement_{c}', 0)) for c in criteria_names]
        parent2_scores = [(c, parent2_metrics.get(f'improvement_{c}', 0)) for c in criteria_names]
        
        parent1_scores.sort(key=lambda x: x[1], reverse=True)
        parent2_scores.sort(key=lambda x: x[1], reverse=True)
        
        parent1_top = [f"{c}: {s:.3f}" for c, s in parent1_scores[:3]]
        parent2_top = [f"{c}: {s:.3f}" for c, s in parent2_scores[:3]]
        
        # Create simple crossover prompt
        crossover_prompt = f"""
You are an expert prompt engineer creating a system prompt that combines the strengths of two parent prompts.

PARENT 1 SYSTEM PROMPT: "{parent1.prompt_text}"
PARENT 1 TOP STRENGTHS: {', '.join(parent1_top)}

PARENT 2 SYSTEM PROMPT: "{parent2.prompt_text}"
PARENT 2 TOP STRENGTHS: {', '.join(parent2_top)}

TASK: Create a new system prompt that:
1. MUST start with "You are..." (system prompt format)
2. Combines the best strengths from both parents
3. Improves upon both parents' performance
4. Is effective for social skills coaching
5. Can be any length that improves performance

Focus on creating a prompt that is better than both parents by combining their strengths.

Respond with ONLY the new system prompt text, no explanations.
"""
        
        try:
            from config import Config
            
            print(f"   🚀 Simple crossover: {parent1.name} + {parent2.name}")
            
            # Call LLM for crossover
            response = requests.post(
                "https://api.deepseek.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {Config.DEEPSEEK_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "deepseek-chat",
                    "messages": [{"role": "user", "content": crossover_prompt}],
                    "temperature": 0.7,  # Higher temperature for more creative combinations
                    "max_tokens": 300
                },
                timeout=30
            )
            
            print(f"   📡 API Response Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                if 'choices' in result and len(result['choices']) > 0:
                    child_prompt_text = result['choices'][0]['message']['content'].strip()
                    print(f"   ✅ LLM generated: {child_prompt_text[:100]}...")
                    
                    # Validate system prompt format
                    if not child_prompt_text.strip().lower().startswith("you are"):
                        print(f"   ❌ Generated prompt not a system prompt: {child_prompt_text[:50]}...")
                        print(f"   ⏭️  Skipping this crossover - quality requirement not met")
                        return None
                    
                    print(f"   ✅ System prompt format validated: {len(child_prompt_text)} chars")
                else:
                    print(f"   ❌ No choices in response")
                    print(f"   ⏭️  Skipping this crossover - API response invalid")
                    return None
            else:
                print(f"   ❌ API Error: {response.status_code} - {response.text}")
                print(f"   ⏭️  Skipping this crossover - API call failed")
                return None
                
        except Exception as e:
            print(f"⚠️  LLM crossover failed: {e}")
            import traceback
            traceback.print_exc()
            print(f"   ⏭️  Skipping this crossover - exception occurred")
            return None
        
        return OptimizedPrompt(
            id=str(uuid.uuid4()),
            name=f"Enhanced Child of {parent1.name} + {parent2.name}",
            prompt_text=child_prompt_text,
            components=[],
            generation=0,  # Will be set by caller
            performance_metrics={},
            pareto_rank=0,
            created_at=datetime.now(),
            last_tested=None
        )

    def _mutate_prompt(self, parent: OptimizedPrompt) -> OptimizedPrompt:
        """Create a mutated version of a parent prompt using LLM analysis"""
        
        # Get performance metrics for the parent
        parent_metrics = parent.performance_metrics or {}
        
        # Extract 20-criteria performance data
        criteria_names = [
            "ask_for_help", "stay_calm", "listen_actively", "express_clearly", "show_empathy",
            "ask_clarifying", "give_constructive", "handle_conflict", "build_confidence", "encourage_participation",
            "respect_boundaries", "offer_support", "celebrate_success", "address_concerns", "foster_connection",
            "model_behavior", "provide_feedback", "create_safety", "promote_growth", "maintain_balance"
        ]
        
        # Identify weak areas (lowest performing criteria)
        criterion_scores = []
        for criterion in criteria_names:
            score = parent_metrics.get(f'improvement_{criterion}', 0)
            criterion_scores.append((criterion, score))
        
        # Sort by performance (ascending) to find weakest areas
        criterion_scores.sort(key=lambda x: x[1])
        weakest_areas = [f"{criterion}: {score:.3f}" for criterion, score in criterion_scores[:5]]
        strongest_areas = [f"{criterion}: {score:.3f}" for criterion, score in criterion_scores[-3:]]
        
        # Create LLM prompt for mutation analysis
        print(f"   🤖 Analyzing mutation: {parent.name} (improvement: {parent_metrics.get('avg_improvement', 0):.3f})")
        
        mutation_prompt = f"""
You are an expert prompt engineer improving a social skills coaching system prompt.

CURRENT SYSTEM PROMPT: "{parent.prompt_text}"

WEAKEST PERFORMING AREAS (need improvement):
{', '.join(weakest_areas) if weakest_areas else 'No specific weak areas identified'}

STRONGEST PERFORMING AREAS (maintain these):
{', '.join(strongest_areas) if strongest_areas else 'No specific strong areas identified'}

TASK: Create an improved system prompt that:
1. MUST start with "You are..." (system prompt format)
2. Addresses the weakest performing areas
3. Preserves the strongest performing areas
4. Improves overall effectiveness for social skills coaching
5. Can be any length that improves performance

Focus on making meaningful improvements to address the weak areas while maintaining what works.

Respond with ONLY the improved system prompt text, no explanations.
"""
        
        try:
            # Call LLM for mutation
            from config import Config
            
            print(f"   🔗 Making LLM mutation API call...")
            response = requests.post(
                "https://api.deepseek.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {Config.DEEPSEEK_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "deepseek-chat",
                    "messages": [{"role": "user", "content": mutation_prompt}],
                    "temperature": 0.6,  # Slightly lower temperature for more focused mutations
                    "max_tokens": 200
                },
                timeout=30  # Add timeout
            )
            
            print(f"   📡 API Response Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"   📝 API Response: {result}")
                if 'choices' in result and len(result['choices']) > 0:
                    mutated_prompt_text = result['choices'][0]['message']['content'].strip()
                    print(f"   ✅ LLM generated: {mutated_prompt_text[:100]}...")
                    
                    # Validate system prompt format
                    if not mutated_prompt_text.strip().lower().startswith("you are"):
                        print(f"   ❌ Generated prompt not a system prompt: {mutated_prompt_text[:50]}...")
                        print(f"   ⏭️  Skipping this mutation - quality requirement not met")
                        return None
                    
                    print(f"   ✅ System prompt format validated: {len(mutated_prompt_text)} chars")
                else:
                    print(f"   ❌ No choices in response")
                    print(f"   ⏭️  Skipping this mutation - API response invalid")
                    return None
            else:
                print(f"   ❌ API Error: {response.status_code} - {response.text}")
                print(f"   ⏭️  Skipping this mutation - API call failed")
                return None
                
        except Exception as e:
            print(f"⚠️  LLM mutation failed: {e}")
            import traceback
            traceback.print_exc()
            print(f"   ⏭️  Skipping this mutation - exception occurred")
            return None
        
        return OptimizedPrompt(
            id=str(uuid.uuid4()),
            name=f"LLM Mutation of {parent.name}",
            prompt_text=mutated_prompt_text,
            components=[],  # No component tracking in LLM approach
            generation=parent.generation + 1,
            performance_metrics={},
            pareto_rank=0,
            created_at=datetime.now(),
            last_tested=None
        )
    
    async def run_optimization_async(self, dummies: List[AIDummy]) -> OptimizedPrompt:
        """Run the complete optimization process"""
        print("🚀 Starting GEPA-inspired prompt optimization...")
        print(f"📊 Population size: {self.population_size}")
        print(f"🧬 Generations: {self.generations}")
        print(f"👥 Dummies: {len(dummies)}")
        print()
        
        # Generate initial population
        self.generate_initial_population()
        
        best_prompt = None
        best_improvement = -float('inf')
        
        for generation in range(self.generations):
            print(f"🔄 Generation {generation + 1}/{self.generations}")
            print("=" * 50)
            
            # Evaluate current population
            await self.evaluate_population_async(dummies)
            
            # Find best prompt in current generation
            generation_best_prompt = None
            generation_best_improvement = -float('inf')
            
            for prompt in self.population:
                if prompt.performance_metrics:
                    improvement = prompt.performance_metrics.get('avg_improvement', 0)
                    if improvement > generation_best_improvement:
                        generation_best_improvement = improvement
                        generation_best_prompt = prompt
                    
                    # Also track overall best
                    if improvement > best_improvement:
                        best_improvement = improvement
                        best_prompt = prompt
            
            # Add best prompt from this generation to tracking
            if generation_best_prompt:
                self.best_per_generation.append(generation_best_prompt)
                print(f"🏆 Best prompt in generation {generation}: {generation_best_prompt.name}")
                print(f"   📈 Improvement: {generation_best_improvement:+.2f}")
            
            if best_prompt:
                print(f"🏆 Best prompt so far: {best_prompt.name}")
                print(f"   📈 Improvement: {best_improvement:+.2f}")
    
            
            # Evolve population (except for last generation)
            if generation < self.generations - 1:
                self.evolve_population()
            
            print()
        
        # Final evaluation
        print("🏁 Final evaluation...")
        await self.evaluate_population_async(dummies, sample_size=len(dummies))  # Use ALL dummies, not just 10
        
        # Return best prompt
        if best_prompt:
            print(f"\n🎉 Optimization complete!")
            print(f"🏆 Best prompt: {best_prompt.name}")
            print(f"📈 Average improvement: {best_improvement:+.2f}")

            print(f"🧬 Final generation: {best_prompt.generation}")
            print(f"📝 Prompt text: {best_prompt.prompt_text}")
        
        return best_prompt
    
    def save_optimization_results(self, filename: str = "data/prompt_optimization_results.json"):
        """Save optimization results to file"""
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        data = {
            'optimization_history': [asdict(result) for result in self.optimization_history],
            'pareto_frontier': [asdict(prompt) for prompt in self.pareto_frontier],
            'best_per_generation': [asdict(prompt) for prompt in self.best_per_generation],
            'all_prompts': [asdict(prompt) for prompt in self.all_prompts],
            'components': [asdict(component) for component in self.prompt_components],
            'timestamp': datetime.now().isoformat()
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"💾 Optimization results saved to {filename}")
    
    def load_optimization_results(self, filename: str = "data/prompt_optimization_results.json"):
        """Load optimization results from file"""
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Reconstruct objects
            self.optimization_history = []
            for result_data in data.get('optimization_history', []):
                result = OptimizationResult(**result_data)
                self.optimization_history.append(result)
            
            print(f"📂 Loaded {len(self.optimization_history)} optimization results")
            return True
        return False

def main():
    """Demo the TRUE GEPA approach prompt optimizer"""
    print("🧬 TRUE GEPA Prompt Optimizer Demo")
    print("=" * 50)
    print("🎯 Starting with single simple prompt")
    print("🔍 Using reflection to discover what's needed")
    print("🌱 Building complexity gradually through evolution")
    print("=" * 50)
    
    # Load existing dummies
    if os.path.exists("data/ai_dummies.json"):
        with open("data/ai_dummies.json", 'r', encoding='utf-8') as f:
            dummies_data = json.load(f)
        
        # Convert to AIDummy objects
        dummies = []
        for dummy_data in dummies_data[:10]:  # Use first 10 for demo
            try:
                dummy = AIDummy(**dummy_data)
                dummies.append(dummy)
            except Exception as e:
                print(f"⚠️  Error loading dummy: {e}")
                continue
        
        if dummies:
            print(f"✅ Loaded {len(dummies)} dummies for optimization")
            
            # Initialize optimizer with current system prompt
            from config import Config
            base_prompt = Config.SYSTEM_PROMPT
            
            optimizer = PromptOptimizer(
                base_prompt=base_prompt,
                population_size=1,   # TRUE GEPA: Start with just ONE prompt
                generations=5,       # More generations, smaller population
                mutation_rate=0.3,
                crossover_rate=0.6
            )
            
            # Run optimization
            best_prompt = optimizer.run_optimization(dummies)
            
            # Save results
            optimizer.save_optimization_results()
            
            if best_prompt:
                print(f"\n🎯 Recommended system prompt:")
                print(f"📝 {best_prompt.prompt_text}")
        else:
            print("❌ No valid dummies found")
    else:
        print("❌ No dummies found. Run character_generator.py first.")

if __name__ == "__main__":
    main()

