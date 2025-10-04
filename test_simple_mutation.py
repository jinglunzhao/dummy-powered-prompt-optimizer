#!/usr/bin/env python3
"""
Simple test for mutation prompt generation without genealogy tracker
"""

import asyncio
import aiohttp
from config import Config

async def test_simple_mutation():
    """Test mutation prompt generation directly with API"""
    
    print("🧪 Testing Simple Mutation Prompt Generation")
    print("=" * 50)
    
    # Test prompt
    parent_prompt_text = "You are a helpful peer mentor for college students. Be supportive and provide practical advice."
    synthesis_analysis = "The prompt shows good basic structure but could benefit from more specific guidance on emotional support and practical strategies."
    
    # Create mutation prompt
    mutation_prompt = f"""
You are an expert prompt engineer improving a social skills coaching system prompt based on comprehensive conversation analysis.

CURRENT SYSTEM PROMPT: "{parent_prompt_text}"

PERFORMANCE CONTEXT:
- Average improvement: +0.47 points
- Generation: 0

SYNTHESIS ANALYSIS (based on actual conversation performance):
{synthesis_analysis}

TASK: Create an improved system prompt that:
1. MUST start with "You are..." (system prompt format)
2. Addresses the weaknesses identified in the synthesis analysis
3. Builds upon the strengths identified in the synthesis analysis
4. Incorporates the specific recommendations from the conversation analysis
5. Improves overall effectiveness for social skills coaching
6. Keep it concise but effective (aim for 1-3 sentences, maximum 200 words)

Focus on making meaningful improvements based on the actual conversation performance analysis, not just numerical scores.

CRITICAL: Your response must be ONLY the system prompt text starting with "You are..." (exactly these words). Do not include any reasoning, analysis, explanations, or other text. Just the prompt.

Example format: "You are a helpful social skills coach who..."
"""

    headers = {
        "Authorization": f"Bearer {Config.DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": Config.DEEPSEEK_REASONER_MODEL,
        "messages": [{"role": "user", "content": mutation_prompt}],
        "temperature": 0.6,
        "max_tokens": 1200
    }
    
    print("🔄 Making API call to generate mutation...")
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.lkeap.cloud.tencent.com/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=60
            ) as response:
                print(f"📡 API Response Status: {response.status}")
                
                if response.status == 200:
                    result = await response.json()
                    if 'choices' in result and len(result['choices']) > 0:
                        message = result['choices'][0]['message']
                        mutated_prompt_text = message.get('content', '').strip()
                        
                        print(f"✅ Generated mutation: {mutated_prompt_text}")
                        print(f"📊 Length: {len(mutated_prompt_text)} characters")
                        
                        # Test validation
                        first_part = mutated_prompt_text[:50].lower()
                        has_you_are = "you are" in first_part
                        has_proper_length = len(mutated_prompt_text) >= 20
                        
                        print(f"\n🔍 Validation Results:")
                        print(f"   - Contains 'you are': {has_you_are}")
                        print(f"   - Length >= 20: {has_proper_length} (actual: {len(mutated_prompt_text)})")
                        print(f"   - First 50 chars: '{first_part}'")
                        
                        if has_you_are and has_proper_length:
                            print(f"   ✅ VALIDATION PASSED")
                            return True
                        else:
                            print(f"   ❌ VALIDATION FAILED")
                            return False
                    else:
                        print(f"❌ No choices in response: {result}")
                        return False
                else:
                    print(f"❌ API Error: {response.status}")
                    error_text = await response.text()
                    print(f"   Error: {error_text}")
                    return False
                    
    except Exception as e:
        print(f"❌ Exception during API call: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    success = await test_simple_mutation()
    
    if success:
        print("\n🎉 Mutation test completed successfully!")
    else:
        print("\n❌ Mutation test failed!")

if __name__ == "__main__":
    asyncio.run(main())

