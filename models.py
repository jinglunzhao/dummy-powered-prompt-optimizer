"""
Data models for the AI Dummy Social Skills Testing System
"""
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from datetime import datetime
import uuid

class PersonalityProfile(BaseModel):
    """Personality profile based on Big Five model"""
    extraversion: int = Field(..., ge=1, le=10)
    agreeableness: int = Field(..., ge=1, le=10)
    conscientiousness: int = Field(..., ge=1, le=10)
    neuroticism: int = Field(..., ge=1, le=10)
    openness: int = Field(..., ge=1, le=10)
    
    def get_dominant_traits(self) -> List[str]:
        """Get the most prominent personality traits"""
        traits = {
            "extraversion": self.extraversion,
            "agreeableness": self.agreeableness,
            "conscientiousness": self.conscientiousness,
            "neuroticism": self.neuroticism,
            "openness": self.openness
        }
        sorted_traits = sorted(traits.items(), key=lambda x: x[1], reverse=True)
        return [trait for trait, score in sorted_traits[:3]]

class SocialAnxietyProfile(BaseModel):
    """Social anxiety profile"""
    anxiety_level: int = Field(..., ge=1, le=10)
    social_comfort: int = Field(..., ge=1, le=10)
    communication_style: str
    triggers: List[str] = Field(default_factory=list)
    
    def get_anxiety_category(self) -> str:
        """Get anxiety level category"""
        if self.anxiety_level <= 3:
            return "low"
        elif self.anxiety_level <= 6:
            return "moderate"
        elif self.anxiety_level <= 9:
            return "high"
        else:
            return "severe"

class EvolutionStage(BaseModel):
    """One stage of personality evolution during a conversation"""
    stage_number: int
    prompt_id: str
    prompt_name: str
    generation: int
    conversation_id: str
    conversation_summary: str
    
    # Materialized traits (abstract → concrete)
    fears_materialized: Dict[str, str] = Field(default_factory=dict)  # "social rejection" → "not being invited to study groups"
    challenges_materialized: Dict[str, str] = Field(default_factory=dict)  # "starting conversations" → "approaching someone in cafeteria"
    behaviors_detailed: Dict[str, str] = Field(default_factory=dict)  # "avoiding eye contact" → "looking at phone when people approach"
    triggers_specified: Dict[str, str] = Field(default_factory=dict)  # "crowded rooms" → "dining hall during peak hours"
    
    # Accepted solutions and progress indicators
    accepted_solutions: Dict[str, str] = Field(default_factory=dict)  # "networking fear" → "start with LinkedIn messages to 2 people per week"
    progress_indicators: Dict[str, str] = Field(default_factory=dict)  # "social anxiety" → "practiced speaking up in class 3 times this week"
    action_plans: Dict[str, str] = Field(default_factory=dict)  # "time management" → "use Pomodoro technique for 25min study blocks"
    
    # Anxiety level changes
    anxiety_change: float = 0.0  # -0.5 (decreased by half a point)
    new_anxiety_level: float = 0.0
    
    # Assessment impact
    pre_assessment_score: float = 0.0
    post_assessment_score: float = 0.0
    improvement_score: float = 0.0
    
    timestamp: datetime = Field(default_factory=datetime.now)

class ConversationBasedProfile(BaseModel):
    """Profile that evolves during conversations but resets between prompt tests"""
    
    # Original (Static - Never Changes)
    original_fears: List[str]
    original_challenges: List[str]
    original_behaviors: List[str]
    original_anxiety_triggers: List[str]
    original_social_anxiety_level: int
    original_big_five: PersonalityProfile
    
    # Current (Dynamic - Changes During Conversation)
    current_fears: List[str]
    current_challenges: List[str]
    current_behaviors: List[str]
    current_anxiety_triggers: List[str]
    current_social_anxiety_level: int
    current_big_five: PersonalityProfile
    
    # Evolution tracking
    evolution_stages: List[EvolutionStage] = Field(default_factory=list)
    current_stage: int = 0
    
    def reset_to_original(self) -> None:
        """Reset current profile to original for fair comparison between prompt tests"""
        self.current_fears = self.original_fears.copy()
        self.current_challenges = self.original_challenges.copy()
        self.current_behaviors = self.original_behaviors.copy()
        self.current_anxiety_triggers = self.original_anxiety_triggers.copy()
        self.current_social_anxiety_level = self.original_social_anxiety_level
        self.current_big_five = self.original_big_five
    
    def apply_evolution_stage(self, stage: EvolutionStage) -> None:
        """Apply a new evolution stage to current profile"""
        # Update materialized traits
        self.current_fears = [stage.fears_materialized.get(fear, fear) for fear in self.original_fears]
        self.current_challenges = [stage.challenges_materialized.get(challenge, challenge) for challenge in self.original_challenges]
        self.current_behaviors = [stage.behaviors_detailed.get(behavior, behavior) for behavior in self.original_behaviors]
        self.current_anxiety_triggers = [stage.triggers_specified.get(trigger, trigger) for trigger in self.original_anxiety_triggers]
        
        # Update anxiety level
        self.current_social_anxiety_level = max(1, min(10, int(stage.new_anxiety_level)))
        
        # Add to evolution history
        self.evolution_stages.append(stage)
        self.current_stage = len(self.evolution_stages)
    
    def get_current_profile_for_assessment(self) -> Dict[str, Any]:
        """Get current evolved profile for assessment"""
        return {
            "fears": self.current_fears,
            "challenges": self.current_challenges,
            "behaviors": self.current_behaviors,
            "anxiety_triggers": self.current_anxiety_triggers,
            "social_anxiety_level": self.current_social_anxiety_level,
            "big_five": self.current_big_five
        }

class PersonalityEvolution(BaseModel):
    """
    Complete personality evolution system for a dummy across all experiments
    
    This replaces the old simple evolution system with a comprehensive
    conversation-based evolution that materializes traits and tracks full history.
    """
    dummy_id: str
    dummy_name: str
    
    # Current conversation-based profile
    conversation_profile: ConversationBasedProfile
    
    # Experiment tracking
    current_experiment_id: Optional[str] = None
    current_prompt_id: Optional[str] = None
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.now)
    last_updated: datetime = Field(default_factory=datetime.now)
    
    def start_new_prompt_test(self, experiment_id: str, prompt_id: str, prompt_name: str) -> None:
        """Start a new prompt test - reset profile for fair comparison"""
        self.current_experiment_id = experiment_id
        self.current_prompt_id = prompt_id
        self.conversation_profile.reset_to_original()
        self.last_updated = datetime.now()
        print(f"🔄 Reset {self.dummy_name}'s personality for prompt test: {prompt_name}")
    
    def add_evolution_stage(self, stage: EvolutionStage) -> None:
        """Add a new evolution stage from a conversation"""
        self.conversation_profile.apply_evolution_stage(stage)
        self.last_updated = datetime.now()
        print(f"🧬 {self.dummy_name} evolved: {stage.conversation_summary[:50]}...")
    
    def get_evolution_timeline(self) -> List[Dict[str, Any]]:
        """Get evolution timeline for web interface visualization"""
        timeline = []
        for i, stage in enumerate(self.conversation_profile.evolution_stages):
            timeline.append({
                "stage_number": stage.stage_number,
                "prompt_name": stage.prompt_name,
                "generation": stage.generation,
                "conversation_summary": stage.conversation_summary,
                "anxiety_level": stage.new_anxiety_level,
                "improvement_score": stage.improvement_score,
                "timestamp": stage.timestamp.isoformat(),
                "materialized_traits": {
                    "fears": stage.fears_materialized,
                    "challenges": stage.challenges_materialized,
                    "behaviors": stage.behaviors_detailed,
                    "triggers": stage.triggers_specified
                }
            })
        return timeline

class AIDummy(BaseModel):
    """AI Dummy character for social skills testing"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    age: int = Field(..., ge=17, le=26)  # College student age range
    gender: str
    university: str
    major: str
    student_type: str  # Undergraduate or Graduate
    personality: PersonalityProfile
    social_anxiety: SocialAnxietyProfile
    fears: List[str]
    goals: List[str]
    challenges: List[str]
    behaviors: List[str]
    created_at: datetime = Field(default_factory=datetime.now)
    
    # Personality evolution system (optional)
    personality_evolution: Optional[PersonalityEvolution] = None
    
    def get_character_summary(self) -> str:
        """Get a concise character summary for AI interactions"""
        # Use evolved personality if available and enabled, otherwise use original
        if self.personality_evolution and self._is_personality_evolution_enabled():
            # Use current evolved profile
            current_profile = self.personality_evolution.conversation_profile
            personality_to_use = current_profile.current_big_five
            fears_to_use = current_profile.current_fears
            challenges_to_use = current_profile.current_challenges
            anxiety_level = current_profile.current_social_anxiety_level
        else:
            # Use original profile
            personality_to_use = self.personality
            fears_to_use = self.fears
            challenges_to_use = self.challenges
            anxiety_level = self.social_anxiety.anxiety_level
        
        dominant_traits = personality_to_use.get_dominant_traits()
        anxiety_category = "low" if anxiety_level <= 3 else "moderate" if anxiety_level <= 6 else "high" if anxiety_level <= 9 else "severe"
        
        return f"""You are {self.name}, a {self.age}-year-old {self.student_type} studying {self.major} at {self.university}. 
        Your personality is characterized by high {', '.join(dominant_traits)}. 
        You experience {anxiety_category} social anxiety and struggle with {', '.join(challenges_to_use)}. 
        Your main fears include {', '.join(fears_to_use[:2])}. 
        You want to improve your {', '.join(self.goals[:2])}."""
    
    def _is_personality_evolution_enabled(self) -> bool:
        """Check if personality evolution is enabled in config"""
        try:
            from config import Config
            return Config.ENABLE_PERSONALITY_EVOLUTION
        except ImportError:
            return False
    
    def initialize_personality_evolution(self) -> None:
        """Initialize personality evolution tracking with conversation-based profile"""
        if not self._is_personality_evolution_enabled():
            return  # Skip initialization if disabled
        
        if not self.personality_evolution:
            # Create conversation-based profile from current dummy data
            conversation_profile = ConversationBasedProfile(
                # Original (static) traits
                original_fears=self.fears.copy(),
                original_challenges=self.challenges.copy(),
                original_behaviors=self.behaviors.copy(),
                original_anxiety_triggers=self.social_anxiety.triggers.copy(),
                original_social_anxiety_level=self.social_anxiety.anxiety_level,
                original_big_five=self.personality,
                
                # Current (dynamic) traits - start same as original
                current_fears=self.fears.copy(),
                current_challenges=self.challenges.copy(),
                current_behaviors=self.behaviors.copy(),
                current_anxiety_triggers=self.social_anxiety.triggers.copy(),
                current_social_anxiety_level=self.social_anxiety.anxiety_level,
                current_big_five=self.personality
            )
            
            self.personality_evolution = PersonalityEvolution(
                dummy_id=self.id,
                dummy_name=self.name,
                conversation_profile=conversation_profile
            )
            print(f"🧬 Initialized personality evolution for {self.name}")
    
    def start_new_prompt_test(self, experiment_id: str, prompt_id: str, prompt_name: str) -> None:
        """Start a new prompt test - reset personality for fair comparison"""
        if not self._is_personality_evolution_enabled():
            return
        
        if not self.personality_evolution:
            self.initialize_personality_evolution()
        
        if self.personality_evolution:
            self.personality_evolution.start_new_prompt_test(experiment_id, prompt_id, prompt_name)
    
    def get_current_profile_for_assessment(self) -> Dict[str, Any]:
        """Get current evolved profile for assessment"""
        if self.personality_evolution and self._is_personality_evolution_enabled():
            return self.personality_evolution.conversation_profile.get_current_profile_for_assessment()
        else:
            # Return original profile if evolution disabled
            return {
                "fears": self.fears,
                "challenges": self.challenges,
                "behaviors": self.behaviors,
                "anxiety_triggers": self.social_anxiety.triggers,
                "social_anxiety_level": self.social_anxiety.anxiety_level,
                "big_five": self.personality
            }
    
    def add_evolution_stage(self, stage: EvolutionStage) -> None:
        """Add a new evolution stage from a conversation"""
        if not self._is_personality_evolution_enabled():
            return
        
        if not self.personality_evolution:
            self.initialize_personality_evolution()
        
        if self.personality_evolution:
            self.personality_evolution.add_evolution_stage(stage)
    
    def get_evolution_timeline(self) -> List[Dict[str, Any]]:
        """Get evolution timeline for web interface"""
        if self.personality_evolution and self._is_personality_evolution_enabled():
            return self.personality_evolution.get_evolution_timeline()
        else:
            return []

class AssessmentResponse(BaseModel):
    """Response to a social skills assessment question"""
    question: str
    score: int = Field(..., ge=1, le=10)
    confidence: int = Field(..., ge=1, le=10)
    notes: Optional[str] = None

class Assessment(BaseModel):
    """Complete social skills assessment"""
    dummy_id: str
    timestamp: datetime = Field(default_factory=datetime.now)
    responses: List[AssessmentResponse]
    total_score: float
    average_score: float
    improvement_areas: List[str]
    
    @classmethod
    def calculate_scores(cls, responses: List[AssessmentResponse]) -> Dict[str, float]:
        """Calculate assessment scores"""
        scores = [r.score for r in responses]
        return {
            "total_score": sum(scores),
            "average_score": sum(scores) / len(scores) if scores else 0
        }

class ConversationTurn(BaseModel):
    """A single turn in a conversation"""
    speaker: str  # "ai" or "dummy"
    message: str  # The actual message spoken
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    # AI-specific fields (only populated when speaker is "ai")
    ai_reasoning: Optional[str] = Field(default=None, description="AI's Chain of Thought reasoning")
    ai_final_response: Optional[str] = Field(default=None, description="AI's final conversational response")
    
    def __init__(self, **data):
        super().__init__(**data)
        # If this is an AI turn and we have both reasoning and final response, use final response as message
        if self.speaker == "ai" and self.ai_reasoning and self.ai_final_response:
            self.message = self.ai_final_response
        # If this is an AI turn with only reasoning, use reasoning as message (fallback)
        elif self.speaker == "ai" and self.ai_reasoning and not self.ai_final_response:
            self.message = self.ai_reasoning

class Conversation(BaseModel):
    """Complete conversation between AI dummy and AI model"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    dummy_id: str
    scenario: str
    system_prompt: str
    turns: List[ConversationTurn]
    start_time: datetime = Field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    
    def add_turn(self, speaker: str, message: str, metadata: Dict[str, Any] = None):
        """Add a turn to the conversation"""
        if metadata is None:
            metadata = {}
        
        turn = ConversationTurn(
            speaker=speaker,
            message=message,
            metadata=metadata
        )
        
        # If this is an AI turn and we have reasoning data in metadata, store it
        if speaker == "ai" and metadata:
            if "ai_reasoning" in metadata:
                turn.ai_reasoning = metadata["ai_reasoning"]
            if "ai_final_response" in metadata:
                turn.ai_final_response = metadata["ai_final_response"]
        
        self.turns.append(turn)
    
    def get_conversation_text(self) -> str:
        """Get conversation as formatted text"""
        text = f"Scenario: {self.scenario}\n\n"
        for turn in self.turns:
            speaker_label = "AI Assistant" if turn.speaker == "ai" else "Student"
            text += f"{speaker_label}: {turn.message}\n\n"
        return text

class TestSession(BaseModel):
    """Complete test session for a dummy"""
    dummy_id: str
    pre_assessment: Assessment
    conversations: List[Conversation]
    post_assessment: Assessment
    improvement_score: float
    session_duration: float
    
    @classmethod
    def calculate_improvement(cls, pre: Assessment, post: Assessment) -> float:
        """Calculate improvement score"""
        return post.average_score - pre.average_score

class SystemPrompt(BaseModel):
    """System prompt configuration for testing"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    prompt: str
    version: str
    created_at: datetime = Field(default_factory=datetime.now)
    performance_metrics: Optional[Dict[str, Any]] = None
