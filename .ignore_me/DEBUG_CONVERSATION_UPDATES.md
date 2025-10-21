# Debug Conversation Updates for Grounded Assessment

## Summary of Changes

The `debug_conversation.py` script has been updated to work seamlessly with the new **grounded progressive assessment system**. Since it uses the main `ConversationLengthExperimentWithEvolution` class with debug wrappers, all improvements automatically propagate.

## Key Updates to `debug_conversation.py`

### 1. **Updated Debug Wrappers** (Lines 242-254)

#### Added `generate_milestone_assessment()` wrapper:
```python
async def generate_milestone_assessment(self, dummy, previous_assessment, 
                                       conversation, conversation_simulator=None, 
                                       turns_so_far=None):
    """Override to track conversation being assessed."""
    self._current_conversation = conversation
    result = await super().generate_milestone_assessment(
        dummy, previous_assessment, conversation, 
        conversation_simulator, turns_so_far
    )
    self._current_conversation = None
    return result
```

**Purpose:** Tracks which conversation is being assessed so debug output can show proper milestone labels.

#### Updated `generate_post_assessment()` wrapper:
```python
async def generate_post_assessment(self, dummy, pre_assessment, 
                                   conversation=None, conversation_simulator=None,
                                   previous_milestone_assessment=None):  # NEW parameter
    """Override to track conversation being assessed."""
    self._current_conversation = conversation
    result = await super().generate_post_assessment(
        dummy, pre_assessment, conversation, 
        conversation_simulator, previous_milestone_assessment
    )
    self._current_conversation = None
    return result
```

**Purpose:** Accepts new `previous_milestone_assessment` parameter for proper grounding.

### 2. **Enhanced Debug Output** (Lines 261-289)

The debug wrapper automatically detects and labels different assessment types:

```python
# Detects milestone assessments from conversation ID
if "milestone_turn11" in conversation.id:
    step_label = "MILESTONE ASSESSMENT at Turn 11"

# Detects baseline assessments
elif "baseline" in user_prompt:
    step_label = "PRE-ASSESSMENT (Baseline)"

# Detects final post-assessments
elif conversation is full conversation:
    step_label = "POST-ASSESSMENT (Final)"
```

### 3. **Automatic Grounding Visibility**

Debug output now shows grounding messages from the main experiment:
```
   📊 Anchoring to baseline pre-assessment (score: 2.40)
   📊 Anchoring to previous milestone assessment (score: 2.50)
```

These messages come from `conversation_length_experiment_with_evolution.py` and appear automatically in debug runs.

## How to Use

### Basic Debug Run:
```bash
python debug_conversation.py \
  --dummy "Gregory Moore" \
  --experiment continuous_conversation_with_evolution_exp_20251021_211354.json
```

### Custom Milestones:
```bash
python debug_conversation.py \
  --dummy "Sarah Brooks" \
  --max-turns 31 \
  --milestones 11,21,31
```

## What You'll See

### Pre-Assessment:
```
STEP 1: PRE-ASSESSMENT (Baseline)
════════════════════════════════════════
📤 PROMPT TO LLM:
  System: You are administering a social skills self-assessment...
  User: STUDENT PROFILE: Name: Gregory Moore...
  
📥 RESPONSE FROM LLM:
  1. I initiate conversations: Score 4
  2. I maintain eye contact: Score 2
  ...
  
✅ Parsed assessment: 2.40 average
```

### Milestone Assessment (Grounded):
```
STEP 10: MILESTONE ASSESSMENT at Turn 11
════════════════════════════════════════
📊 Anchoring to baseline pre-assessment (score: 2.40)

📤 PROMPT TO LLM:
  System: You are administering...
          CRITICAL: USE PREVIOUS SCORES AS YOUR ANCHOR
  
  User: PREVIOUS ASSESSMENT SCORES (USE AS YOUR ANCHOR):
        Previous average score: 2.40/4.0
        
        PREVIOUS SCORES FOR EACH QUESTION:
        1. I initiate conversations
           Previous score: 4/4  ← ANCHOR POINT
        2. I maintain eye contact
           Previous score: 2/4  ← ANCHOR POINT
        ...
        
        CONVERSATION SO FAR:
        [Memo of turns 1-11]
        
        CRITICAL GROUNDING RULES:
        1. START with previous scores above
        2. ONLY change if skill was discussed
        3. Max change: ±1 point
```

### Second Milestone (Chained Grounding):
```
STEP 15: MILESTONE ASSESSMENT at Turn 21
════════════════════════════════════════
📊 Anchoring to previous milestone assessment (score: 2.50)

📤 PROMPT TO LLM:
  PREVIOUS ASSESSMENT SCORES:
  Previous average score: 2.50/4.0
  
  1. I initiate conversations
     Previous score: 3/4  ← FROM MILESTONE 1
  2. I maintain eye contact
     Previous score: 2/4  ← FROM MILESTONE 1
```

## Verification

The grounding is working if you see:
1. ✅ "Anchoring to..." messages before each assessment
2. ✅ "PREVIOUS ASSESSMENT SCORES" in prompts
3. ✅ "CRITICAL GROUNDING RULES" in prompts
4. ✅ Small incremental changes (±0.5 to ±1.0 typical)
5. ✅ Milestone notes showing "Grounded assessment"

## Files Modified for Grounded Assessment

1. **`prompts/assessment_prompts.yaml`**
   - Added `milestone_assessment_prompt` with grounding rules
   - Updated `post_conversation_assessment_prompt` with grounding

2. **`assessment_system_llm_based.py`**
   - Added `generate_milestone_assessment()` method
   - Updated `generate_post_assessment()` to accept previous milestone
   - Added `_create_milestone_assessment_user_prompt()` method
   - Renamed `_get_baseline_scores_summary()` → `_get_previous_scores_summary()`

3. **`conversation_length_experiment_with_evolution.py`**
   - Updated `_process_single_milestone()` to accept full previous result and pre_assessment
   - Updated `_process_milestones_parallel()` to pass pre_assessment for grounding chain
   - Updated `_simulate_conversation_with_milestones()` to accept and pass pre_assessment
   - Updated post-assessment to anchor to last milestone if available

4. **`debug_conversation.py`**
   - Added `generate_milestone_assessment()` wrapper
   - Updated `generate_post_assessment()` wrapper with new parameter
   - All changes automatic since it uses main experiment class

