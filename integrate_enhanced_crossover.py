#!/usr/bin/env python3

# Read the current file
with open('prompt_optimizer.py', 'r') as f:
    content = f.read()

# Add import at the top
if 'from corrected_enhanced_crossover import CorrectedEnhancedCrossover' not in content:
    content = 'from corrected_enhanced_crossover import CorrectedEnhancedCrossover\n' + content

# Find and replace the _crossover_prompts method
import re

old_method = r'def _crossover_prompts\(self, parent1: OptimizedPrompt, parent2: OptimizedPrompt\) -> OptimizedPrompt:.*?(?=    def _mutate_prompt)'

new_method = '''def _crossover_prompts(self, parent1: OptimizedPrompt, parent2: OptimizedPrompt) -> OptimizedPrompt:
        """Create a child prompt using enhanced crossover with performance+diversity balance"""
        
        # Initialize enhanced crossover
        enhanced_crossover = CorrectedEnhancedCrossover()
        
        # Analyze parent performance profiles
        parent1_profile = enhanced_crossover.analyze_parent_performance(
            parent1.prompt_text, 
            parent1.performance_metrics or {}, 
            parent1.generation
        )
        
        parent2_profile = enhanced_crossover.analyze_parent_performance(
            parent2.prompt_text, 
            parent2.performance_metrics or {}, 
            parent2.generation
        )
        
        # Get existing prompts for diversity analysis
        existing_prompts = [p.prompt_text for p in self.all_prompts[-10:]]
        
        # Create enhanced crossover prompt
        enhanced_prompt = enhanced_crossover.create_performance_diversity_crossover_prompt(
            parent1_profile, parent2_profile, existing_prompts, diversity_weight=0.7
        )
        
        try:
            from config import Config
            
            print(f"   🚀 Enhanced crossover: {parent1.name} + {parent2.name}")
            response = requests.post(
                "https://api.deepseek.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {Config.DEEPSEEK_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "deepseek-chat",
                    "messages": [{"role": "user", "content": enhanced_prompt}],
                    "temperature": 0.9,
                    "max_tokens": 200
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if 'choices' in result and len(result['choices']) > 0:
                    child_prompt_text = result['choices'][0]['message']['content'].strip()
                    print(f"   ✅ Enhanced: {child_prompt_text[:80]}...")
                    
                    # Validate length
                    max_parent_length = max(len(parent1.prompt_text), len(parent2.prompt_text))
                    if len(child_prompt_text) > max_parent_length * 3.0:
                        child_prompt_text = f"{parent1.prompt_text} {parent2.prompt_text}"
                else:
                    child_prompt_text = f"{parent1.prompt_text} {parent2.prompt_text}"
            else:
                child_prompt_text = f"{parent1.prompt_text} {parent2.prompt_text}"
                
        except Exception as e:
            print(f"⚠️  Enhanced crossover failed: {e}")
            child_prompt_text = f"{parent1.prompt_text} {parent2.prompt_text}"
        
        return OptimizedPrompt(
            id=str(uuid.uuid4()),
            name=f"Enhanced Child of {parent1.name} + {parent2.name}",
            prompt_text=child_prompt_text,
            components=[],
            generation=parent1.generation + 1,
            performance_metrics={},
            pareto_rank=0,
            created_at=datetime.now(),
            last_tested=None
        )

'''

# Replace the method
new_content = re.sub(old_method, new_method, content, flags=re.DOTALL)

# Write the new file
with open('prompt_optimizer.py', 'w') as f:
    f.write(new_content)

print("✅ Enhanced crossover integrated successfully!")
