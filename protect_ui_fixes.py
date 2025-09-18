#!/usr/bin/env python3
"""
UI Fixes Protection Script
Automatically restores the three critical UI fixes if they get reverted by Cursor IDE auto-save
"""

import os
import time
import subprocess
import json
from datetime import datetime

# The three critical UI fixes that must be protected
UI_FIXES = {
    "templates/optimization.html": {
        "description": "Chart number display fix",
        "critical_lines": [
            "const bestPrompt = genPrompts.reduce((best, current) => {",
            "const bestScore = (best.performance_metrics?.avg_improvement || 0);",
            "const currentScore = (current.performance_metrics?.avg_improvement || 0);",
            "return currentScore > bestScore ? current : best;"
        ]
    },
    "templates/prompt_detail.html": {
        "description": "Separated conversation/reflections and synthesis analysis display",
        "critical_lines": [
            "Reflection Details",
            "loadSynthesisAnalysis(promptId)",
            "displaySynthesisAnalysis(synthesisData)",
            "synthesisText",
            "if (!synthesisText) {"
        ]
    }
}

def check_file_integrity(file_path, critical_lines):
    """Check if a file contains all critical lines"""
    if not os.path.exists(file_path):
        return False
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            return all(line in content for line in critical_lines)
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return False

def restore_from_git(file_path):
    """Restore file from Git if it's been corrupted"""
    try:
        result = subprocess.run(['git', 'checkout', '--', file_path], 
                              capture_output=True, text=True, cwd=os.getcwd())
        if result.returncode == 0:
            print(f"✅ Restored {file_path} from Git")
            return True
        else:
            print(f"❌ Failed to restore {file_path}: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error restoring {file_path}: {e}")
        return False

def monitor_ui_fixes():
    """Monitor and protect UI fixes"""
    print("🛡️  UI Fixes Protection Script Started")
    print(f"📅 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🔍 Monitoring files for reversion...")
    
    while True:
        try:
            for file_path, fix_info in UI_FIXES.items():
                if not check_file_integrity(file_path, fix_info["critical_lines"]):
                    print(f"⚠️  DETECTED REVERSION: {file_path} - {fix_info['description']}")
                    print(f"🔄 Attempting to restore from Git...")
                    
                    if restore_from_git(file_path):
                        print(f"✅ Successfully restored {file_path}")
                    else:
                        print(f"❌ Failed to restore {file_path} - manual intervention required")
            
            # Check every 30 seconds
            time.sleep(30)
            
        except KeyboardInterrupt:
            print("\n🛑 Protection script stopped by user")
            break
        except Exception as e:
            print(f"❌ Error in monitoring loop: {e}")
            time.sleep(60)  # Wait longer on error

if __name__ == "__main__":
    monitor_ui_fixes()
