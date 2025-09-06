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
    
    def get_character_summary(self) -> str:
        """Get a concise character summary for AI interactions"""
        dominant_traits = self.personality.get_dominant_traits()
        anxiety_category = self.social_anxiety.get_anxiety_category()
        
        return f"""You are {self.name}, a {self.age}-year-old {self.student_type} studying {self.major} at {self.university}. 
        Your personality is characterized by high {', '.join(dominant_traits)}. 
        You experience {anxiety_category} social anxiety and struggle with {', '.join(self.challenges)}. 
        Your main fears include {', '.join(self.fears[:2])}. 
        You want to improve your {', '.join(self.goals[:2])}."""

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
