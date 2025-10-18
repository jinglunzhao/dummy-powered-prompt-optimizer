# Prompts Directory

This directory contains all static prompt templates used across the system.

## 📁 Files

### `default_prompts.yaml` (2 prompts)
**Starting point prompts for experiments**

- `default_system_prompt` - Simple fallback (not actively used)
- `default_peer_mentor_prompt` - Main baseline for conversation length experiments

**Usage:** Starting point for GEPA evolution and manual experiments

---

### `conversation_prompts.yaml` (5 prompts) ⭐
**Technical conversation mechanics - ALWAYS APPENDED**

- `student_opening_prompt` - How students start conversations
- `ai_coach_system_addition` - **CRITICAL: Appended to ALL system prompts**
- `student_response_system` - How students respond during conversations
- `conversation_end_detection_prompt` - Detect when to end conversations
- `end_detection_system` - System prompt for end detection

**Usage:** Every conversation run appends these mechanics for quality control

---

### `assessment_prompts.yaml` (3 prompts)
**LLM-based self-assessment simulation**

- `assessment_system_prompt` - Assessment methodology (1-4 scale)
- `baseline_assessment_prompt` - Pre-conversation assessment
- `post_conversation_assessment_prompt` - Post-conversation assessment

**Usage:** Pre/post assessments to measure coaching effectiveness

---

### `optimizer_prompts.yaml` (4 prompts)
**GEPA prompt evolution system**

- `mutation_prompt` - Evolve single prompt using feedback
- `crossover_prompt` - Combine two prompts into one
- `synthesis_analysis_prompt` - Analyze multi-conversation performance
- `reflection_prompt` - Analyze single conversation

**Usage:** GEPA system uses these to evolve prompts over generations

---

### `materializer_prompts.yaml` (2 prompts)
**Personality trait evolution tracking**

- `materialization_prompt` - Convert abstract traits to concrete behaviors
- `fallback_summary_prompt` - Fallback conversation summary

**Usage:** Track how dummy personalities evolve during conversations

---

## 🔧 How to Use

### Load a Prompt
```python
from prompts.prompt_loader import prompt_loader

prompt = prompt_loader.get_prompt(
    'default_prompts.yaml',
    'default_peer_mentor_prompt'
)
```

### With Variables
```python
prompt = prompt_loader.get_prompt(
    'conversation_prompts.yaml',
    'student_opening_prompt',
    student_name="Alex",
    age=20,
    student_type="Undergraduate",
    university="Example University"
)
```

---

## ⚙️ How Prompts Work Together

### In a Conversation:
```python
# Final prompt = base coaching style + technical mechanics
final_prompt = system_prompt + ai_coach_system_addition
#              ↑                ↑
#              Variable         Constant (always appended)
#              (from default)   (from conversation_prompts)
```

**Why?**
- `system_prompt`: Define different coaching approaches (what we test)
- `ai_coach_system_addition`: Ensure quality/prevent issues (technical controls)

---

## 📊 Tracking

### Check Prompt Usage
```bash
# Run tracking tool to see where each prompt is used
python scripts/track_prompts.py
```

### Find Duplicates
The tracking tool will identify:
- Unused prompts in YAML files
- Hardcoded prompts that should be in YAML
- Duplicate prompt definitions

---

## 🎯 Best Practices

### DO ✅
- Use `prompt_loader.get_prompt()` to load prompts
- Keep prompts in YAML files (single source of truth)
- Use descriptive prompt keys
- Document new prompts in [PROMPT_REFERENCE_GUIDE.md](../PROMPT_REFERENCE_GUIDE.md)

### DON'T ❌
- Hardcode prompts in Python files
- Duplicate prompt text across files
- Skip `ai_coach_system_addition` (breaks conversations)
- Modify `conversation_prompts.yaml` without testing ALL experiments

---

## 📚 Related Documentation

- **Comprehensive Reference:** [../PROMPT_REFERENCE_GUIDE.md](../PROMPT_REFERENCE_GUIDE.md)
- **Quick Summary:** [../PROMPT_TRACKING_SUMMARY.md](../PROMPT_TRACKING_SUMMARY.md)
- **Architecture:** [../.cursor/rules/project-overview.mdc](../.cursor/rules/project-overview.mdc)

---

**Questions?** See the comprehensive guide or run the tracking tool.

