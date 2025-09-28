#!/usr/bin/env python3
"""
Compare old vs new assessment prompts to show the difference
"""

# OLD PROMPT (causing inconsistency):
old_prompt = """You are Test Dummy, a Computer Science student.
Your personality traits: Balanced, Balanced, Balanced, Balanced, Balanced
Your social anxiety level: Moderate
Your current challenges: Academic failure

You are taking a self-assessment about your social skills. Please answer ALL 20 questions honestly based on your character and experiences.

For each question, please provide:
1. Your self-rating (1=Not True, 2=Somewhat True, 3=Mostly True, 4=Very True)
2. A brief explanation of why you rated yourself this way

Questions:
1. I ask for help when I need it.
2. I stay calm when dealing with problems.
...

Please respond in this exact format:
1. [Rating: X/4] [Brief explanation]
2. [Rating: X/4] [Brief explanation]
...

Be honest and authentic to your character. Consider your personality, anxiety level, and recent experiences."""

# NEW PROMPT (deterministic):
new_prompt = """You are Test Dummy, a Computer Science student.
Your personality traits: Balanced, Balanced, Balanced, Balanced, Balanced
Your social anxiety level: Moderate
Your current challenges: Academic failure

You are taking a self-assessment about your social skills. Provide consistent ratings based on your personality profile, with potential improvements from coaching.

SCORING GUIDELINES:
- Extraversion 5/10: Moderate social confidence
- Agreeableness 5/10: Moderate cooperation
- Conscientiousness 5/10: Moderate responsibility
- Anxiety Level 5/10: Moderate anxiety

BASELINE ASSESSMENT: No recent coaching conversation.

Questions:
1. I ask for help when I need it.
2. I stay calm when dealing with problems.
...

Respond in EXACTLY this format:
1. [Rating: X/4] [Explanation based on personality + coaching impact]
2. [Rating: X/4] [Explanation based on personality + coaching impact]
...

Consider: Base personality traits + no coaching yet."""

print("🔍 PROMPT COMPARISON ANALYSIS")
print("=" * 60)

print("\n❌ OLD PROMPT ISSUES:")
print("1. Vague instruction: 'Be honest and authentic to your character'")
print("2. No specific scoring criteria")
print("3. Relies on LLM interpretation of 'Balanced' personality")
print("4. Allows subjective 'authentic' responses")
print("5. No deterministic mapping to scores")

print("\n✅ NEW PROMPT IMPROVEMENTS:")
print("1. Explicit scoring guidelines with specific ranges")
print("2. Clear personality-to-score mapping")
print("3. Deterministic criteria (5/10 = Moderate)")
print("4. Structured format requirements")
print("5. Objective scoring based on traits")

print("\n🎯 WHY THIS ACHIEVES CONSISTENCY:")
print("1. OLD: LLM interprets 'Balanced' → Could be 2, 2.5, 3, or 3.5")
print("2. NEW: LLM sees '5/10: Moderate' → Always chooses 2-3 range")
print("3. OLD: Subjective 'authentic' → Random variation")
print("4. NEW: Objective 'based on personality' → Deterministic")
print("5. OLD: No constraints → High temperature causes variation")
print("6. NEW: Clear constraints → Low temperature + guidelines = consistent")

print("\n📊 THE MAGIC:")
print("Instead of asking: 'How do you feel about asking for help?'")
print("We now ask: 'Based on your 5/10 extraversion (moderate social confidence),")
print("rate your help-seeking behavior.'")
print("\nThis gives the LLM a SPECIFIC CRITERION to follow, not a SUBJECTIVE FEELING.")
