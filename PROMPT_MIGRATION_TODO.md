# Prompt Migration TODO

## ✅ Completed

1. **conversation_simulator.py** - All prompts migrated to `prompts/conversation_prompts.yaml`
   - Student opening prompt
   - AI coach system addition
   - Student response system
   - End detection prompts

2. **prompt_optimizer.py** - All prompts migrated to `prompts/optimizer_prompts.yaml`
   - Mutation prompt
   - Crossover prompt
   - Synthesis analysis prompt
   - Reflection prompt

3. **personality_materializer.py** - All prompts migrated to `prompts/materializer_prompts.yaml`
   - Materialization prompt
   - Fallback summary prompt

4. **Created prompt infrastructure**:
   - `prompts/prompt_loader.py` - Centralized loading utility
   - `prompts/assessment_prompts.yaml` - Assessment prompts (prepared but not integrated yet)

## 🔄 Remaining Work

### High Priority

1. **assessment_system_llm_based.py** - Prompts ready but not integrated
   - File: `prompts/assessment_prompts.yaml` (already created)
   - Methods to update:
     - `_create_assessment_system_prompt()` (lines 100-131)
     - `_create_baseline_user_prompt()` (lines 133-164)
     - `_create_post_conversation_user_prompt()` (lines 166-218)
   
   **Action needed**: Replace the multi-line string returns with prompt_loader calls
   
   **Example**:
   ```python
   def _create_assessment_system_prompt(self) -> str:
       return prompt_loader.get_prompt(
           'assessment_prompts.yaml',
           'assessment_system_prompt'
       )
   ```

### Medium Priority

2. **conversation_length_experiment_with_evolution.py** - Contains base prompt
   - Line ~43: `base_prompt` parameter default value
   - Consider creating `experiment_prompts.yaml` for experiment configurations

3. **config.py** - Contains default system prompt
   - `SYSTEM_PROMPT` constant
   - Could move to `prompts/default_prompts.yaml`

### Low Priority (Test Files - Can Keep As-Is)

4. **test_gepa_system.py** - Test-specific prompts
   - Can remain in code since they're for testing only

5. **test_conversation_quality.py** - Test prompt
   - Can remain in code

6. **simple_conversation_mock.py** - Mock/demo file
   - Can remain in code

## 📋 Migration Process

For each remaining file:

1. Add `from prompts.prompt_loader import prompt_loader` to imports
2. Create YAML entry in appropriate prompts file (or create new file)
3. Replace multi-line string with `prompt_loader.get_prompt()` call
4. Test to ensure functionality unchanged
5. Commit changes

## 🎯 Benefits After Full Migration

- **30-40% code size reduction** in files with prompts
- **Easy prompt iteration** - edit YAML without touching code
- **Version control friendly** - diffs show actual prompt changes
- **Centralized prompt management** - all prompts in one place
- **A/B testing ready** - swap prompt files easily

## 📝 Notes

- The prompt infrastructure is solid and working
- `assessment_prompts.yaml` is already created and ready to use
- Just need to update the Python files to use it
- This is non-urgent since embedded prompts still work fine
- Can be done incrementally as files are modified for other reasons

---

*Last updated: 2025-10-18*

