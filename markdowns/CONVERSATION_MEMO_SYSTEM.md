# Conversation Memo System
**Realistic AI Coach Knowledge Management**

## 🎯 Purpose

The AI coach should only know what the student explicitly shares in conversation, not have access to their full psychological profile. This makes the coaching more realistic and fair.

---

## 🔄 How It Works

### Before (Unrealistic):
```python
# AI had full access to student's internal profile
user_content = f"Student Profile: {dummy.get_character_summary()}"
# This included: personality scores, anxiety levels, all fears, challenges, etc.
```
❌ AI could "read the student's mind"  
❌ Unrealistic - real coaches don't have this information  
❌ Gives AI unfair advantage in assessments

### After (Realistic):
```python
# AI only knows: student's name and what they've shared
user_content = f"You are meeting with {dummy.name}, a student seeking help with social skills.\n\n"

# After 6+ rounds, generate memo from conversation
if len(conversation.turns) >= 12:
    memo = await self._generate_conversation_memo(conversation, dummy)
    user_content += f"{memo}\n\n"

# Add recent conversation (last 6 turns)
user_content += "Recent Conversation:\n{transcript}"
```
✅ AI learns about student through conversation  
✅ Realistic coaching scenario  
✅ Fair assessment of coaching effectiveness

---

## 📋 Memo Generation

### When Memos Are Generated
- **Trigger:** After 12+ turns (6+ conversation rounds)
- **Frequency:** Every time AI generates response after threshold
- **Content:** Key points student explicitly shared

### Memo Format
```
Key Points from Previous Conversation:
- Student struggles with approaching peers in dining hall
- Goal: Join at least one study group this semester
- Mentioned fear of being judged for asking questions
- Action item: Practice small talk with one classmate this week
```

### Memo Generation Prompt
Located in `prompts/conversation_prompts.yaml`:
```yaml
conversation_memo_generation_prompt: |
  Based on this conversation, create a brief memo of key points 
  the AI coach should remember about the student.
  
  Create a concise memo (3-5 bullet points) covering:
  - What concerns/challenges the student has shared
  - What goals they mentioned
  - Any progress or action items discussed
  - Important context to remember
  
  Only include what the student explicitly shared.
```

---

## 🔍 Message Structure

### AI Coach Response Generation

**System Role:**
```
{coaching_prompt} + {ai_coach_system_addition}
```

**User Role:**
```
You are meeting with {student_name}, a student seeking help with social skills.

[Memo after 12+ turns]

Recent Conversation:
Amy: I've been having trouble making friends...
Assistant: That's a common challenge. Can you tell me more?
Amy: Well, I get anxious in group settings...
Assistant: I understand. What specific situations trigger this?
...

Provide your next response to Amy.
```

### Student Response Generation

Student DOES know their own personality (keeps full profile):
```python
# Student knows themselves fully
user_content = f"Student Profile: {dummy.get_character_summary()}\n\n"
user_content += "Conversation History:\n{transcript}"
```

---

## 💡 Key Benefits

### 1. **Realistic Coaching**
- AI coach learns about student naturally
- Mirrors real-world coaching scenarios
- Student reveals information over time

### 2. **Fair Assessment**
- AI must work with limited information
- Better test of coaching prompt effectiveness
- Can't rely on "mind reading"

### 3. **Better Conversation Flow**
- AI asks clarifying questions
- Student has opportunity to share
- More natural dialogue progression

### 4. **Accurate Testing**
- Tests prompt's ability to elicit information
- Measures active listening and questioning skills
- Evaluates relationship building

---

## 🔧 Implementation Details

### Code Location
- **File:** `conversation_simulator.py`
- **Memo Generation:** `_generate_conversation_memo()` (lines ~123-159)
- **AI Response:** `_generate_ai_response_async()` (lines ~161-196)
- **Student Response:** `_generate_character_response_async()` (keeps full profile)

### Memo Update Strategy
```python
if len(conversation.turns) >= 12:  # After 6+ rounds
    memo = await self._generate_conversation_memo(conversation, dummy)
```

**Why 12 turns?**
- 12 turns = 6 conversation rounds (student + AI)
- Gives student time to share information
- Generates memo when earlier context might be lost

### Context Window
- **Last 6 turns always included** (recent conversation)
- **Memo summarizes earlier context** (turns 1-N where N > 6)
- **Combined:** AI has recent details + historical summary

---

## 📊 Information Flow

```
Turn 1-12:
┌──────────────────────────────────────┐
│ AI knows: Name + Recent 6 turns only │
└──────────────────────────────────────┘

Turn 13+:
┌──────────────────────────────────────┐
│ AI knows:                             │
│ • Name                                │
│ • Memo (what student shared so far)  │
│ • Recent 6 turns                      │
└──────────────────────────────────────┘

Student always knows:
┌──────────────────────────────────────┐
│ • Full personality profile            │
│ • All fears, goals, challenges        │
│ • Conversation history                │
└──────────────────────────────────────┘
```

---

## 🎓 Example Comparison

### Unrealistic (Before):
```
AI's view at turn 1:
  Student: Amy
  Personality: Extraversion 3/10, Neuroticism 8/10
  Anxiety Level: 7/10
  Fears: Social rejection, public speaking, being judged
  Challenges: Starting conversations, maintaining eye contact
  
  [AI already knows everything before student speaks]
```

### Realistic (After):
```
AI's view at turn 1:
  You are meeting with Amy, a student seeking help with social skills.
  
  Amy is about to speak with you. Prepare to listen and help.

AI's view at turn 7 (after memo generation):
  You are meeting with Amy, a student seeking help with social skills.
  
  Key Points from Previous Conversation:
  - Amy mentioned feeling anxious in group settings
  - Goal: Join a study group this semester
  - Challenged by initiating conversations
  
  Recent Conversation:
  Amy: I tried talking to someone today...
  Assistant: That's great progress! How did it go?
  [etc...]
```

---

## ⚙️ Configuration

### Customizable Parameters

In `conversation_simulator.py`, you can adjust:

```python
# Memo generation threshold
if len(conversation.turns) >= 12:  # Change this number
    
# Context window size
for turn in conversation.turns[-6]:  # Change this number

# Memo update frequency
# Currently: Every AI response after threshold
# Could be: Every N rounds, or specific milestones
```

---

## 🚀 Benefits for Experiments

### GEPA Optimization
- Tests prompt's ability to build rapport
- Evaluates information-gathering techniques
- Measures student engagement and openness

### Assessment System
- More accurate measure of coaching effectiveness
- Can't inflate scores with privileged information
- Tests real coaching skills

### Personality Evolution
- Student shares information naturally over time
- AI coach adapts based on what they learn
- More realistic trait materialization

---

**This change makes the system more realistic and better tests actual coaching effectiveness!** 🎯

