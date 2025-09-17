#!/usr/bin/env python3
"""
Quick Analysis Script for GEPA Reflections and Synthesis
Analyzes conversation reflections and synthesis analyses from the first 4 generations
"""

import json
import os
import glob
from datetime import datetime
from collections import defaultdict, Counter
import re

def load_synthesis_analyses():
    """Load all synthesis analysis files"""
    synthesis_files = glob.glob("data/synthesis_analysis_*.json")
    synthesis_data = []
    
    for file_path in synthesis_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                synthesis_data.append(data)
        except Exception as e:
            print(f"⚠️  Error loading {file_path}: {e}")
    
    return synthesis_data

def load_conversation_reflections():
    """Load conversation reflections from conversation files"""
    conversation_files = glob.glob("data/conversations/dummy_*.json")
    all_reflections = []
    
    for file_path in conversation_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                # Extract conversations with reflections
                for conversation in data.get('conversations', []):
                    if 'reflection' in conversation and conversation['reflection']:
                        all_reflections.append({
                            'dummy_name': data.get('dummy_name', 'Unknown'),
                            'prompt_id': conversation.get('prompt_id', 'Unknown'),
                            'prompt_name': conversation.get('prompt_name', 'Unknown'),
                            'generation': conversation.get('generation', 'Unknown'),
                            'improvement': conversation.get('improvement', 0),
                            'reflection': conversation['reflection'],
                            'timestamp': conversation.get('timestamp', 'Unknown')
                        })
        except Exception as e:
            print(f"⚠️  Error loading {file_path}: {e}")
    
    return all_reflections

def analyze_reflection_patterns(reflections):
    """Analyze patterns in conversation reflections"""
    print("🔍 CONVERSATION REFLECTION ANALYSIS")
    print("=" * 50)
    
    # Basic statistics
    print(f"📊 Total reflections: {len(reflections)}")
    
    # Group by generation
    by_generation = defaultdict(list)
    for ref in reflections:
        by_generation[ref['generation']].append(ref)
    
    print(f"\n📈 Reflections by generation:")
    for gen in sorted(by_generation.keys()):
        print(f"   G{gen}: {len(by_generation[gen])} reflections")
    
    # Group by prompt
    by_prompt = defaultdict(list)
    for ref in reflections:
        by_prompt[ref['prompt_name']].append(ref)
    
    print(f"\n🎯 Reflections by prompt:")
    for prompt_name in sorted(by_prompt.keys()):
        print(f"   {prompt_name}: {len(by_prompt[prompt_name])} reflections")
    
    # Analyze reflection content
    print(f"\n📝 Reflection Content Analysis:")
    
    # Common words in reflections
    all_reflection_text = " ".join([ref['reflection'] for ref in reflections])
    words = re.findall(r'\b\w+\b', all_reflection_text.lower())
    word_freq = Counter(words)
    
    print(f"   Most common words in reflections:")
    for word, count in word_freq.most_common(10):
        if len(word) > 3:  # Skip short words
            print(f"     '{word}': {count} times")
    
    # Reflection length analysis
    lengths = [len(ref['reflection']) for ref in reflections]
    print(f"\n📏 Reflection length statistics:")
    print(f"   Average length: {sum(lengths) / len(lengths):.1f} characters")
    print(f"   Shortest: {min(lengths)} characters")
    print(f"   Longest: {max(lengths)} characters")
    
    # Performance correlation
    print(f"\n📊 Performance vs Reflection Quality:")
    high_perf = [ref for ref in reflections if ref['improvement'] > 0.3]
    low_perf = [ref for ref in reflections if ref['improvement'] <= 0.3]
    
    if high_perf and low_perf:
        high_avg_len = sum(len(ref['reflection']) for ref in high_perf) / len(high_perf)
        low_avg_len = sum(len(ref['reflection']) for ref in low_perf) / len(low_perf)
        print(f"   High performance (>{0.3}): {high_avg_len:.1f} avg chars")
        print(f"   Low performance (<={0.3}): {low_avg_len:.1f} avg chars")

def analyze_synthesis_patterns(synthesis_data):
    """Analyze patterns in synthesis analyses"""
    print("\n🧠 SYNTHESIS ANALYSIS ANALYSIS")
    print("=" * 50)
    
    print(f"📊 Total synthesis analyses: {len(synthesis_data)}")
    
    # Group by generation
    by_generation = defaultdict(list)
    for synth in synthesis_data:
        by_generation[synth.get('generation', 'Unknown')].append(synth)
    
    print(f"\n📈 Synthesis analyses by generation:")
    for gen in sorted(by_generation.keys()):
        print(f"   G{gen}: {len(by_generation[gen])} analyses")
    
    # Analyze synthesis content
    print(f"\n📝 Synthesis Content Analysis:")
    
    # Common words in synthesis
    all_synthesis_text = " ".join([synth.get('synthesis_analysis', '') for synth in synthesis_data])
    words = re.findall(r'\b\w+\b', all_synthesis_text.lower())
    word_freq = Counter(words)
    
    print(f"   Most common words in synthesis:")
    for word, count in word_freq.most_common(10):
        if len(word) > 3:  # Skip short words
            print(f"     '{word}': {count} times")
    
    # Synthesis length analysis
    lengths = [len(synth.get('synthesis_analysis', '')) for synth in synthesis_data]
    print(f"\n📏 Synthesis length statistics:")
    print(f"   Average length: {sum(lengths) / len(lengths):.1f} characters")
    print(f"   Shortest: {min(lengths)} characters")
    print(f"   Longest: {max(lengths)} characters")
    
    # Conversation count analysis
    conv_counts = [synth.get('conversation_count', 0) for synth in synthesis_data]
    print(f"\n💬 Conversation count statistics:")
    print(f"   Average conversations per synthesis: {sum(conv_counts) / len(conv_counts):.1f}")
    print(f"   Most conversations: {max(conv_counts)}")
    print(f"   Least conversations: {min(conv_counts)}")

def analyze_evolution_patterns(reflections, synthesis_data):
    """Analyze how reflections and synthesis evolve across generations"""
    print("\n🔄 EVOLUTION PATTERN ANALYSIS")
    print("=" * 50)
    
    # Group reflections by generation
    by_gen_reflections = defaultdict(list)
    for ref in reflections:
        by_gen_reflections[ref['generation']].append(ref)
    
    # Group synthesis by generation
    by_gen_synthesis = defaultdict(list)
    for synth in synthesis_data:
        by_gen_synthesis[synth.get('generation', 'Unknown')].append(synth)
    
    print("📈 Evolution across generations:")
    for gen in sorted(set(list(by_gen_reflections.keys()) + list(by_gen_synthesis.keys()))):
        ref_count = len(by_gen_reflections.get(gen, []))
        synth_count = len(by_gen_synthesis.get(gen, []))
        
        if ref_count > 0:
            avg_improvement = sum(ref['improvement'] for ref in by_gen_reflections[gen]) / ref_count
            avg_reflection_len = sum(len(ref['reflection']) for ref in by_gen_reflections[gen]) / ref_count
        else:
            avg_improvement = 0
            avg_reflection_len = 0
        
        if synth_count > 0:
            avg_synthesis_len = sum(len(synth.get('synthesis_analysis', '')) for synth in by_gen_synthesis[gen]) / synth_count
        else:
            avg_synthesis_len = 0
        
        print(f"   G{gen}: {ref_count} reflections, {synth_count} synthesis")
        print(f"     Avg improvement: {avg_improvement:.3f}")
        print(f"     Avg reflection length: {avg_reflection_len:.1f} chars")
        print(f"     Avg synthesis length: {avg_synthesis_len:.1f} chars")

def show_sample_reflections(reflections, n=3):
    """Show sample reflections from different generations"""
    print("\n📋 SAMPLE REFLECTIONS")
    print("=" * 50)
    
    # Group by generation and show samples
    by_gen = defaultdict(list)
    for ref in reflections:
        by_gen[ref['generation']].append(ref)
    
    for gen in sorted(by_gen.keys()):
        print(f"\n🔸 Generation {gen} samples:")
        samples = by_gen[gen][:n]
        for i, ref in enumerate(samples, 1):
            print(f"\n   Sample {i} ({ref['dummy_name']}, improvement: {ref['improvement']:.3f}):")
            print(f"   {ref['reflection'][:200]}{'...' if len(ref['reflection']) > 200 else ''}")

def show_sample_synthesis(synthesis_data, n=2):
    """Show sample synthesis analyses"""
    print("\n🧠 SAMPLE SYNTHESIS ANALYSES")
    print("=" * 50)
    
    # Group by generation and show samples
    by_gen = defaultdict(list)
    for synth in synthesis_data:
        by_gen[synth.get('generation', 'Unknown')].append(synth)
    
    for gen in sorted(by_gen.keys()):
        print(f"\n🔸 Generation {gen} samples:")
        samples = by_gen[gen][:n]
        for i, synth in enumerate(samples, 1):
            print(f"\n   Sample {i} ({synth.get('prompt_name', 'Unknown')}):")
            synthesis_text = synth.get('synthesis_analysis', '')
            print(f"   {synthesis_text[:300]}{'...' if len(synthesis_text) > 300 else ''}")

def main():
    """Main analysis function"""
    print("🔍 GEPA REFLECTIONS & SYNTHESIS ANALYSIS")
    print("=" * 60)
    print(f"Analysis started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Load data
    print("📂 Loading data...")
    synthesis_data = load_synthesis_analyses()
    reflections = load_conversation_reflections()
    
    print(f"✅ Loaded {len(synthesis_data)} synthesis analyses")
    print(f"✅ Loaded {len(reflections)} conversation reflections")
    print()
    
    # Run analyses
    analyze_reflection_patterns(reflections)
    analyze_synthesis_patterns(synthesis_data)
    analyze_evolution_patterns(reflections, synthesis_data)
    
    # Show samples
    show_sample_reflections(reflections)
    show_sample_synthesis(synthesis_data)
    
    print("\n✅ Analysis complete!")
    print(f"Analysis finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
