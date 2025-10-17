# Codebase Architecture Analysis
*Generated: October 14, 2025*

## 📊 Overview
This is an AI-powered educational chatbot system using **GEPA (Genetic Evolution of Prompts for AI)** to optimize social skills coaching conversations through evolutionary algorithms.

---

## 🏗️ Core Architecture

### **1. CORE MODULES** (Essential - Keep)

#### **A. Data Models & Configuration**
- `models.py` (19K) - **CORE** - Pydantic data models for dummies, conversations, assessments
- `config.py` (3.9K) - **CORE** - API keys, model configurations, system settings

#### **B. Conversation System**
- `conversation_simulator.py` (14K) - **CORE** - Main conversation engine with end detection
- `conversation_storage.py` (9.4K) - **CORE** - Persistent storage for conversation data
- `personality_materializer.py` (22K) - **CORE** - Converts traits to concrete behaviors
- `personality_evolution_storage.py` (12K) - **CORE** - Tracks personality changes over time

#### **C. Assessment System**
- `assessment_system_v3_quantitative.py` (28K) - **CORE** - Current assessment system
- `assessment_system_llm_based.py` (19K) - **LEGACY** - Old LLM-based assessment (replaced)

#### **D. GEPA Optimization Engine**
- `prompt_optimizer.py` (85K) - **CORE** - Evolutionary prompt optimization
  - Mutation, crossover, selection
  - Pareto frontier analysis
  - Multi-objective optimization
- `prompt_naming.py` (8.2K) - **CORE** - Genealogy tracking for prompts

#### **E. Web Interface**
- `web_interface.py` (100K) - **CORE** - Flask server, API endpoints, template rendering
- `templates/` (7 files) - **CORE** - HTML templates for visualization
  - `optimization.html` - GEPA results overview
  - `generation_detail.html` - Per-generation prompt analysis
  - `prompt_detail.html` - Individual prompt results
  - `prompt_family_tree.html` - Genealogy visualization
  - `personality_evolution.html` - Dummy personality tracking
  - `index.html` - Main dashboard
  - `dummy_detail.html` - Individual dummy analysis

---

### **2. EXPERIMENT RUNNERS** (Keep Active Ones)

#### **Current/Active**
- `conversation_length_experiment_with_evolution.py` (27K) - **ACTIVE** - Full experiment with GEPA
- `conversation_length_experiment_v2.py` (22K) - **ACTIVE** - Conversation length testing
- `test_gepa_system.py` (21K) - **ACTIVE** - Main GEPA testing script

#### **Legacy/Superseded**
- `conversation_length_experiment.py` (9.4K) - **LEGACY** - Original version (v2 is better)
- `quick_gepa_test.py` (5.5K) - **UTILITY** - Quick validation tool
- `quick_conversation_test.py` (9.0K) - **UTILITY** - Quick conversation check

---

### **3. TEMPORARY TEST FILES** (Can Delete)

#### **Debug/Fix Tests** (Completed fixes - no longer needed)
- `test_conversation_fixes.py` (7.0K) - ❌ DELETE
- `test_enhanced_gepa.py` (4.3K) - ❌ DELETE
- `test_evaluation_fix.py` (5.3K) - ❌ DELETE
- `test_gepa_fix.py` (5.0K) - ❌ DELETE
- `test_mutation_validation.py` (6.2K) - ❌ DELETE
- `test_old_validation.py` (5.4K) - ❌ DELETE
- `test_optimized_flow.py` (2.4K) - ❌ DELETE
- `test_prompt_length.py` (2.2K) - ❌ DELETE
- `test_simple_mutation.py` (4.8K) - ❌ DELETE
- `simple_conversation_mock.py` (15K) - ❌ DELETE (or keep as utility?)

---

### **4. VISUALIZATION & ANALYSIS**

#### **Visualizer System**
- `conversation_journey_visualizer.html` - **KEEP** - D3.js conversation analysis
- `experiment_api_server.py` (6.6K) - **KEEP** - API for visualizer
- `start_visualizer.py` (1.6K) - **KEEP** - Launcher script

---

### **5. DATA STRUCTURE**

```
data/
├── comments/                    # User experiment annotations ✅ KEEP
├── conversations/               # Conversation logs ✅ KEEP
├── experiments/                 # Experiment results ✅ KEEP
│   ├── gepa_optimization_exp_*.json          (20 files - keep recent)
│   ├── continuous_conversation_*.json        (keep all)
│   └── conversation_length_exp_*.json        (keep all)
├── failure_analysis/           # Error logs ⚠️  REVIEW/CLEAN
├── personality_evolution/      # Dummy evolution ✅ KEEP
├── synthesis_analysis/         # Prompt analysis ✅ KEEP
├── ai_dummies.json             # Dummy definitions ✅ CORE
├── enhanced_gepa_test_results.json  # Old results ⚠️  ARCHIVE
├── gepa_fix_test_results.json       # Old results ⚠️  ARCHIVE
├── gepa_test_systematic.json        # Old results ⚠️  ARCHIVE
├── quick_test_results.json          # Old results ⚠️  ARCHIVE
├── validation_test_results.json     # Used by UI ✅ KEEP
└── validation_test_history.json     # History ✅ KEEP
```

---

### **6. DOCUMENTATION**

#### **Keep**
- `README.md` - Main documentation
- `requirements.txt` - Dependencies
- `reports/VISUALIZER_README.md` - Visualizer docs
- `reports/EXECUTIVE_SUMMARY_CONVERSATION_LENGTH.md` - Key findings

#### **Archive/Clean**
- 25+ analysis reports in `reports/` - **ARCHIVE** most, keep summaries

---

## 🎯 Cleanup Recommendations

### **IMMEDIATE ACTIONS**

#### **1. Delete Test Files** (Save ~60K code)
```bash
rm test_conversation_fixes.py
rm test_enhanced_gepa.py
rm test_evaluation_fix.py
rm test_gepa_fix.py
rm test_mutation_validation.py
rm test_old_validation.py
rm test_optimized_flow.py
rm test_prompt_length.py
rm test_simple_mutation.py
```

#### **2. Archive Legacy Files** (Move to `legacy/`)
```bash
mkdir -p legacy
mv conversation_length_experiment.py legacy/
mv assessment_system_llm_based.py legacy/
```

#### **3. Clean Old Data**
```bash
mkdir -p data/archive
mv data/enhanced_gepa_test_results.json data/archive/
mv data/gepa_fix_test_results.json data/archive/
mv data/gepa_test_systematic.json data/archive/
mv data/quick_test_results.json data/archive/
```

#### **4. Archive Old Reports** (Keep only key docs)
```bash
mkdir -p reports/archive
# Move 20+ old analysis reports to archive
# Keep: README, VISUALIZER_README, EXECUTIVE_SUMMARY
```

---

## 📦 Core System Dependencies

### **Module Dependency Graph**

```
config.py
    ↓
models.py ← conversation_simulator.py
    ↓           ↓
    ↓      personality_materializer.py
    ↓           ↓
    ↓      conversation_storage.py
    ↓           ↓
    ↓      assessment_system_v3_quantitative.py
    ↓           ↓
    ↓      prompt_optimizer.py (GEPA Engine)
    ↓           ↓
    └─────→ web_interface.py
                ↓
          templates/*.html
```

---

## 🔧 Simplification Strategy

### **Phase 1: Cleanup** (Today)
1. ✅ Commit everything to git (DONE)
2. Delete temporary test files
3. Archive legacy code
4. Clean old data files
5. Organize reports

### **Phase 2: Consolidation** (Future)
1. Merge experiment runners into single modular script
2. Simplify web_interface.py (separate template strings)
3. Create unified CLI interface
4. Document API properly

### **Phase 3: Optimization** (Future)
1. Reduce prompt_optimizer.py size (modularize)
2. Clean up web_interface.py templates
3. Improve code reusability

---

## 📈 Final Statistics

### **Before Cleanup**
- **Python Files**: 29 files, ~450K total code
- **Templates**: 7 HTML files
- **Data Files**: ~100+ JSON files
- **Reports**: 27 markdown files

### **After Cleanup** (Estimated)
- **Python Files**: ~15 core files, ~350K code
- **Templates**: 7 HTML files (unchanged)
- **Data Files**: ~30 active + archived rest
- **Reports**: ~5 key docs + archive

### **Redundancy Reduction**: ~22% code, ~70% test files

---

## 🎓 System Purpose Summary

**Primary Function**: Optimize AI coaching conversations for social skills development using evolutionary algorithms

**Key Innovation**: GEPA system evolves prompts across multiple assessment dimensions to find Pareto-optimal solutions

**User Interface**: Web-based visualization dashboard with experiment tracking, comment annotation, and genealogy analysis

---

## ✅ Next Steps

1. Review and approve cleanup plan
2. Execute cleanup (with git backup)
3. Test core functionality
4. Push to GitHub
5. Document simplified architecture

