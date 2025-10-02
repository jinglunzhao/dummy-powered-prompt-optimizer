#!/usr/bin/env python3
"""
Test script for the optimized conversation length experiment flow
"""

import asyncio
import json
import os
from models import AIDummy
from conversation_length_experiment_with_evolution import ConversationLengthExperimentWithEvolution

async def test_optimized_flow():
    """Test the optimized conversation flow with parallel milestone processing"""
    
    print("🧪 Testing Optimized Conversation Length Experiment Flow")
    print("=" * 60)
    
    # Load test dummies
    dummies_file = "data/ai_dummies.json"
    if not os.path.exists(dummies_file):
        print("❌ No dummies file found. Please run dummy generation first.")
        return
    
    with open(dummies_file, 'r', encoding='utf-8') as f:
        all_dummies = json.load(f)
    
    # Use first 2 dummies for quick test
    selected_dummies = all_dummies[:2]
    dummies = [AIDummy(**dummy_data) for dummy_data in selected_dummies]
    
    print(f"✅ Loaded {len(dummies)} dummies for testing")
    print(f"   • {dummies[0].name}")
    print(f"   • {dummies[1].name}")
    print()
    
    # Test configuration
    max_rounds = 10
    milestones = [3, 6, 9]  # Fewer milestones for quick test
    
    print(f"📊 Test Configuration:")
    print(f"   • Max rounds: {max_rounds}")
    print(f"   • Milestones: {milestones}")
    print(f"   • Expected evolution stages: {len(milestones) + 1} (milestones + final)")
    print()
    
    # Run experiment
    experiment = ConversationLengthExperimentWithEvolution()
    
    start_time = asyncio.get_event_loop().time()
    
    await experiment.run_experiment(
        dummies=dummies,
        max_rounds=max_rounds,
        milestones=milestones,
        base_prompt="You are a helpful peer mentor for college students. Be supportive and provide practical advice.",
        save_details=True,
        enable_assessments=False  # Disable assessments to avoid API timeout issues
    )
    
    end_time = asyncio.get_event_loop().time()
    duration = end_time - start_time
    
    print(f"\n⏱️  Test completed in {duration:.1f} seconds")
    print(f"   • Expected time with old flow: ~{len(milestones) * 2 * 60:.0f} seconds")
    print(f"   • Actual time with optimized flow: {duration:.1f} seconds")
    print(f"   • Speed improvement: ~{len(milestones) * 2 * 60 / duration:.1f}x faster")

if __name__ == "__main__":
    asyncio.run(test_optimized_flow())
