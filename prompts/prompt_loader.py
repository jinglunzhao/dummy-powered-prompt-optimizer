"""
Prompt Loader Utility
Loads prompts from YAML files for clean code separation
"""

import os
import yaml
from typing import Dict, Any

class PromptLoader:
    def __init__(self, prompts_dir: str = "prompts"):
        self.prompts_dir = prompts_dir
        self._prompts_cache: Dict[str, Dict[str, Any]] = {}
    
    def load_prompts(self, filename: str) -> Dict[str, Any]:
        """Load prompts from a YAML file"""
        if filename in self._prompts_cache:
            return self._prompts_cache[filename]
        
        filepath = os.path.join(self.prompts_dir, filename)
        
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Prompt file not found: {filepath}")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            prompts = yaml.safe_load(f)
        
        self._prompts_cache[filename] = prompts
        return prompts
    
    def get_prompt(self, filename: str, prompt_name: str, **kwargs) -> str:
        """Get a specific prompt and format it with variables"""
        prompts = self.load_prompts(filename)
        
        if prompt_name not in prompts:
            raise KeyError(f"Prompt '{prompt_name}' not found in {filename}")
        
        prompt_template = prompts[prompt_name]
        
        # Format with provided variables
        if kwargs:
            return prompt_template.format(**kwargs)
        
        return prompt_template

# Global instance
prompt_loader = PromptLoader()

