"""
Configuration file for the AI Dummy Social Skills Testing System
"""
import os
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables
# load_dotenv()  # Disabled to avoid encoding issues

class Config:
    """Configuration class for the system"""
    
    # AI API Configuration (DeepSeek)
    OPENAI_API_KEY = "sk-d64d89acb0904956a4f5e37d512ae950"  # Direct API key
    DEEPSEEK_API_KEY = "sk-d64d89acb0904956a4f5e37d512ae950"  # Same key for DeepSeek API
    OPENAI_MODEL = "deepseek-chat"  # Use for conversations (cheaper, direct responses)
    DEEPSEEK_REASONER_MODEL = "deepseek-reasoner"  # Use for prompt generation, reflections, synthesis (better reasoning)
    
    # Default System Prompt
    SYSTEM_PROMPT = "You are a supportive AI assistant helping students improve their social skills. Be encouraging, provide practical advice, and help them build confidence gradually."
    
    # System Configuration
    NUM_DUMMIES = 100
    CONVERSATION_ROUNDS = 5
    MAX_TOKENS_PER_RESPONSE = 300  # Increased for DeepSeek R1 reasoning
    MAX_POPULATION_SIZE = 20  # Maximum number of prompts per generation
    
    # Feature Toggles
    ENABLE_PERSONALITY_EVOLUTION = True  # Toggle for dummy personality evolution during conversations
    
    # Character Generation Parameters
    PERSONALITY_DIMENSIONS = {
        "extraversion": {"min": 1, "max": 10, "description": "Outgoing vs. Reserved"},
        "agreeableness": {"min": 1, "max": 10, "description": "Friendly vs. Challenging"},
        "conscientiousness": {"min": 1, "max": 10, "description": "Organized vs. Careless"},
        "neuroticism": {"min": 1, "max": 10, "description": "Sensitive vs. Secure"},
        "openness": {"min": 1, "max": 10, "description": "Curious vs. Conventional"}
    }
    
    # Social Anxiety Levels
    ANXIETY_LEVELS = {
        "low": {"range": (1, 3), "description": "Minimal social anxiety"},
        "moderate": {"range": (4, 6), "description": "Moderate social anxiety"},
        "high": {"range": (7, 9), "description": "High social anxiety"},
        "severe": {"range": (10, 10), "description": "Severe social anxiety"}
    }
    
    # Social Skills Assessment Questions (4-point scale: 1=not true, 2=somewhat true, 3=mostly true, 4=very true)
    SOCIAL_SKILLS_QUESTIONS = [
        "I ask for help when I need it.",
        "I stay calm when dealing with problems.",
        "I help my friends when they are having a problem.",
        "I work well with my classmates.",
        "I do the right thing without being told.",
        "I do my part in a group.",
        "I stay calm when I disagree with others.",
        "I stand up for others when they are not treated well.",
        "I look at people when I talk to them.",
        "I am careful when I use things that aren't mine.",
        "I let people know when there's a problem.",
        "I pay attention when the teacher talks to the class.",
        "I try to make others feel better.",
        "I say \"thank you\" when someone helps me.",
        "I keep my promises.",
        "I pay attention when others present their ideas.",
        "I try to find a good way to end a disagreement.",
        "I try to think about how others feel.",
        "I try to forgive others when they say \"sorry\".",
        "I follow school rules."
    ]
    
    # File Paths
    DATA_DIR = "data"
    DUMMIES_FILE = "ai_dummies.json"
    CONVERSATIONS_FILE = "conversations.json"
    ASSESSMENTS_FILE = "assessments.json"
    RESULTS_FILE = "results.json"
    
    @classmethod
    def validate(cls) -> bool:
        """Validate configuration"""
        if not cls.OPENAI_API_KEY:
            print("Warning: OPENAI_API_KEY not found in environment variables")
            return False
        return True
