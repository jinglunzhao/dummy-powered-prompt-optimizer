# Personality Evolution System - Implementation Design

## Core Principles (Based on User Requirements)

1. **Per-Conversation Evolution**: Personality evolves DURING each conversation, then resets for fair comparison
2. **Materialization, Not Jumps**: Fears/challenges become more CONCRETE and TANGIBLE, not discrete state changes
3. **Pre-Assessment Evolution**: Update personality BEFORE each assessment based on conversation
4. **Unified Evaluation**: Personality growth IS prompt effectiveness - measure it together

## Architecture

### 1. Data Structures

```python
class ConversationBasedProfile(BaseModel):
    """Profile that evolves during a conversation"""
    # Original (Static - Never Changes)
    original_fears: List[str]
    original_challenges: List[str]
    original_behaviors: List[str]
    original_anxiety_triggers: List[str]
    original_social_anxiety_level: int
    
    # Evolved (Dynamic - Changes During Conversation)
    current_fears: List[str]  # Made more concrete/specific
    current_challenges: List[str]  # Made more tangible
    current_behaviors: List[str]  # Made more detailed
    current_anxiety_triggers: List[str]  # Made more specific
    current_social_anxiety_level: int  # Can decrease
    
    # Big Five (Mostly Stable - Rare Changes)
    original_big_five: PersonalityProfile
    current_big_five: PersonalityProfile
    
    # Evolution Tracking
    evolution_history: List[EvolutionStage]
    conversation_summary: str  # Brief summary for backtracking

class EvolutionStage(BaseModel):
    """One stage of personality evolution"""
    stage_number: int
    prompt_id: str
    prompt_name: str
    generation: int
    conversation_summary: str
    
    # Changes (materialization)
    fears_materialized: Dict[str, str]  # "social rejection" -> "fear of not being invited to study groups"
    challenges_materialized: Dict[str, str]  # "starting conversations" -> "approaching someone in the cafeteria"
    behaviors_detailed: Dict[str, str]  # "avoiding eye contact" -> "looking at phone when people approach"
    triggers_specified: Dict[str, str]  # "crowded rooms" -> "dining hall during peak hours"
    anxiety_change: float  # -0.5 (decreased by half a point)
    
    timestamp: datetime
```

### 2. Evolution Flow

```
BEFORE CONVERSATION:
1. Load dummy with original (static) profile
2. Reset current profile to original (fair comparison)

DURING CONVERSATION:
3. Have conversation with chatbot (5 rounds)
4. LLM analyzes conversation for personality insights
5. LLM materializes fears/challenges (makes them specific)
6. Update current profile with materialized traits
7. Generate brief conversation summary

BEFORE ASSESSMENT:
8. Use CURRENT (evolved) profile for assessment
9. Assessment reflects personality growth from conversation

AFTER ASSESSMENT:
10. Store evolution stage (for backtracking)
11. Calculate improvement (original vs evolved assessment)

FOR NEXT PROMPT TEST:
12. Reset current profile to original
13. Repeat process (fair comparison)
```

### 3. LLM-Based Materialization

```python
async def materialize_personality(dummy: AIDummy, conversation: Conversation) -> Dict[str, Any]:
    """Use LLM to analyze conversation and materialize personality traits"""
    
    prompt = f"""
Analyze this conversation between {dummy.name} and a social skills coach.

ORIGINAL PROFILE (abstract):
- Fears: {dummy.fears}
- Challenges: {dummy.challenges}
- Behaviors: {dummy.behaviors}
- Anxiety Triggers: {dummy.social_anxiety.triggers}
- Social Anxiety Level: {dummy.social_anxiety.anxiety_level}/10

CONVERSATION:
{conversation.get_conversation_text()}

TASK: Based on the conversation, make these traits MORE CONCRETE and TANGIBLE:

1. FEAR MATERIALIZATION:
   - For each abstract fear, identify a SPECIFIC situation or concern that emerged
   - Example: "social rejection" → "not being invited to the study group after asking"

2. CHALLENGE MATERIALIZATION:
   - For each challenge, identify SPECIFIC instances or scenarios
   - Example: "starting conversations" → "asking the person next to me about the homework"

3. BEHAVIOR MATERIALIZATION:
   - For each behavior, add SPECIFIC details that emerged
   - Example: "avoiding eye contact" → "looking down at notes when someone tries to talk"

4. TRIGGER SPECIFICATION:
   - For each trigger, identify SPECIFIC contexts
   - Example: "crowded rooms" → "the student union during lunch hour"

5. ANXIETY ASSESSMENT:
   - Did social anxiety decrease during the conversation? By how much (0.0-3.0)?

6. CONVERSATION SUMMARY:
   - Brief 2-3 sentence summary of what was discussed

Return JSON with materialized traits and changes.
"""
    
    # Call LLM for materialization
    response = await call_deepseek_reasoner(prompt)
    return parse_materialization_response(response)
```

### 4. Frontend Visualization

```javascript
// Personality Evolution Timeline
{
  "dummy": "Alex Lewis",
  "original_profile": {
    "fears": ["social rejection", "being judged"],
    "challenges": ["starting conversations"],
    "anxiety_level": 8
  },
  "evolution_stages": [
    {
      "stage": 0,
      "prompt": "Genesis",
      "conversation_summary": "Discussed fear of group projects",
      "materialized_fears": {
        "social rejection": "not being included in group chat for project"
      },
      "anxiety_level": 7.5
    },
    {
      "stage": 1,
      "prompt": "G1M01",
      "conversation_summary": "Practiced approaching study partner",
      "materialized_challenges": {
        "starting conversations": "saying hi to lab partner before class"
      },
      "anxiety_level": 7.0
    }
  ]
}
```

## Implementation Steps

1. ✅ Update `models.py` - Add `ConversationBasedProfile` class
2. ✅ Update `AIDummy` - Add profile management methods
3. ✅ Update `conversation_simulator.py` - Add materialization after conversation
4. ✅ Update `assessment_system.py` - Use evolved profile for assessment
5. ✅ Update `prompt_optimizer.py` - Reset profile before each prompt test
6. ✅ Add `personality_materializer.py` - LLM-based materialization service
7. ✅ Update `web_interface.py` - Add evolution timeline visualization
8. ✅ Add storage for evolution history

## Key Benefits

- ✅ **Fair Comparison**: Each prompt tested against same original baseline
- ✅ **Realistic Evolution**: Personality growth happens naturally through conversation
- ✅ **Full Traceability**: Complete evolution history for each dummy
- ✅ **Meaningful Assessment**: Evolved personality reflects conversation impact
- ✅ **Visual Backtracking**: See exactly how personality changed over time

