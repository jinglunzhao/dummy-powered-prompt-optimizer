# Prompt Reference Guide
**AI Dummy Social Skills Testing System**

This document tracks all prompts in the system, where they're used, and how to manage them.

---

## 📋 Table of Contents
1. [Prompt Inventory](#prompt-inventory)
2. [Usage Map](#usage-map)
3. [Hardcoded Prompts & Duplication Issues](#hardcoded-prompts--duplication-issues)
4. [Best Practices](#best-practices)
5. [Quick Reference](#quick-reference)

---

## 📦 Prompt Inventory

### 1. `prompts/default_prompts.yaml` (2 prompts)
**Purpose:** Baseline starting prompts for experiments

| Prompt Key | Purpose | Lines |
|------------|---------|-------|
| `default_system_prompt` | Simple fallback for backwards compatibility | 4-5 |
| `default_peer_mentor_prompt` | Main baseline prompt for experiments (detailed) | 7-27 |

**Key Features:**
- ✅ Contains role instructions
- ✅ Conversation continuity guidelines
- ✅ Quality standards

---

### 2. `prompts/conversation_prompts.yaml` (5 prompts)
**Purpose:** Technical conversation mechanics (appended to all system prompts)

| Prompt Key | Purpose | Used In | Lines |
|------------|---------|---------|-------|
| `student_opening_prompt` | Generate student's first message | `conversation_simulator.py:96` | 4-9 |
| `ai_coach_system_addition` | **CRITICAL: Appended to ALL system prompts** | `conversation_simulator.py:137` | 11-35 |
| `student_response_system` | Generate student's responses | `conversation_simulator.py:181` | 37-62 |
| `conversation_end_detection_prompt` | Detect natural conversation endings | `conversation_simulator.py:312` | 64-79 |
| `end_detection_system` | System prompt for end detection | `conversation_simulator.py:318` | 81-82 |

**Critical Note:** `ai_coach_system_addition` is **ALWAYS appended** to system prompts:
```python
{"role": "system", "content": system_prompt + system_addition}
```

---

### 3. `prompts/assessment_prompts.yaml` (3 prompts)
**Purpose:** LLM-based self-assessment simulation

| Prompt Key | Purpose | Used In | Lines |
|------------|---------|---------|-------|
| `assessment_system_prompt` | System prompt for assessment methodology | `assessment_system_llm_based.py:102` | 4-34 |
| `baseline_assessment_prompt` | Pre-conversation assessment | `assessment_system_llm_based.py:117` | 36-58 |
| `post_conversation_assessment_prompt` | Post-conversation assessment | `assessment_system_llm_based.py:148` | 60-92 |

**Scoring Scale:** 1-4 (NOT 1-10 like anxiety levels)

---

### 4. `prompts/optimizer_prompts.yaml` (4 prompts)
**Purpose:** GEPA prompt evolution system

| Prompt Key | Purpose | Used In | Lines |
|------------|---------|---------|-------|
| `mutation_prompt` | Evolve a single prompt using synthesis | `prompt_optimizer.py:1400` | 4-26 |
| `crossover_prompt` | Combine two prompts into one | `prompt_optimizer.py:1260` | 28-42 |
| `synthesis_analysis_prompt` | Analyze conversation performance | `prompt_optimizer.py` (inline) | 44-61 |
| `reflection_prompt` | Analyze single conversation | `prompt_optimizer.py` (inline) | 63-81 |

**Output Format:** Must start with "You are..." (validated in code)

---

### 5. `prompts/materializer_prompts.yaml` (2 prompts)
**Purpose:** Convert abstract traits to concrete behaviors

| Prompt Key | Purpose | Used In | Lines |
|------------|---------|---------|-------|
| `materialization_prompt` | Main trait materialization | `personality_materializer.py:143` | 4-31 |
| `fallback_summary_prompt` | Fallback conversation summary | `personality_materializer.py` (fallback) | 33-47 |

**Output Format:** JSON only (strictly validated)

---

## 🗺️ Usage Map

### System Prompt Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    EXPERIMENT STARTS                         │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ├─ GEPA Optimization
                 │  └─> Starts with: default_peer_mentor_prompt
                 │      └─> Evolves to: hundreds of prompts
                 │          └─> Stored in: gepa_optimization_exp_*.json
                 │
                 ├─ Conversation Length Experiment  
                 │  └─> Uses: default_peer_mentor_prompt OR --prompt arg
                 │      └─> Tests at different lengths
                 │          └─> Stored in: continuous_conversation_*.json
                 │
                 └─ All Conversations
                    └─> system_prompt = base_prompt + ai_coach_system_addition
                        └─> base_prompt: from YAML or GEPA-generated
                        └─> ai_coach_system_addition: ALWAYS from conversation_prompts.yaml
```

### Key Files Using Prompts

| File | Prompts Used | Purpose |
|------|--------------|---------|
| **conversation_simulator.py** | • `ai_coach_system_addition` (appended to all)<br>• `student_opening_prompt`<br>• `student_response_system`<br>• `conversation_end_detection_prompt`<br>• `end_detection_system` | Runs all conversations |
| **assessment_system_llm_based.py** | • `assessment_system_prompt`<br>• `baseline_assessment_prompt`<br>• `post_conversation_assessment_prompt` | Pre/post assessments |
| **prompt_optimizer.py** | • `mutation_prompt`<br>• `crossover_prompt`<br>• Uses synthesis/reflection inline | GEPA evolution |
| **personality_materializer.py** | • `materialization_prompt`<br>• `fallback_summary_prompt` | Trait evolution |
| **conversation_length_experiment_with_evolution.py** | • `default_peer_mentor_prompt` (as starting point) | Conversation length tests |

---

## ⚠️ Hardcoded Prompts & Duplication Issues

### 🔴 Critical Duplication Found

**Issue #1: `Config.SYSTEM_PROMPT` vs `default_system_prompt`**

Location: `config.py:24`
```python
SYSTEM_PROMPT = "You are a supportive AI assistant helping students improve their social skills. Be encouraging, provide practical advice, and help them build confidence gradually."
```

- **Duplicate of:** `default_system_prompt` in `default_prompts.yaml`
- **Used in:** `conversation_simulator.py:33` as fallback
- **Risk:** Two sources of truth, potential inconsistency
- **Recommendation:** 
  ```python
  # In config.py, load from YAML instead:
  SYSTEM_PROMPT = prompt_loader.get_prompt('default_prompts.yaml', 'default_system_prompt')
  ```

---

**Issue #2: Test File Hardcoded Prompts**

Locations with hardcoded "You are a helpful peer mentor..." or similar:
- `test_gepa_system.py:169` - Creates initial prompt inline
- `simple_conversation_mock.py` - May have hardcoded prompts
- Multiple experiment JSON files store prompts (expected behavior)

**Recommendation:**
- Replace hardcoded prompts with `prompt_loader.get_prompt()` calls
- Only exception: GEPA-generated prompts stored in experiment results

---

**Issue #3: Prompt Validation in Multiple Places**

Prompt format validation ("must start with 'You are...'") appears in:
- `prompt_optimizer.py:1305` - Crossover validation
- `prompt_optimizer.py:1448` - Mutation validation

**Recommendation:** Create a shared validation function:
```python
def validate_system_prompt(prompt: str) -> bool:
    """Validate system prompt format"""
    return prompt.strip().startswith("You are")
```

---

## ✅ Best Practices

### 1. **Always Use `prompt_loader`**
```python
# ✅ CORRECT
prompt = prompt_loader.get_prompt('default_prompts.yaml', 'default_peer_mentor_prompt')

# ❌ WRONG
prompt = "You are a helpful peer mentor..."  # Hardcoded!
```

### 2. **Understand Prompt Composition**
```python
# Final prompt = base + mechanics
final_prompt = system_prompt + ai_coach_system_addition
#              ↑                ↑
#              Variable         Constant (always appended)
#              (from YAML/GEPA) (from conversation_prompts.yaml)
```

### 3. **Know Your Prompt Types**

| Type | Storage | Mutable | Purpose |
|------|---------|---------|---------|
| **Baseline** | YAML files | No | Starting points |
| **GEPA-Generated** | Experiment JSON | Yes (evolves) | Optimized prompts |
| **Mechanics** | `conversation_prompts.yaml` | No | Technical controls |

### 4. **Experiment Result Prompts**

Generated prompts are stored in experiment JSON files:
```json
{
  "optimization": {
    "all_prompts": [/* every generated prompt */],
    "pareto_frontier": [/* best performing prompts */]
  }
}
```

**To reuse a GEPA-generated prompt:**
1. Find it in `data/experiments/gepa_optimization_exp_*.json`
2. Copy the `prompt_text` from `all_prompts[]` array
3. Pass to experiment via `--prompt` argument or use directly

---

## 🔍 Quick Reference

### Find Where a Prompt is Used
```bash
# Search for prompt key usage
grep -r "prompt_key_name" --include="*.py"

# Find get_prompt calls
grep -r "get_prompt" --include="*.py"

# Find hardcoded system prompts
grep -r "You are a" --include="*.py" --include="*.yaml"
```

### Add a New Prompt
1. Add to appropriate YAML file in `prompts/`
2. Use descriptive key name (e.g., `new_feature_system_prompt`)
3. Load with: `prompt_loader.get_prompt('file.yaml', 'key_name')`
4. Document here in this guide

### Modify Existing Prompt
1. **Baseline prompts:** Edit YAML file directly
2. **GEPA prompts:** They auto-evolve; edit YAML starting point to influence evolution
3. **Mechanics prompts:** Edit carefully - affects ALL conversations

---

## 📊 Summary Statistics

| Category | Count | Location |
|----------|-------|----------|
| **YAML Files** | 5 | `prompts/*.yaml` |
| **Total YAML Prompts** | 16 | Across all files |
| **Active Python Files Using Prompts** | 5 | Main codebase |
| **GEPA-Generated Prompts** | 100s | `data/experiments/gepa_*.json` |
| **Hardcoded Duplications Found** | 2 | See issues above |

---

## 🎯 Recommendations

### Priority 1: Remove Hardcoded Duplicates
- [ ] Replace `Config.SYSTEM_PROMPT` with YAML loader
- [ ] Update `test_gepa_system.py:169` to use YAML

### Priority 2: Centralize Validation
- [ ] Create `prompts/prompt_validator.py`
- [ ] Add shared validation functions
- [ ] Use across all prompt-generating code

### Priority 3: Documentation
- [ ] Keep this guide updated when adding prompts
- [ ] Add docstrings to `prompt_loader.py` methods
- [ ] Document prompt format requirements in YAML files

---

**Last Updated:** 2025-10-18  
**Maintainer:** System Documentation  
**Related:** See `.cursor/rules/project-overview.mdc` for architecture

