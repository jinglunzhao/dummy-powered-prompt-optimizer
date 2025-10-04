#!/usr/bin/env python3
"""
Test the old validation logic to see what's causing the failures
"""

def test_old_validation_logic():
    """Test the old validation logic that was supposedly failing"""
    
    print("🧪 Testing OLD Validation Logic")
    print("=" * 50)
    
    # Test prompts from the terminal output
    test_prompts = [
        # These are the actual prompts that were failing in the terminal
        '"You are a supportive peer mentor for college students who combines practical advice with emotional support."',
        '"You are a deeply attentive social skills mentor who helps college students build confidence through personalized guidance."',
        '"You are a thoughtful social skills mentor who actively listens before responding, using strategic questioning."',
        '"You are a supportive peer mentor for college students who combines practical advice with deep emotional understanding."',
        
        # Test variations
        'You are a supportive peer mentor for college students who combines practical advice with emotional support.',
        '  You are a supportive peer mentor for college students who combines practical advice with emotional support.  ',
        '"You are a supportive peer mentor"',  # Short with quotes
        'You are a supportive peer mentor',  # Short without quotes
    ]
    
    for i, prompt_text in enumerate(test_prompts):
        print(f"\nTest {i+1}: {prompt_text[:60]}...")
        
        # OLD VALIDATION LOGIC (exactly as it was)
        mutated_prompt_text = prompt_text.strip()
        
        # This is the exact old validation that was failing
        old_validation_result = not mutated_prompt_text.lower().startswith("you are") or len(mutated_prompt_text) < 20
        
        print(f"   📝 Text: '{mutated_prompt_text}'")
        print(f"   📊 Length: {len(mutated_prompt_text)}")
        print(f"   🔍 Lowercase: '{mutated_prompt_text.lower()}'")
        print(f"   🔍 Starts with 'you are': {mutated_prompt_text.lower().startswith('you are')}")
        print(f"   🔍 Length >= 20: {len(mutated_prompt_text) >= 20}")
        
        if old_validation_result:
            print(f"   ❌ OLD VALIDATION FAILED")
            print(f"      Reason: {'Does not start with \"you are\"' if not mutated_prompt_text.lower().startswith('you are') else 'Too short'}")
        else:
            print(f"   ✅ OLD VALIDATION PASSED")

def test_new_validation_logic():
    """Test the new validation logic for comparison"""
    
    print("\n🧪 Testing NEW Validation Logic")
    print("=" * 50)
    
    test_prompts = [
        '"You are a supportive peer mentor for college students who combines practical advice with emotional support."',
        '"You are a deeply attentive social skills mentor who helps college students build confidence through personalized guidance."',
        '"You are a thoughtful social skills mentor who actively listens before responding, using strategic questioning."',
        '"You are a supportive peer mentor for college students who combines practical advice with deep emotional understanding."',
    ]
    
    for i, prompt_text in enumerate(test_prompts):
        print(f"\nTest {i+1}: {prompt_text[:60]}...")
        
        # NEW VALIDATION LOGIC
        mutated_prompt_text = prompt_text.strip()
        
        # More robust validation - check for "you are" anywhere in first 50 chars, handle quotes
        first_part = mutated_prompt_text[:50].lower()
        has_you_are = "you are" in first_part
        has_proper_length = len(mutated_prompt_text) >= 20
        
        print(f"   📝 Text: '{mutated_prompt_text}'")
        print(f"   📊 Length: {len(mutated_prompt_text)}")
        print(f"   🔍 First 50 chars: '{first_part}'")
        print(f"   🔍 Contains 'you are': {has_you_are}")
        print(f"   🔍 Length >= 20: {has_proper_length}")
        
        if not has_you_are or not has_proper_length:
            print(f"   ❌ NEW VALIDATION FAILED")
        else:
            print(f"   ✅ NEW VALIDATION PASSED")

def analyze_terminal_output():
    """Analyze what we see in the terminal output"""
    
    print("\n🔍 Analyzing Terminal Output")
    print("=" * 50)
    
    # From the terminal output, we see:
    terminal_examples = [
        '"You are a supportive peer mentor for college students who combines practical advice with emotional ...',
        '"You are a deeply attentive social skills mentor who helps college students build confidence through...',
        '"You are a thoughtful social skills mentor who actively listens before responding, using strategic p...',
    ]
    
    print("From terminal output, the prompts that were failing:")
    for i, prompt in enumerate(terminal_examples):
        print(f"\nExample {i+1}: {prompt}")
        
        # Test with old validation
        old_result = not prompt.lower().startswith("you are") or len(prompt) < 20
        print(f"   Old validation result: {'FAIL' if old_result else 'PASS'}")
        
        if old_result:
            if not prompt.lower().startswith("you are"):
                print(f"   ❌ Reason: Does not start with 'you are'")
                print(f"   🔍 Actual start: '{prompt.lower()[:20]}'")
            if len(prompt) < 20:
                print(f"   ❌ Reason: Too short (length: {len(prompt)})")

if __name__ == "__main__":
    test_old_validation_logic()
    test_new_validation_logic()
    analyze_terminal_output()

