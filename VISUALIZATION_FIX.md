# Flat Line Visualization Fix

## Problem: All Lines Appear Flat

The conversation journey visualizer was showing flat lines for all dummies instead of showing progression.

## Root Cause: Incremental vs Cumulative Improvement

### What Was Being Stored (BEFORE):
```python
# Milestone 1
improvement = milestone1_score - pre_score  # -0.10 (cumulative)

# Milestone 2 (WRONG!)
improvement = milestone2_score - milestone1_score  # +0.10 (incremental from M1)

# Milestone 3 (WRONG!)
improvement = milestone3_score - milestone2_score  # +0.05 (incremental from M2)
```

**Chart received:**
```
Turn 0:  improvement = 0.00
Turn 11: improvement = -0.10
Turn 21: improvement = +0.10  ← This looks like it went UP to +0.10!
Turn 31: improvement = +0.05  ← Then DOWN to +0.05?
```

**Visualization interpretation:**
The chart tries to plot these values and gets confused because:
- Y-axis shows "Improvement (points)"
- Data points: 0.00, -0.10, +0.10, +0.05
- These don't represent cumulative progression!

### What Should Be Stored (AFTER):
```python
# ALL milestones calculate from BASELINE
# Milestone 1
cumulative_improvement = milestone1_score - pre_score  # -0.10

# Milestone 2
cumulative_improvement = milestone2_score - pre_score  # 0.00

# Milestone 3
cumulative_improvement = milestone3_score - pre_score  # +0.05
```

**Chart receives:**
```
Turn 0:  improvement = 0.00  (baseline)
Turn 11: improvement = -0.10 (total change from baseline)
Turn 21: improvement = 0.00  (total change from baseline)
Turn 31: improvement = +0.05 (total change from baseline)
```

**Visualization shows:**
A proper progression line: starts at 0, dips to -0.10, recovers to 0.00, improves to +0.05 ✅

## The Fix

**File:** `conversation_length_experiment_with_evolution.py` lines 555-566

```python
# Calculate BOTH for different purposes:
incremental_improvement = milestone_score - previous_score  # For grounded comparison
cumulative_improvement = milestone_score - pre_score      # For visualization

milestone_result = {
    "improvement": cumulative_improvement,        # Primary field (visualization)
    "incremental_improvement": incremental_improvement,  # Secondary field (analysis)
    ...
}
```

### Benefits:
1. **Visualization works:** Shows actual progression over time
2. **Analysis works:** Can still see step-by-step changes
3. **Grounding works:** Still compares to previous assessment during generation
4. **Best of both worlds:** Store both values for different use cases

## Example Output

### Before (Flat Lines):
```
Milestone results stored:
  Turn 11: improvement=-0.10 (from baseline)
  Turn 21: improvement=+0.05 (from turn 11) ← Looks like big jump!
  Turn 31: improvement=+0.10 (from turn 21)

Chart: Confusing zigzag or flat line
```

### After (Proper Progression):
```
Milestone results stored:
  Turn 11: improvement=-0.10 (total from baseline), incremental=-0.10
  Turn 21: improvement=-0.05 (total from baseline), incremental=+0.05
  Turn 31: improvement=+0.05 (total from baseline), incremental=+0.10

Chart: Smooth progression line showing recovery
Terminal output: "Δ+0.05 from previous, -0.05 total"
```

## Testing

Run experiment and check visualization:
```bash
python conversation_length_experiment_with_evolution.py \
  --dummies 5 \
  --max-turns 51 \
  --milestones 11,21,31,41,51 \
  --save-details

# Then view in browser:
# Open templates/conversation_journey_visualizer.html
```

**Expected:**
- ✅ Lines show actual progression (not flat)
- ✅ Y-axis values represent total improvement from baseline
- ✅ Terminal shows both incremental and cumulative for clarity

