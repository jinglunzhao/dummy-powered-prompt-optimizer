#!/usr/bin/env python3
"""
Start Conversation Journey Visualizer
====================================

Simple script to start the experiment API server for the conversation journey visualizer.
"""

import subprocess
import sys
import os

def main():
    print("🎯 Conversation Journey Visualizer")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists('data/experiments'):
        print("❌ Error: data/experiments directory not found!")
        print("   Please run this script from the edu_chatbot root directory.")
        sys.exit(1)
    
    # Check if experiment files exist
    experiment_files = [f for f in os.listdir('data/experiments') if f.startswith('continuous_conversation_exp_')]
    if not experiment_files:
        print("❌ Error: No continuous conversation experiment files found!")
        print("   Please run some experiments first using conversation_length_experiment_v2.py")
        sys.exit(1)
    
    print(f"✅ Found {len(experiment_files)} experiment files")
    print("🚀 Starting API server...")
    print()
    print("📊 The visualizer will be available at: http://localhost:5001")
    print("🛑 Press Ctrl+C to stop the server")
    print("=" * 50)
    
    try:
        # Start the Flask server
        subprocess.run([sys.executable, 'experiment_api_server.py'])
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
