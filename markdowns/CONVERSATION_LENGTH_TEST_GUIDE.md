# 📚 Conversation Length Test - Code Guide

## 🎯 What Does This Test Do?

The **conversation length experiment** tests how AI mentor conversations affect students over time. It measures:
- How long conversations can run before naturally ending
- How students' assessment scores change during the conversation
- How students' personalities evolve through the conversation

---

## 🏗️ Architecture Overview

```
conversation_length_experiment_with_evolution.py
├── Main experiment coordinator
├── Runs conversations with personality evolution
├── Tracks assessment scores at milestones
└── Saves all results to JSON files
```

### **Key Components:**

1. **ConversationLengthExperimentWithEvolution** (Main Class)
2. **ConversationSimulator** (Generates actual conversations)
3. **AssessmentSystem** (Evaluates student progress)
4. **PersonalityMaterializer** (Tracks personality changes)

---

## 🔄 How It Works: Step-by-Step

### **Phase 1: Setup**
```python
# Initialize the experiment
experiment = ConversationLengthExperimentWithEvolution()

# Load test dummies (students)
dummies = [AIDummy.model_validate(data) for data in dummy_data]

# Configure experiment
max_rounds = 10          # Up to 10 conversation rounds
milestones = [2, 5, 8, 10]  # Check progress at these points
```

### **Phase 2: For Each Student (Dummy)**

#### **Step 1: Pre-Assessment**
```python
# Measure baseline social skills
pre_assessment = await assessment_system.generate_pre_assessment(dummy)
# Example: Student scores 2.5/5 in social skills
```

#### **Step 2: Run Conversation**
```python
# Simulate natural conversation between student and AI mentor
conversation = await conversation_simulator.simulate_conversation_async(
    dummy=dummy,
    num_rounds=max_rounds,
    custom_system_prompt=base_prompt
)
```

**What happens in the conversation:**
```
Round 1:
  Student: "Hi, I'm struggling with social anxiety..."
  AI Mentor: "That's brave of you to share. Let's work on..."

Round 2:
  Student: "Okay, I tried your advice but..."
  AI Mentor: "Great progress! Now let's try..."

... continues until natural ending or max_rounds ...
```

#### **Step 3: Milestone Checkpoints** (if enabled)
```python
# At rounds 2, 5, 8, 10 - check progress
for milestone_round in [2, 5, 8, 10]:
    # Take snapshot of conversation so far
    partial_conversation = conversation[:milestone_round]
    
    # Materialize personality changes
    evolution_stage = await personality_materializer.materialize(
        dummy, partial_conversation
    )
    
    # Assess progress
    milestone_assessment = await assessment_system.generate_post_assessment(
        dummy, pre_assessment, partial_conversation
    )
```

#### **Step 4: Personality Evolution**
```python
# Track how student's personality changed
evolution_stage = await personality_materializer.materialize_personality(
    dummy=dummy,
    conversation=conversation,
    ...
)

# Example changes tracked:
# - Fears become more specific: "social events" → "speaking at club fair"
# - Solutions accepted: "try practicing with roommate"
# - Progress indicators: "willing to email NGO contact"
# - Anxiety level: 8/10 → 6/10
```

#### **Step 5: Post-Assessment**
```python
# Measure final social skills after conversation
post_assessment = await assessment_system.generate_post_assessment(
    dummy, pre_assessment, conversation
)
# Example: Student now scores 3.2/5 (improved by +0.7)
```

### **Phase 3: Save Results**
```python
# Save to JSON file
experiment_data = {
    "experiment_info": {...},
    "results": [
        {
            "dummy_name": "Sarah Wright",
            "pre_assessment_score": 2.5,
            "final_assessment_score": 3.2,
            "final_improvement": +0.7,
            "total_conversation_turns": 11,
            "personality_evolution": {
                "evolution_stages": 4,
                "final_anxiety_level": 6,
                ...
            },
            "milestone_results": [...]
        }
    ]
}

# Save to: data/experiments/continuous_conversation_with_evolution_exp_TIMESTAMP.json
```

---

## 🔍 Key Functions Explained

### **1. `run_experiment()` - Main Entry Point**

**Purpose:** Orchestrates the entire experiment for multiple students

**Flow:**
```python
async def run_experiment(dummies, max_rounds, milestones, ...):
    # 1. Print configuration
    print("Starting experiment with X dummies...")
    
    # 2. Run all students in parallel
    tasks = [run_dummy_experiment(dummy, ...) for dummy in dummies]
    results = await asyncio.gather(*tasks)
    
    # 3. Save all results
    save_to_json(experiment_data)
    
    # 4. Print analysis
    print_analysis(results)
```

### **2. `run_dummy_experiment()` - Single Student Test**

**Purpose:** Run the complete test for one student

**Flow:**
```python
async def run_dummy_experiment(dummy, max_rounds, milestones, ...):
    # 1. Initialize personality evolution
    dummy.initialize_personality_evolution()
    
    # 2. Pre-assessment
    pre_assessment = await generate_pre_assessment(dummy)
    
    # 3. Conversation with milestones
    conversation, milestone_assessments = await simulate_conversation_with_milestones(...)
    
    # 4. Materialize personality evolution
    evolution_stage = await materialize_personality(dummy, conversation)
    
    # 5. Post-assessment
    post_assessment = await generate_post_assessment(dummy, pre_assessment, conversation)
    
    # 6. Return results
    return {
        "dummy_name": dummy.name,
        "pre_assessment_score": 2.5,
        "final_assessment_score": 3.2,
        ...
    }
```

### **3. `_simulate_conversation_with_milestones()` - Conversation Flow**

**Purpose:** Run conversation and process milestones efficiently

**Two-Phase Approach:**

**Phase 1: Continuous Conversation**
```python
async def _run_continuous_conversation(dummy, base_prompt, max_rounds):
    # Run conversation without interruptions
    conversation = await conversation_simulator.simulate_conversation_async(
        dummy=dummy,
        num_rounds=max_rounds,
        custom_system_prompt=base_prompt
    )
    return conversation
```

**Phase 2: Parallel Milestone Processing**
```python
async def _process_milestones_parallel(dummy, conversation, milestones, ...):
    # Create tasks for each milestone
    tasks = []
    for milestone_round in milestones:
        partial_conv = conversation[:milestone_round]
        task = process_single_milestone(dummy, partial_conv, milestone_round)
        tasks.append(task)
    
    # Process all milestones in parallel
    milestone_results = await asyncio.gather(*tasks)
    return milestone_results
```

### **4. `_process_single_milestone()` - Checkpoint Analysis**

**Purpose:** Analyze conversation state at a specific round

```python
async def _process_single_milestone(dummy, partial_conversation, milestone_round):
    # 1. Materialize personality evolution up to this point
    evolution_stage = await personality_materializer.materialize(
        dummy, partial_conversation, ...
    )
    
    # 2. Generate assessment at this milestone
    milestone_assessment = await assessment_system.generate_post_assessment(
        dummy, pre_assessment, partial_conversation
    )
    
    # 3. Return results
    return {
        "milestone_round": milestone_round,
        "milestone_score": milestone_assessment.average_score,
        "improvement": milestone_assessment.average_score - pre_score,
        "materialized_traits": {...}
    }
```

---

## 📊 Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│ START: conversation_length_experiment_with_evolution.py     │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│ Load AI Dummies from data/ai_dummies.json                   │
│ Example: Sarah Wright, Marcus Johnson, Emily Chen           │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│ FOR EACH DUMMY (in parallel):                               │
│   ┌──────────────────────────────────────┐                 │
│   │ 1. Pre-Assessment                     │                 │
│   │    └─> Baseline score: 2.5/5          │                 │
│   └──────────────────────────────────────┘                 │
│                   │                                          │
│                   ▼                                          │
│   ┌──────────────────────────────────────┐                 │
│   │ 2. Conversation Simulation            │                 │
│   │    ├─> Round 1: Student opens up      │                 │
│   │    ├─> Round 2: AI provides advice    │                 │
│   │    ├─> Round 3: Student responds      │                 │
│   │    └─> ... continues ...              │                 │
│   └──────────────────────────────────────┘                 │
│                   │                                          │
│                   ▼                                          │
│   ┌──────────────────────────────────────┐                 │
│   │ 3. Milestone Checkpoints (parallel)   │                 │
│   │    ├─> Round 2: Check progress        │                 │
│   │    ├─> Round 5: Check progress        │                 │
│   │    ├─> Round 8: Check progress        │                 │
│   │    └─> Round 10: Final check          │                 │
│   └──────────────────────────────────────┘                 │
│                   │                                          │
│                   ▼                                          │
│   ┌──────────────────────────────────────┐                 │
│   │ 4. Personality Evolution              │                 │
│   │    ├─> Materialize trait changes      │                 │
│   │    ├─> Track anxiety reduction        │                 │
│   │    └─> Capture accepted solutions     │                 │
│   └──────────────────────────────────────┘                 │
│                   │                                          │
│                   ▼                                          │
│   ┌──────────────────────────────────────┐                 │
│   │ 5. Post-Assessment                    │                 │
│   │    └─> Final score: 3.2/5 (+0.7)      │                 │
│   └──────────────────────────────────────┘                 │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│ Aggregate Results & Save                                     │
│ ├─> data/experiments/continuous_conversation_..._TIMESTAMP   │
│ └─> data/conversations/dummy_[ID].json                       │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎮 How to Run It

### **Basic Usage:**
```bash
python conversation_length_experiment_with_evolution.py \
    --dummies 3 \
    --max-rounds 10 \
    --save-details
```

### **Command Line Arguments:**

| Argument | Default | Description |
|----------|---------|-------------|
| `--dummies` | 5 | Number of students to test |
| `--max-rounds` | 10 | Maximum conversation rounds |
| `--milestones` | 2,5,8,10 | When to check progress |
| `--save-details` | False | Save full conversation transcripts |
| `--no-assessments` | False | Disable assessment system |

### **Examples:**

**Quick test with 1 student:**
```bash
python conversation_length_experiment_with_evolution.py --dummies 1 --max-rounds 5
```

**Full test with details:**
```bash
python conversation_length_experiment_with_evolution.py \
    --dummies 10 \
    --max-rounds 10 \
    --save-details
```

**Conversation-only mode (no assessments):**
```bash
python conversation_length_experiment_with_evolution.py \
    --dummies 5 \
    --no-assessments
```

---

## 📁 Output Files

### **1. Experiment Results**
```
data/experiments/continuous_conversation_with_evolution_exp_20251017_123456.json
```

**Structure:**
```json
{
  "experiment_info": {
    "timestamp": "2025-10-17T12:34:56",
    "num_dummies": 3,
    "max_rounds": 10,
    "personality_evolution_enabled": true
  },
  "results": [
    {
      "dummy_name": "Sarah Wright",
      "pre_assessment_score": 2.5,
      "final_assessment_score": 3.2,
      "final_improvement": 0.7,
      "total_conversation_turns": 11,
      "milestone_results": [...],
      "personality_evolution": {
        "evolution_stages": 4,
        "final_anxiety_level": 6,
        ...
      }
    }
  ]
}
```

### **2. Conversation Storage**
```
data/conversations/dummy_[DUMMY_ID].json
```

**Contains:** All conversations for a specific student across all experiments

### **3. Personality Evolution**
```
data/personality_evolution/dummy_[DUMMY_ID]_evolution.json
```

**Tracks:** How student's personality evolved across conversations

---

## 🔧 Key Configuration Options

### **In the Code:**

**Base Prompt (AI Mentor's Instructions):**
```python
base_prompt = """You are a helpful peer mentor for college students. 
Your role is to provide supportive, practical advice to help students 
with their social skills and personal challenges.

IMPORTANT GUIDELINES:
- Maintain your role as mentor (never act like the student)
- Provide detailed, helpful responses
- Give specific, actionable advice with examples
- Be encouraging but realistic
"""
```

**Milestones:**
```python
milestones = [2, 5, 8, 10]  # Check progress at these conversation rounds
```

**Parallel Processing:**
```python
# All students tested in parallel for speed
tasks = [run_dummy_experiment(dummy, ...) for dummy in dummies]
results = await asyncio.gather(*tasks)
```

---

## 🐛 Common Issues & Solutions

### **Issue 1: Role Confusion**
**Symptom:** AI generates dialogue for both mentor and student  
**Solution:** ✅ FIXED - See commit c23aab9

### **Issue 2: Conversations Too Short**
**Symptom:** Conversations end after 2-3 rounds  
**Check:** End detection prompt sensitivity  
**Solution:** Adjust `conversation_end_detection_prompt` in `prompts/conversation_prompts.yaml`

### **Issue 3: Assessment System Not Available**
**Symptom:** "Assessment system not available" warning  
**Solution:** Either:
- Run with `--no-assessments` flag
- Ensure `assessment_system_llm_based.py` exists

### **Issue 4: Slow Performance**
**Symptom:** Takes too long with many dummies  
**Reason:** Network latency + LLM API calls  
**Solution:** Reduce `--dummies` or `--max-rounds`

---

## 📈 Interpreting Results

### **Good Results:**
- ✅ Improvement: +0.5 to +1.5 points
- ✅ Conversation length: 8-12 rounds
- ✅ Evolution stages: 3-5 captured
- ✅ Anxiety reduction: -1 to -3 points

### **Concerning Results:**
- ⚠️ Improvement: < +0.2 or negative
- ⚠️ Conversation length: < 5 rounds
- ⚠️ Evolution stages: 0-1 captured
- ⚠️ No anxiety change

---

## 🎓 Summary

The conversation length test:
1. **Simulates** realistic student-mentor conversations
2. **Tracks** how conversations affect student progress
3. **Measures** assessment score changes at milestones
4. **Captures** personality evolution throughout
5. **Saves** all data for analysis and visualization

**Key innovation:** Optimized flow that runs conversation first, then processes milestones in parallel for better performance!

---

## 🔗 Related Files

- `conversation_simulator.py` - Generates conversations
- `assessment_system_llm_based.py` - Evaluates progress
- `personality_materializer.py` - Tracks personality changes
- `personality_evolution_storage.py` - Stores evolution data
- `conversation_storage.py` - Stores conversations
- `prompts/conversation_prompts.yaml` - Conversation prompts

---

**Questions? Check the code comments or run with `--help`!**

