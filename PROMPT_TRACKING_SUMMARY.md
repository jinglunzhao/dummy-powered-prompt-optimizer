# Prompt Tracking Summary

## Quick Access

### Run Tracking Tool
```bash
python scripts/track_prompts.py
```

### Latest Analysis (2025-10-18)

**Total Prompts:** 16 across 5 YAML files  
**Used:** 12/16 (75%)  
**Unused:** 4/16 (25%)  
**Hardcoded Issues:** 13 instances found

---

## ✅ Currently Used Prompts (12)

### `assessment_prompts.yaml` (3/3 used)
- ✅ `assessment_system_prompt` → `assessment_system_llm_based.py`
- ✅ `baseline_assessment_prompt` → `assessment_system_llm_based.py`
- ✅ `post_conversation_assessment_prompt` → `assessment_system_llm_based.py`

### `conversation_prompts.yaml` (5/5 used) ⭐ **All Active**
- ✅ `ai_coach_system_addition` → `conversation_simulator.py` **[CRITICAL: Appended to all prompts]**
- ✅ `conversation_end_detection_prompt` → `conversation_simulator.py`
- ✅ `end_detection_system` → `conversation_simulator.py`
- ✅ `student_opening_prompt` → `conversation_simulator.py`
- ✅ `student_response_system` → `conversation_simulator.py`

### `default_prompts.yaml` (1/2 used)
- ✅ `default_peer_mentor_prompt` → `conversation_length_experiment_with_evolution.py`
- ⚠️ `default_system_prompt` → **NOT USED**

### `materializer_prompts.yaml` (1/2 used)
- ✅ `materialization_prompt` → `personality_materializer.py`
- ⚠️ `fallback_summary_prompt` → **NOT USED**

### `optimizer_prompts.yaml` (2/4 used)
- ✅ `crossover_prompt` → `prompt_optimizer.py`
- ✅ `mutation_prompt` → `prompt_optimizer.py`
- ⚠️ `reflection_prompt` → **NOT USED**
- ⚠️ `synthesis_analysis_prompt` → **NOT USED**

---

## ⚠️ Unused Prompts (4)

These prompts exist in YAML but aren't referenced in code:

1. **`default_prompts.yaml:default_system_prompt`**
   - Likely superseded by `default_peer_mentor_prompt`
   - Also hardcoded in `config.py:SYSTEM_PROMPT`
   - **Action:** Remove or document purpose

2. **`materializer_prompts.yaml:fallback_summary_prompt`**
   - Fallback for when materialization fails
   - **Action:** Check if fallback logic is still in code

3. **`optimizer_prompts.yaml:reflection_prompt`**
   - Single conversation analysis
   - **Action:** Check if still needed or integrated elsewhere

4. **`optimizer_prompts.yaml:synthesis_analysis_prompt`**
   - Multi-conversation analysis
   - **Action:** Check if still needed or integrated elsewhere

---

## 🔴 Hardcoded Prompt Issues (13 instances)

### Priority 1: Core Files
- `config.py:24` - Duplicates `default_system_prompt`
- `test_gepa_system.py:169` - Should use YAML
- `conversation_length_experiment_with_evolution.py:44` - Comment/fallback?

### Priority 2: Test Scripts (Can be lower priority)
- `simple_conversation_mock.py:36`
- `scripts/test_role_separation.py:149`
- `scripts/test_assessment_invariance.py:64, 98, 132`
- `scripts/test_gepa_system.py:148`
- `scripts/test_multiturn_assessment.py:60`
- `scripts/test_human_like_assessment.py:60`
- `scripts/test_conversation_memory.py:60`
- `scripts/test_improved_summarization.py:59`

---

## 📋 Action Items

### Immediate
- [ ] Investigate unused prompts (reflection_prompt, synthesis_analysis_prompt)
- [ ] Fix `Config.SYSTEM_PROMPT` duplication in `config.py`
- [ ] Update `test_gepa_system.py` to use YAML

### Medium Priority  
- [ ] Migrate test script hardcoded prompts to YAML
- [ ] Document why `fallback_summary_prompt` exists if not used
- [ ] Remove `default_system_prompt` if truly unused

### Documentation
- [ ] Keep this file updated when adding/removing prompts
- [ ] Run `scripts/track_prompts.py` before major changes

---

## 📚 Related Documentation

- **Comprehensive Guide:** [PROMPT_REFERENCE_GUIDE.md](PROMPT_REFERENCE_GUIDE.md)
- **Architecture:** [.cursor/rules/project-overview.mdc](.cursor/rules/project-overview.mdc)
- **Tracking Tool:** `scripts/track_prompts.py`

---

**Last Updated:** 2025-10-18  
**Next Review:** Before next major release

