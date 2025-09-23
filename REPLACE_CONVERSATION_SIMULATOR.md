# Replace Conversation Simulator Plan

## Current Status
- ✅ Clean conversation simulator created and tested
- ✅ Removes all hardcoded scenarios and fallback templates
- ✅ Uses rich character data for authentic conversations
- ✅ API-first design with no fallback complexity

## Implementation Steps

### 1. **Backup Current Simulator**
```bash
mv conversation_simulator.py conversation_simulator_old.py
```

### 2. **Replace with Clean Version**
```bash
mv conversation_simulator_clean.py conversation_simulator.py
```

### 3. **Update Imports**
Update any files that import from `conversation_simulator`:
- `prompt_optimizer.py` - Update import if needed
- `test_gepa_system.py` - Should work with same interface

### 4. **Remove Unused Configuration**
Remove from `config.py`:
```python
# REMOVE these hardcoded scenarios
CONVERSATION_SCENARIOS = [
    "Meeting someone new at a party",
    "Asking for directions from a stranger",
    # ... etc
]
```

### 5. **Update Method Calls**
The clean simulator has the same interface:
```python
# Same method signature
conversation = await simulator.simulate_conversation_async(
    dummy=dummy,
    scenario="Social skills coaching session",  # Now generic
    num_rounds=num_rounds,
    custom_system_prompt=prompt.prompt_text
)
```

## Benefits After Replacement

### 1. **Reduced Codebase**
- **Before**: 769 lines with complex scenario handling
- **After**: ~200 lines focused on AI generation
- **Removed**: ~500 lines of hardcoded templates

### 2. **More Authentic Conversations**
- Conversations emerge from character's real concerns
- No artificial scenario constraints
- Natural dialogue flow

### 3. **Better Character Fidelity**
- Responses match individual personality traits
- Anxiety levels expressed authentically
- Real fears, goals, and challenges drive conversation

### 4. **Simplified Maintenance**
- Single code path for conversation generation
- No complex scenario matching logic
- Pure AI generation approach

## Testing Plan

### 1. **Unit Test**
```bash
python conversation_simulator_clean.py
```

### 2. **Integration Test**
```bash
python test_gepa_system.py --dummies 1 --rounds 1 --generations 1
```

### 3. **Verify Conversation Quality**
- Check that conversations are more natural
- Verify character authenticity
- Ensure no hardcoded responses

## Rollback Plan
If issues arise:
```bash
mv conversation_simulator.py conversation_simulator_clean.py
mv conversation_simulator_old.py conversation_simulator.py
```

## Files to Update
1. `conversation_simulator.py` - Replace with clean version
2. `config.py` - Remove CONVERSATION_SCENARIOS
3. Any test files - Update if needed

The replacement maintains the same external interface while dramatically simplifying the internal implementation and improving conversation quality.
