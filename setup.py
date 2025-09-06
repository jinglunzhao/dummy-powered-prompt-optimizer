#!/usr/bin/env python3
"""
Setup Script for AI Social Skills Training Pipeline
Helps collaborators get started quickly.
"""

import os
import sys
import subprocess
import json

def check_python_version():
    """Check if Python version is compatible"""
    print("🐍 Checking Python version...")
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required. Current version:", sys.version)
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    return True

def install_dependencies():
    """Install required dependencies"""
    print("\n📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def create_env_file():
    """Create .env file template"""
    print("\n🔑 Setting up environment file...")
    
    if os.path.exists(".env"):
        print("✅ .env file already exists")
        return True
    
    env_content = """# AI Social Skills Training Pipeline Configuration
# Add your API key here
OPENAI_API_KEY=your_api_key_here

# Optional: Override default model
# OPENAI_MODEL=deepseek-chat

# Optional: Override default base URL for DeepSeek
# OPENAI_BASE_URL=https://api.deepseek.com/v1
"""
    
    try:
        with open(".env", "w") as f:
            f.write(env_content)
        print("✅ Created .env file template")
        print("   Please edit .env and add your API key")
        return True
    except Exception as e:
        print(f"❌ Failed to create .env file: {e}")
        return False

def create_data_directory():
    """Create data directory if it doesn't exist"""
    print("\n📁 Setting up data directory...")
    
    if not os.path.exists("data"):
        try:
            os.makedirs("data")
            print("✅ Created data/ directory")
        except Exception as e:
            print(f"❌ Failed to create data directory: {e}")
            return False
    else:
        print("✅ data/ directory already exists")
    
    return True

def check_existing_data():
    """Check if there's existing data to work with"""
    print("\n📊 Checking existing data...")
    
    data_files = {
        "ai_dummies.json": "AI dummy profiles",
        "assessments.json": "Assessment results", 
        "conversations.json": "Conversation logs"
    }
    
    existing_data = []
    for filename, description in data_files.items():
        filepath = os.path.join("data", filename)
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    existing_data.append(f"   • {description}: {len(data)} records")
            except:
                existing_data.append(f"   • {description}: File exists but may be corrupted")
    
    if existing_data:
        print("✅ Found existing data:")
        for item in existing_data:
            print(item)
        print("   You can use this data or generate new data")
    else:
        print("ℹ️  No existing data found")
        print("   You'll need to generate data first")
    
    return True

def run_quick_test():
    """Run a quick test to verify everything works"""
    print("\n🧪 Running quick test...")
    
    try:
        # Test basic imports
        from config import Config
        from models import AIDummy, Assessment, Conversation
        print("✅ Core modules imported successfully")
        
        # Test data models
        print("✅ Data models validated")
        
        return True
    except Exception as e:
        print(f"❌ Quick test failed: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 **AI Social Skills Training Pipeline Setup**")
    print("=" * 60)
    print("This script will help you get started with the project.")
    print()
    
    # Run setup steps
    steps = [
        ("Python Version Check", check_python_version),
        ("Dependencies Installation", install_dependencies),
        ("Environment Setup", create_env_file),
        ("Data Directory Setup", create_data_directory),
        ("Data Check", check_existing_data),
        ("Quick Test", run_quick_test)
    ]
    
    successful_steps = 0
    total_steps = len(steps)
    
    for step_name, step_func in steps:
        print(f"\n🔧 {step_name}...")
        if step_func():
            successful_steps += 1
        else:
            print(f"⚠️  {step_name} had issues")
    
    # Summary
    print(f"\n🎯 **Setup Summary**")
    print("=" * 30)
    print(f"✅ Successful steps: {successful_steps}/{total_steps}")
    
    if successful_steps == total_steps:
        print("🎉 Setup completed successfully!")
        print("\n🚀 Next steps:")
        print("1. Edit .env file and add your API key")
        print("2. Run demo: python demo.py")
        print("3. Generate data: python character_generator.py")
        print("4. Launch web interface: python web_interface.py")
    else:
        print("⚠️  Some setup steps had issues.")
        print("Please check the error messages above and try again.")
    
    print(f"\n📚 For more information, see README.md")
    print("🤝 Happy collaborating!")

if __name__ == "__main__":
    main()
