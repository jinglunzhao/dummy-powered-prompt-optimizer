#!/usr/bin/env python3
"""
Demo: How V3 System Calculates Conversation Effectiveness Without LLM
"""

def demo_effectiveness_calculation():
    """Demonstrate the effectiveness calculation process"""
    
    # Example: High effectiveness conversation from our test
    messages = """You've made incredible progress in your communication skills! Your confidence has improved dramatically, and you're now much more articulate and expressive. I've noticed you're making excellent eye contact and asking thoughtful questions. Your emotional regulation has also improved - you stay calm and composed even in difficult situations. Thank you! I do feel much more confident and relaxed now. The breathing techniques you taught me really help me stay calm, and I'm finding it easier to express myself clearly. Exactly! And I can see how much more empathetic and supportive you've become. You're now helping others feel better and thinking about how they feel. Your teamwork and cooperation skills have also developed significantly. You're becoming a natural leader! I'm really proud of my progress! I feel like I can now handle social situations with confidence and help others too. Thank you for all your guidance and support."""
    
    messages_lower = messages.lower()
    total_words = len(messages.split())
    
    print("🧪 DEMO: Conversation Effectiveness Calculation Without LLM")
    print("=" * 60)
    print(f"Conversation length: {total_words} words")
    print()
    
    # Communication effectiveness
    communication_positive = [
        "confident", "clear", "articulate", "expressive", "outgoing", "talkative",
        "eye contact", "listening", "asking questions", "speaking up", "communicating",
        "voice", "presentation", "explanation", "discussion", "conversation"
    ]
    
    communication_negative = [
        "quiet", "shy", "mumbling", "avoiding", "not speaking", "withdrawn",
        "poor communication", "unclear", "inarticulate", "tongue-tied"
    ]
    
    communication_coaching = [
        "practice", "technique", "skill", "improvement", "development",
        "training", "guidance", "feedback", "advice", "tip", "strategy"
    ]
    
    # Count indicators
    pos_count = sum(1 for word in communication_positive if word in messages_lower)
    neg_count = sum(1 for word in communication_negative if word in messages_lower)
    coach_count = sum(1 for word in communication_coaching if word in messages_lower)
    
    print("📊 COMMUNICATION EFFECTIVENESS CALCULATION:")
    print(f"Positive words found: {pos_count}")
    print(f"  Examples: {[word for word in communication_positive if word in messages_lower]}")
    print(f"Negative words found: {neg_count}")
    print(f"  Examples: {[word for word in communication_negative if word in messages_lower]}")
    print(f"Coaching quality words found: {coach_count}")
    print(f"  Examples: {[word for word in communication_coaching if word in messages_lower]}")
    print()
    
    # Calculate ratios
    pos_ratio = pos_count / total_words
    neg_ratio = neg_count / total_words
    coach_ratio = coach_count / total_words
    
    print("📈 RATIO CALCULATIONS:")
    print(f"Positive ratio: {pos_count}/{total_words} = {pos_ratio:.4f}")
    print(f"Negative ratio: {neg_count}/{total_words} = {neg_ratio:.4f}")
    print(f"Coaching ratio: {coach_count}/{total_words} = {coach_ratio:.4f}")
    print()
    
    # Apply formula
    effectiveness = (pos_ratio - neg_ratio) * 20 + coach_ratio * 10
    final_effectiveness = max(-3.0, min(3.0, effectiveness))
    
    print("🧮 EFFECTIVENESS FORMULA:")
    print(f"effectiveness = (positive_ratio - negative_ratio) * 20 + coaching_ratio * 10")
    print(f"effectiveness = ({pos_ratio:.4f} - {neg_ratio:.4f}) * 20 + {coach_ratio:.4f} * 10")
    print(f"effectiveness = {pos_ratio - neg_ratio:.4f} * 20 + {coach_ratio * 10:.4f}")
    print(f"effectiveness = {(pos_ratio - neg_ratio) * 20:.4f} + {coach_ratio * 10:.4f}")
    print(f"effectiveness = {effectiveness:.4f}")
    print(f"Final effectiveness (clamped): {final_effectiveness:.4f}")
    print()
    
    print("🎯 RESULT:")
    if final_effectiveness > 0.5:
        print(f"✅ HIGH EFFECTIVENESS ({final_effectiveness:.2f}) - Conversation was very helpful!")
    elif final_effectiveness > 0.1:
        print(f"⚠️  MODERATE EFFECTIVENESS ({final_effectiveness:.2f}) - Conversation was somewhat helpful")
    elif final_effectiveness > -0.1:
        print(f"➖ NEUTRAL EFFECTIVENESS ({final_effectiveness:.2f}) - Conversation had minimal impact")
    elif final_effectiveness > -0.5:
        print(f"⚠️  LOW EFFECTIVENESS ({final_effectiveness:.2f}) - Conversation was not very helpful")
    else:
        print(f"❌ NEGATIVE EFFECTIVENESS ({final_effectiveness:.2f}) - Conversation was harmful")
    
    print()
    print("🔍 KEY INSIGHTS:")
    print("• No LLM needed - pure pattern matching and math")
    print("• Predefined dictionaries of effectiveness indicators")
    print("• Quantitative ratios based on word frequency")
    print("• Simple formula: (positive - negative) * 20 + coaching * 10")
    print("• Clamped to reasonable range (-3.0 to +3.0)")
    print("• Fast, reliable, and interpretable")

if __name__ == "__main__":
    demo_effectiveness_calculation()


