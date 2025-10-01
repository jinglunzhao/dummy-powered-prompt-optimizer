"""
Personality Materializer Service

Uses LLM to analyze conversations and materialize abstract personality traits
into concrete, tangible situations and behaviors.
"""

import asyncio
import aiohttp
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from models import EvolutionStage, Conversation

class PersonalityMaterializer:
    """LLM-based service for materializing personality traits from conversations"""
    
    def __init__(self, api_key: str = None):
        from config import Config
        self.api_key = api_key or Config.DEEPSEEK_API_KEY
        if not self.api_key:
            raise ValueError("API key is required for personality materializer")
        
        print("✅ Personality Materializer initialized")
    
    async def materialize_personality_from_conversation(self, 
                                                      dummy, 
                                                      conversation: Conversation,
                                                      prompt_id: str,
                                                      prompt_name: str,
                                                      generation: int,
                                                      pre_assessment_score: float = 0.0,
                                                      post_assessment_score: float = 0.0) -> Optional[EvolutionStage]:
        """Analyze conversation and materialize personality traits"""
        
        print(f"🧠 Materializing personality for {dummy.name} after conversation...")
        
        # Create materialization prompt
        materialization_prompt = self._create_materialization_prompt(dummy, conversation)
        
        try:
            # Call DeepSeek Reasoner for materialization
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "https://api.deepseek.com/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "deepseek-chat",
                        "messages": [{"role": "user", "content": materialization_prompt}],
                        "temperature": 0.3,  # Low temperature for focused analysis
                        "max_tokens": 2000   # Enough for detailed materialization
                    },
                    timeout=180
                ) as response:
                    
                    if response.status == 200:
                        result = await response.json()
                        print(f"🔍 API Response received: {len(str(result))} chars")
                        
                        if 'choices' in result and len(result['choices']) > 0:
                            message = result['choices'][0]['message']
                            # DeepSeek Reasoner puts the actual response in 'reasoning_content' or 'content'
                            materialization_text = (message.get('reasoning_content') or message.get('content') or '').strip()
                            print(f"📝 Materialization text: {len(materialization_text)} chars")
                            print(f"📄 Text preview: {materialization_text[:200]}...")
                            
                            # Parse the materialization response
                            materialization_data = self._parse_materialization_response(materialization_text)
                            print(f"🔍 Parsed data keys: {list(materialization_data.keys())}")
                            
                            # Create evolution stage
                            evolution_stage = EvolutionStage(
                                stage_number=dummy.personality_evolution.conversation_profile.current_stage + 1 if dummy.personality_evolution else 1,
                                prompt_id=prompt_id,
                                prompt_name=prompt_name,
                                generation=generation,
                                conversation_id=conversation.id,
                                conversation_summary=materialization_data.get("conversation_summary", "No summary available"),
                                
                                fears_materialized=materialization_data.get("fears_materialized", {}),
                                challenges_materialized=materialization_data.get("challenges_materialized", {}),
                                behaviors_detailed=materialization_data.get("behaviors_detailed", {}),
                                triggers_specified=materialization_data.get("triggers_specified", {}),
                                
                                anxiety_change=materialization_data.get("anxiety_change", 0.0),
                                new_anxiety_level=materialization_data.get("new_anxiety_level", dummy.social_anxiety.anxiety_level),
                                
                                pre_assessment_score=pre_assessment_score,
                                post_assessment_score=post_assessment_score,
                                improvement_score=post_assessment_score - pre_assessment_score
                            )
                            
                            print(f"✅ Materialized {dummy.name}'s personality: {evolution_stage.conversation_summary[:50]}...")
                            return evolution_stage
                        else:
                            print(f"❌ No materialization response from DeepSeek Reasoner")
                            print(f"🔍 Response structure: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
                            return None
                    else:
                        error_text = await response.text()
                        print(f"❌ DeepSeek Reasoner API Error: {response.status}")
                        print(f"🔍 Error details: {error_text[:500]}")
                        return None
                        
        except Exception as e:
            print(f"⚠️  Personality materialization failed: {e}")
            print("❌ Returning None - no fallback mechanism")
            return None
    
    def _create_materialization_prompt(self, dummy, conversation: Conversation) -> str:
        """Create prompt for personality materialization"""
        
        # Get conversation text
        conversation_text = ""
        for turn in conversation.turns:
            speaker_label = "AI Coach" if turn.speaker == "ai" else dummy.name
            conversation_text += f"{speaker_label}: {turn.message}\n"
        
        return f"""
You are an expert psychologist analyzing a conversation between a social skills coach and a student to understand how the student's personality traits have been materialized (made more concrete and tangible) through the interaction.

STUDENT: {dummy.name}
ORIGINAL ABSTRACT TRAITS:
- Fears: {', '.join(dummy.fears)}
- Challenges: {', '.join(dummy.challenges)}
- Behaviors: {', '.join(dummy.behaviors)}
- Anxiety Triggers: {', '.join(dummy.social_anxiety.triggers)}
- Social Anxiety Level: {dummy.social_anxiety.anxiety_level}/10

CONVERSATION:
{conversation_text}

TASK: Based on this conversation, analyze how the student's abstract traits have become more concrete and specific. The goal is NOT to change the traits completely, but to make them more tangible and specific based on what emerged during the conversation.

For each category, provide specific materializations:

1. FEAR MATERIALIZATION:
   - Take each abstract fear and identify SPECIFIC situations or concerns that emerged in the conversation
   - Example: "social rejection" → "fear of not being included in study group after asking to join"
   - Format: {{"original_fear": "specific_situation"}}

2. CHALLENGE MATERIALIZATION:
   - Take each abstract challenge and identify SPECIFIC instances or scenarios that came up
   - Example: "starting conversations" → "approaching someone in the cafeteria to ask about homework"
   - Format: {{"original_challenge": "specific_scenario"}}

3. BEHAVIOR MATERIALIZATION:
   - Take each abstract behavior and add SPECIFIC details that emerged
   - Example: "avoiding eye contact" → "looking down at phone when people try to start conversations"
   - Format: {{"original_behavior": "specific_behavior"}}

4. TRIGGER SPECIFICATION:
   - Take each abstract trigger and identify SPECIFIC contexts or situations
   - Example: "crowded rooms" → "the student union dining hall during lunch hour"
   - Format: {{"original_trigger": "specific_context"}}

5. ANXIETY ASSESSMENT:
   - Did the student's social anxiety level change during the conversation? 
   - If yes, by how much? (Range: -3.0 to +1.0, negative means anxiety decreased)
   - New anxiety level: (1-10)

6. CONVERSATION SUMMARY:
   - Brief 2-3 sentence summary of what was discussed and how the student responded

RESPONSE FORMAT (JSON ONLY):
{{
    "fears_materialized": {{"social rejection": "specific situation"}},
    "challenges_materialized": {{"starting conversations": "specific scenario"}},
    "behaviors_detailed": {{"avoiding eye contact": "specific behavior"}},
    "triggers_specified": {{"crowded rooms": "specific context"}},
    "anxiety_change": -0.5,
    "new_anxiety_level": 7.5,
    "conversation_summary": "Brief summary of what happened"
}}

CRITICAL INSTRUCTIONS:
1. Your response must be ONLY the JSON object above - no explanations, no reasoning, no additional text
2. Only materialize traits that were actually discussed or emerged in the conversation
3. Keep the same core meaning but make it more specific and concrete
4. If a trait wasn't mentioned, don't include it in the materialization
5. Focus on making abstract concepts more tangible, not changing them completely
6. Start your response with {{ and end with }} - nothing else
"""
    
    def _parse_materialization_response(self, response_text: str) -> Dict[str, Any]:
        """Parse the materialization response from LLM"""
        try:
            # Try to extract JSON from the response
            if "```json" in response_text:
                # Extract JSON from code block
                start = response_text.find("```json") + 7
                end = response_text.find("```", start)
                json_text = response_text[start:end].strip()
            elif "{" in response_text and "}" in response_text:
                # Extract JSON from response
                start = response_text.find("{")
                end = response_text.rfind("}") + 1
                json_text = response_text[start:end]
            else:
                print(f"⚠️  Could not find JSON in materialization response")
                return self._create_fallback_materialization()
            
            # Parse JSON
            materialization_data = json.loads(json_text)
            
            # Validate required fields
            required_fields = ["fears_materialized", "challenges_materialized", "behaviors_detailed", "triggers_specified", "conversation_summary"]
            for field in required_fields:
                if field not in materialization_data:
                    materialization_data[field] = {}
            
            # Ensure anxiety fields are present
            if "anxiety_change" not in materialization_data:
                materialization_data["anxiety_change"] = 0.0
            if "new_anxiety_level" not in materialization_data:
                materialization_data["new_anxiety_level"] = 8.0  # Default
            
            return materialization_data
            
        except json.JSONDecodeError as e:
            print(f"⚠️  Failed to parse materialization JSON: {e}")
            print(f"Response text: {response_text[:200]}...")
            return self._create_fallback_materialization()
        except Exception as e:
            print(f"⚠️  Error parsing materialization response: {e}")
            return self._create_fallback_materialization()
    
    def _create_fallback_materialization(self) -> Dict[str, Any]:
        """Create fallback materialization when LLM parsing fails"""
        return {
            "fears_materialized": {},
            "challenges_materialized": {},
            "behaviors_detailed": {},
            "triggers_specified": {},
            "anxiety_change": 0.0,
            "new_anxiety_level": 8.0,
            "conversation_summary": "Conversation analysis unavailable - fallback materialization used"
        }

# Global materializer instance
personality_materializer = PersonalityMaterializer()

async def main():
    """Test the personality materializer"""
    print("Testing Personality Materializer...")
    
    # This would be tested with actual conversation data
    print("Materializer ready for use")

if __name__ == "__main__":
    asyncio.run(main())
