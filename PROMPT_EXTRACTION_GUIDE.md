# Prompt Extraction Guide
*Separating Prompts from Code for Better Readability*

## 📁 New Structure

```
prompts/
├── prompt_loader.py          # Utility to load prompts from YAML
├── optimizer_prompts.yaml    # GEPA evolution prompts
├── materializer_prompts.yaml # Personality materialization prompts
├── conversation_prompts.yaml # Conversation simulator prompts
└── assessment_prompts.yaml   # Assessment generation prompts (future)
```

## 🎯 Benefits

### **Before:**
- 85KB prompt_optimizer.py with 50+ embedded prompts
- Hard to read, maintain, and version control prompts
- Mixing logic and content

### **After:**
- Clean Python code focusing on logic
- Easy-to-edit YAML files for prompts
- Version control friendly (diff shows actual prompt changes)
- Easier A/B testing of prompts

## 📝 Usage Examples

### **Load a Prompt:**

```python
from prompts.prompt_loader import prompt_loader

# Load and format a mutation prompt
mutation_prompt = prompt_loader.get_prompt(
    'optimizer_prompts.yaml',
    'mutation_prompt',
    parent_prompt=parent.prompt_text,
    avg_improvement=0.5,
    generation=2,
    synthesis_analysis="..."
)
```

### **Load All Prompts from a File:**

```python
# Load all optimizer prompts
prompts = prompt_loader.load_prompts('optimizer_prompts.yaml')
mutation_template = prompts['mutation_prompt']
crossover_template = prompts['crossover_prompt']
```

## 🔄 Migration Plan

### **Phase 1: Extract Prompts** ✅ DONE
- [x] Create `prompts/` directory
- [x] Create `prompt_loader.py` utility
- [x] Extract prompts to YAML files:
  - [x] optimizer_prompts.yaml (mutation, crossover, synthesis)
  - [x] materializer_prompts.yaml (materialization)
  - [x] conversation_prompts.yaml (student, coach, end detection)

### **Phase 2: Update Code** (Next)
- [ ] Update `prompt_optimizer.py` to use prompt_loader
- [ ] Update `personality_materializer.py` to use prompt_loader
- [ ] Update `conversation_simulator.py` to use prompt_loader
- [ ] Add tests to ensure prompts load correctly

### **Phase 3: Cleanup** (Future)
- [ ] Remove old embedded prompts
- [ ] Update documentation
- [ ] Create prompt version tracking

## 📦 Extracted Prompts

### **optimizer_prompts.yaml**
- `mutation_prompt` - Creates evolved prompts based on synthesis
- `crossover_prompt` - Combines two parent prompts
- `synthesis_analysis_prompt` - Analyzes conversation performance
- `reflection_prompt` - Reflects on individual conversations

### **materializer_prompts.yaml**
- `materialization_prompt` - Converts abstract traits to concrete behaviors
- `fallback_summary_prompt` - Creates conversation summaries

### **conversation_prompts.yaml**
- `student_opening_prompt` - Student character initialization
- `ai_coach_system_addition` - Important instructions for AI coach
- `student_response_system` - Student character system prompt
- `conversation_end_detection_prompt` - Detects natural conversation endings
- `end_detection_system` - System prompt for end detection

## 🛠️ Implementation Steps

### **For prompt_optimizer.py:**

Replace this:
```python
mutation_prompt = f"""
CURRENT SYSTEM PROMPT: "{parent.prompt_text}"
PERFORMANCE CONTEXT:
...
"""
```

With this:
```python
from prompts.prompt_loader import prompt_loader

mutation_prompt = prompt_loader.get_prompt(
    'optimizer_prompts.yaml',
    'mutation_prompt',
    parent_prompt=parent.prompt_text,
    avg_improvement=avg_improvement,
    generation=parent.generation,
    synthesis_analysis=synthesis_analysis
)
```

### **For personality_materializer.py:**

Replace this:
```python
prompt = f"""Analyze this conversation and materialize abstract traits...
STUDENT: {dummy.name}
...
"""
```

With this:
```python
from prompts.prompt_loader import prompt_loader

prompt = prompt_loader.get_prompt(
    'materializer_prompts.yaml',
    'materialization_prompt',
    student_name=dummy.name,
    fears=', '.join(dummy.fears),
    challenges=', '.join(dummy.challenges),
    # ... other parameters
)
```

## 📊 Code Size Reduction

### **Estimated Savings:**

| File | Before | After | Reduction |
|------|--------|-------|-----------|
| prompt_optimizer.py | 85KB | ~60KB | **30%** |
| personality_materializer.py | 22KB | ~15KB | **32%** |
| conversation_simulator.py | 14KB | ~10KB | **29%** |
| **Total** | **121KB** | **85KB** | **~30%** |

## ✅ Requirements

Add to `requirements.txt`:
```
pyyaml>=6.0
```

## 🎓 Best Practices

1. **Versioning**: Keep old prompt versions in separate files (e.g., `optimizer_prompts_v1.yaml`)
2. **Documentation**: Add comments in YAML explaining prompt purpose
3. **Testing**: Create tests to ensure prompts format correctly
4. **A/B Testing**: Easy to create variant prompts for testing

## 🚀 Next Steps

1. Install PyYAML: `pip install pyyaml`
2. Update code files to use prompt_loader
3. Test functionality
4. Commit changes
5. Remove old embedded prompts

---

*This separation makes the codebase more maintainable and prompts easier to iterate on!*

