# Grounded Assessment System - Implementation Summary

## Problem Identified

### Assessment Inconsistency Issue
The LLM-based assessment system was showing **severe scoring drift** between assessments:

**Example (Gregory Moore):**
- **Pre-assessment** (based on profile only): Q1 = 4/4, Q2 = 3/4, Q4 = 4/4
- **Post-assessment** (after good coaching): Q1 = 2/4 ❌, Q2 = 2/4 ❌, Q4 = 2/4 ❌
- **Result:** -0.550 improvement despite helpful conversation!

### Root Cause
1. **Pre-assessment** doesn't see actual student struggles, scores optimistically based on personality description
2. **Post-assessment** sees student admitting vulnerabilities ("I'm terrified", "I freeze up")
3. **LLM penalizes honesty** - interprets vulnerability as weakness rather than growth

## Solution: Grounded Progressive Assessment

### Core Principle
**Each assessment anchors to the previous assessment** - preventing drift and maintaining consistency.

### Assessment Flow
```
Pre-Assessment (baseline)
    ↓ (anchor)
Milestone 1 (Turn 11) - anchored to pre-assessment
    ↓ (anchor)
Milestone 2 (Turn 21) - anchored to milestone 1
    ↓ (anchor)
Milestone 3 (Turn 31) - anchored to milestone 2
    ↓ (anchor)
Post-Assessment - anchored to last milestone
```

## Implementation Changes

### 1. New YAML Prompts (`prompts/assessment_prompts.yaml`)

#### Added `milestone_assessment_prompt`:
```yaml
PREVIOUS ASSESSMENT SCORES (USE AS YOUR ANCHOR):
{previous_scores}

CRITICAL GROUNDING RULES:
1. START with the previous assessment scores shown above
2. ONLY adjust scores for skills SPECIFICALLY discussed in conversation
3. If a skill wasn't mentioned, KEEP the previous score unchanged
4. Maximum change per assessment: ±1 point
5. Do NOT penalize honesty or vulnerability
6. Showing vulnerability demonstrates growth
```

#### Updated `post_conversation_assessment_prompt`:
- Changed "BASELINE SCORES" to "PREVIOUS ASSESSMENT SCORES"
- Added same grounding rules
- Anchors to last milestone instead of original baseline

### 2. New Methods in `assessment_system_llm_based.py`

#### `generate_milestone_assessment()` (NEW):
```python
async def generate_milestone_assessment(
    dummy: AIDummy,
    previous_assessment: Assessment,  # Anchor point
    conversation: Conversation,
    conversation_simulator = None,
    turns_so_far: int = None
) -> Assessment:
```
- Uses `milestone_assessment_prompt` from YAML
- Passes previous assessment scores for grounding
- Designed for progressive assessment at milestones

#### `generate_post_assessment()` (UPDATED):
```python
async def generate_post_assessment(
    dummy: AIDummy,
    pre_assessment: Assessment,
    conversation: Conversation = None,
    conversation_simulator = None,
    previous_milestone_assessment: Assessment = None  # NEW parameter
) -> Assessment:
```
- Now accepts `previous_milestone_assessment`
- Anchors to last milestone if available, otherwise uses baseline
- Uses updated prompt with grounding rules

#### `_get_previous_scores_summary()` (RENAMED):
```python
def _get_previous_scores_summary(previous_assessment: Assessment) -> str:
    """Format: '1. Question text\n   Previous score: 3/4'"""
```
- Renamed from `_get_baseline_scores_summary()`
- Clearer formatting showing previous scores as anchors

### 3. Updated Experiment Flow (`conversation_length_experiment_with_evolution.py`)

#### `_process_single_milestone()` (UPDATED):
```python
async def _process_single_milestone(
    dummy: AIDummy,
    conversation: Conversation,
    milestone_turn: int,
    previous_milestone_result: Dict[str, Any] = None,  # Full result, not just score
    pre_assessment: Assessment = None  # Baseline for first milestone
) -> Optional[Dict[str, Any]]:
```

**Key changes:**
1. Accepts full `previous_milestone_result` (contains detailed_assessment)
2. Reconstructs previous Assessment object from result
3. Calls new `generate_milestone_assessment()` with proper anchoring
4. Calculates improvement relative to previous assessment (not baseline)

#### `_process_milestones_parallel()` (UPDATED):
```python
async def _process_milestones_parallel(
    dummy: AIDummy,
    conversation: Conversation,
    milestone_turns: List[int],
    pre_assessment: Assessment  # NEW parameter
) -> List[Dict[str, Any]]:
```

**Key changes:**
1. Accepts `pre_assessment` to use as anchor for first milestone
2. Passes full `previous_result` (not just score) to each milestone
3. Progressive chaining: M1 → M2 → M3 → Post

### 4. Debug Support (`debug_conversation.py`)

Added wrappers for new methods:
- `generate_milestone_assessment()` - tracks conversation for debug output
- Updated `generate_post_assessment()` - accepts new parameter

## Expected Behavior

### Before (Drift):
```
Pre:  Q1=4/4, Q2=3/4, Q4=4/4 (avg 2.75)
      ↓ (Student shares struggles in conversation)
Turn11: Q1=2/4, Q2=2/4, Q4=2/4 (avg 2.00) ❌ -0.75 points!
```

### After (Grounded):
```
Pre:  Q1=4/4, Q2=3/4, Q4=4/4 (avg 2.75)
      ↓ (Anchored grounding)
Turn11: Q1=4/4, Q2=3/4, Q4=3/4 (avg 2.70) ✅ Small targeted improvement
      ↓ (Anchored grounding)
Turn21: Q1=4/4, Q2=3/4, Q4=3/4 (avg 2.75) ✅ Continued progress
```

## Benefits

1. **Consistency** - Assessments build on each other, no random drift
2. **Fairness** - Students aren't penalized for being vulnerable
3. **Targeted Change** - Only skills discussed in conversation change
4. **Realistic Progress** - Small incremental improvements (±1 point max)
5. **True Measurement** - Measures actual coaching impact, not LLM mood swings

## Testing

Run a test to verify:
```bash
python conversation_length_experiment_with_evolution.py \
  --dummies 5 \
  --max-turns 31 \
  --milestones 11,21,31 \
  --save-details

# Then analyze:
python analyze_performance_decay.py
python examine_conversation_quality.py
```

Look for:
- ✅ Milestone notes showing "Grounded assessment: X (anchored to previous Y)"
- ✅ Small incremental changes (±0.5 to ±1.0 typical)
- ✅ Mostly positive or neutral improvements
- ✅ Scores that make sense given conversation content

