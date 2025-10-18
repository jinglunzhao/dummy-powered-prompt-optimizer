#!/usr/bin/env python3
"""
Prompt Tracking Tool
Analyzes prompt usage across the codebase and detects duplication issues.
"""

import os
import re
import yaml
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Set

class PromptTracker:
    """Track and analyze prompt usage across the codebase"""
    
    def __init__(self, root_dir: str = "."):
        self.root_dir = Path(root_dir)
        self.prompts_dir = self.root_dir / "prompts"
        self.yaml_prompts: Dict[str, Dict[str, str]] = {}
        self.usage_map: Dict[str, List[str]] = defaultdict(list)
        self.hardcoded_prompts: List[tuple] = []
        
    def load_yaml_prompts(self):
        """Load all prompts from YAML files"""
        print("📂 Loading YAML prompts...")
        
        for yaml_file in self.prompts_dir.glob("*.yaml"):
            with open(yaml_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                if data:
                    self.yaml_prompts[yaml_file.name] = data
                    print(f"   ✓ {yaml_file.name}: {len(data)} prompts")
    
    def find_prompt_usage(self):
        """Find where each prompt is used"""
        print("\n🔍 Analyzing prompt usage...")
        
        # Search for get_prompt calls
        py_files = list(self.root_dir.glob("**/*.py"))
        
        for py_file in py_files:
            # Skip virtual environments and hidden directories
            if '.venv' in str(py_file) or '__pycache__' in str(py_file):
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Find get_prompt calls (handles multiline)
                # Pattern: get_prompt('filename.yaml', 'prompt_key', ...)
                # Remove newlines for easier matching
                single_line = content.replace('\n', ' ')
                pattern = r"get_prompt\(\s*['\"]([^'\"]+\.yaml)['\"],\s*['\"]([^'\"]+)['\"]"
                matches = re.findall(pattern, single_line)
                
                for yaml_file, prompt_key in matches:
                    key = f"{yaml_file}:{prompt_key}"
                    relative_path = py_file.relative_to(self.root_dir)
                    self.usage_map[key].append(str(relative_path))
                    
            except Exception as e:
                print(f"   ⚠️  Error reading {py_file}: {e}")
    
    def find_hardcoded_prompts(self):
        """Find hardcoded prompts that should be in YAML"""
        print("\n🔎 Searching for hardcoded prompts...")
        
        patterns = [
            r'"You are a [^"]{20,}"',  # Double quotes
            r"'You are a [^']{20,}'",  # Single quotes
            r'"""You are a [^"]{20,}"""',  # Triple double quotes
            r"'''You are a [^']{20,}'''",  # Triple single quotes
        ]
        
        py_files = list(self.root_dir.glob("**/*.py"))
        
        for py_file in py_files:
            if '.venv' in str(py_file) or '__pycache__' in str(py_file):
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    
                for line_num, line in enumerate(lines, 1):
                    for pattern in patterns:
                        matches = re.findall(pattern, line)
                        if matches:
                            relative_path = py_file.relative_to(self.root_dir)
                            self.hardcoded_prompts.append((
                                str(relative_path),
                                line_num,
                                matches[0][:80] + "..." if len(matches[0]) > 80 else matches[0]
                            ))
                            
            except Exception as e:
                pass  # Skip errors silently
    
    def print_report(self):
        """Print comprehensive prompt tracking report"""
        print("\n" + "="*70)
        print("📊 PROMPT REFERENCE REPORT")
        print("="*70)
        
        # 1. YAML Prompts Inventory
        print("\n📦 YAML PROMPTS INVENTORY")
        print("-" * 70)
        total_prompts = 0
        for yaml_file, prompts in sorted(self.yaml_prompts.items()):
            print(f"\n{yaml_file} ({len(prompts)} prompts):")
            for key in sorted(prompts.keys()):
                print(f"   • {key}")
                total_prompts += 1
        print(f"\nTotal YAML Prompts: {total_prompts}")
        
        # 2. Usage Map
        print("\n\n🗺️  PROMPT USAGE MAP")
        print("-" * 70)
        
        used_prompts = 0
        unused_prompts = []
        
        for yaml_file, prompts in sorted(self.yaml_prompts.items()):
            print(f"\n{yaml_file}:")
            for key in sorted(prompts.keys()):
                lookup_key = f"{yaml_file}:{key}"
                usages = self.usage_map.get(lookup_key, [])
                
                if usages:
                    used_prompts += 1
                    print(f"   ✓ {key}")
                    for usage in usages:
                        print(f"      └─> {usage}")
                else:
                    unused_prompts.append(f"{yaml_file}:{key}")
                    print(f"   ⚠️  {key} - NOT USED")
        
        print(f"\nUsage Statistics:")
        print(f"   • Used: {used_prompts}/{total_prompts}")
        print(f"   • Unused: {len(unused_prompts)}/{total_prompts}")
        
        # 3. Hardcoded Prompts
        print("\n\n⚠️  HARDCODED PROMPTS FOUND")
        print("-" * 70)
        
        if self.hardcoded_prompts:
            print(f"Found {len(self.hardcoded_prompts)} potential hardcoded prompts:\n")
            for file_path, line_num, prompt_text in self.hardcoded_prompts:
                print(f"📍 {file_path}:{line_num}")
                print(f"   {prompt_text}\n")
        else:
            print("✅ No hardcoded prompts found!")
        
        # 4. Duplication Check
        print("\n\n🔍 DUPLICATION CHECK")
        print("-" * 70)
        
        # Check if Config.SYSTEM_PROMPT exists
        config_file = self.root_dir / "config.py"
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                content = f.read()
                if 'SYSTEM_PROMPT = ' in content and 'prompt_loader' not in content:
                    print("⚠️  DUPLICATION FOUND:")
                    print("   config.py:SYSTEM_PROMPT is hardcoded")
                    print("   Duplicates: default_prompts.yaml:default_system_prompt")
                    print("   Recommendation: Use prompt_loader instead")
                else:
                    print("✅ Config.SYSTEM_PROMPT uses prompt_loader or not found")
        
        # 5. Recommendations
        print("\n\n💡 RECOMMENDATIONS")
        print("-" * 70)
        
        if unused_prompts:
            print(f"• Remove or document {len(unused_prompts)} unused prompts")
        
        if self.hardcoded_prompts:
            print(f"• Migrate {len(self.hardcoded_prompts)} hardcoded prompts to YAML files")
        
        if not unused_prompts and not self.hardcoded_prompts:
            print("✅ Prompt management looks good!")
        
        print("\n" + "="*70)

def main():
    """Run prompt tracking analysis"""
    tracker = PromptTracker()
    tracker.load_yaml_prompts()
    tracker.find_prompt_usage()
    tracker.find_hardcoded_prompts()
    tracker.print_report()
    
    print("\n📖 For detailed information, see: PROMPT_REFERENCE_GUIDE.md")

if __name__ == "__main__":
    main()

