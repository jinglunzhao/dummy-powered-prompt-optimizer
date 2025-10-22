# File Reference Guide - After Reorganization

## 📁 Main Experiment Scripts

| New Name | Old Name | Purpose |
|----------|----------|---------|
| `conversation_experiment_with_visualization.py` | `conversation_length_experiment_with_evolution.py` | Test ONE prompt at different conversation lengths with milestone assessments |
| `prompt_optimizer_experiment.py` | `test_gepa_system.py` | GEPA optimization - evolve prompts across generations |
| `single_conversation_experiment.py` | `debug_conversation.py` | Debug single conversation with full LLM prompt/response visibility |
| `conversation_visualizer.py` | `start_visualizer.py` | Launch web visualization dashboard |

## 🧠 Core System Components

| New Name | Old Name | Purpose |
|----------|----------|---------|
| `assessment_system.py` | `assessment_system_llm_based.py` | LLM-based social skills assessment with grounded progressive scoring |
| `conversation_simulator.py` | (unchanged) | Simulates conversations between AI coach and student dummy |
| `prompt_optimizer.py` | (unchanged) | GEPA-based prompt evolution and optimization engine |
| `personality_materializer.py` | (unchanged) | Converts abstract traits into concrete examples |

## 📊 Data Models & Config

| File | Purpose |
|------|---------|
| `models.py` | All Pydantic data models (AIDummy, Conversation, Assessment, etc.) |
| `config.py` | Centralized configuration (API keys, feature flags, parameters) |

## 🎨 Prompts (YAML Templates)

| File | Purpose |
|------|---------|
| `prompts/default_prompts.yaml` | Baseline AI coach prompts (starting points) |
| `prompts/conversation_prompts.yaml` | Conversation mechanics (opening, responses, memos, end detection) |
| `prompts/assessment_prompts.yaml` | Assessment prompts with grounding rules |
| `prompts/materializer_prompts.yaml` | Personality materialization prompts |
| `prompts/optimizer_prompts.yaml` | GEPA optimizer prompts (reflection, mutation) |

## 🌐 Web Interface

| File | Purpose |
|------|---------|
| `web_interface.py` | Flask web dashboard (main interface) |
| `experiment_api_server.py` | API server for experiment data |
| `templates/conversation_journey_visualizer.html` | Interactive D3.js visualization |

## 📈 Analysis Tools

| File | Purpose |
|------|---------|
| `examine_conversation_quality.py` | Deep dive into conversation content and assessment details |

## 🗂️ Data Directories

| Directory | Purpose | Tracked in Git? |
|-----------|---------|----------------|
| `data/experiments/` | Experiment results JSON files | ❌ No (regenerated) |
| `data/conversations/` | Individual conversation logs | ❌ No (regenerated) |
| `data/synthesis_analysis/` | GEPA synthesis results | ❌ No (regenerated) |
| `data/personality_evolution/` | Evolution tracking data | ❌ No (regenerated) |
| `data/ai_dummies.json` | 100 AI dummy personalities | ✅ Yes (source data) |

## 🚀 Quick Start Commands

### Run Conversation Experiment:
```bash
python conversation_experiment_with_visualization.py \
  --dummies 5 \
  --max-turns 31 \
  --milestones 11,21,31 \
  --save-details
```

### Run GEPA Optimization:
```bash
python prompt_optimizer_experiment.py \
  --dummies 10 \
  --turns 31 \
  --generations 6
```

### Debug Single Conversation:
```bash
python single_conversation_experiment.py \
  --dummy "Gregory Moore" \
  --max-turns 31 \
  --milestones 11,21,31
```

### View Results:
```bash
python conversation_visualizer.py
# Then open: http://localhost:5000/
```

## 📝 Documentation

| File | Purpose |
|------|---------|
| `README.md` | Project overview (if exists) |
| `PUSH_TO_GITHUB.md` | GitHub push instructions |
| `examine_conversation_quality.py` | Script for analyzing conversations |

## 🔄 Import Changes Summary

All imports have been updated:
```python
# OLD
from assessment_system_llm_based import AssessmentSystemLLMBased
from conversation_length_experiment_with_evolution import ConversationLengthExperimentWithEvolution

# NEW
from assessment_system import AssessmentSystemLLMBased
from conversation_experiment_with_visualization import ConversationLengthExperimentWithEvolution
```

## 🎯 File Organization Benefits

**Before:**
- Inconsistent naming (debug_, test_, start_, _llm_based)
- Unclear purpose from names
- Hard to find the right script

**After:**
- Consistent naming (experiment.py, visualizer.py)
- Clear purpose from names
- Easy to navigate

All renames preserve full git history! 📚

