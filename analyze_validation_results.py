#!/usr/bin/env python3
"""
Comprehensive analysis of validation test results to understand prompt evolution
and identify why performance isn't improving overall.
"""

import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from collections import defaultdict, Counter
import re
from typing import Dict, List, Any, Tuple
import warnings
warnings.filterwarnings('ignore')

class ValidationAnalyzer:
    def __init__(self, results_file: str):
        """Initialize analyzer with validation results"""
        self.results_file = results_file
        self.data = None
        self.load_data()
        
    def load_data(self):
        """Load validation results data"""
        print("📊 Loading validation results...")
        with open(self.results_file, 'r', encoding='utf-8') as f:
            self.data = json.load(f)
        print(f"✅ Loaded data with {len(self.data['optimization']['all_prompts'])} total prompts")
        
    def analyze_generation_progression(self):
        """Analyze how performance changes across generations"""
        print("\n" + "="*60)
        print("📈 GENERATION PROGRESSION ANALYSIS")
        print("="*60)
        
        # Get best prompt per generation
        best_per_gen = self.data['optimization']['best_per_generation']
        
        print(f"\n📊 Found {len(best_per_gen)} generations:")
        
        for i, prompt in enumerate(best_per_gen):
            metrics = prompt.get('performance_metrics', {})
            avg_improvement = metrics.get('avg_improvement', 0)
            test_count = metrics.get('test_count', 0)
            
            print(f"  Gen {i}: {prompt['name']}")
            print(f"    Avg Improvement: {avg_improvement:.4f}")
            print(f"    Test Count: {test_count}")
            print(f"    Prompt: \"{prompt['prompt_text'][:100]}...\"")
            print()
            
        # Calculate progression metrics
        improvements = [p.get('performance_metrics', {}).get('avg_improvement', 0) for p in best_per_gen]
        
        print(f"📈 Performance Progression:")
        print(f"  First Generation: {improvements[0]:.4f}")
        print(f"  Last Generation:  {improvements[-1]:.4f}")
        print(f"  Total Change:     {improvements[-1] - improvements[0]:.4f}")
        print(f"  Best Generation:  Gen {np.argmax(improvements)} ({max(improvements):.4f})")
        
        return best_per_gen, improvements
    
    def analyze_prompt_diversity(self):
        """Analyze diversity of prompts across generations"""
        print("\n" + "="*60)
        print("🎭 PROMPT DIVERSITY ANALYSIS")
        print("="*60)
        
        all_prompts = self.data['optimization']['all_prompts']
        
        # Group by generation
        gen_prompts = defaultdict(list)
        for prompt in all_prompts:
            gen_prompts[prompt['generation']].append(prompt)
            
        print(f"\n📊 Prompts per generation:")
        for gen in sorted(gen_prompts.keys()):
            prompts = gen_prompts[gen]
            print(f"  Gen {gen}: {len(prompts)} prompts")
            
            # Analyze prompt text diversity
            prompt_texts = [p['prompt_text'] for p in prompts]
            unique_texts = set(prompt_texts)
            print(f"    Unique texts: {len(unique_texts)}/{len(prompt_texts)}")
            
            # Check for identical prompts
            if len(unique_texts) < len(prompt_texts):
                duplicates = len(prompt_texts) - len(unique_texts)
                print(f"    ⚠️  {duplicates} duplicate prompts found!")
                
                # Show duplicate examples
                text_counts = Counter(prompt_texts)
                for text, count in text_counts.most_common(3):
                    if count > 1:
                        print(f"      \"{text[:50]}...\" appears {count} times")
            
            print()
            
        return gen_prompts
    
    def analyze_llm_evolution_effectiveness(self):
        """Analyze how effective LLM-based evolution is"""
        print("\n" + "="*60)
        print("🤖 LLM EVOLUTION EFFECTIVENESS")
        print("="*60)
        
        all_prompts = self.data['optimization']['all_prompts']
        
        # Categorize prompts by type
        mutation_prompts = [p for p in all_prompts if 'Mutation' in p['name']]
        crossover_prompts = [p for p in all_prompts if 'Child' in p['name']]
        initial_prompts = [p for p in all_prompts if p['generation'] == 0]
        
        print(f"📊 Prompt Types:")
        print(f"  Initial prompts: {len(initial_prompts)}")
        print(f"  Mutation prompts: {len(mutation_prompts)}")
        print(f"  Crossover prompts: {len(crossover_prompts)}")
        
        # Analyze performance by type
        def get_avg_improvement(prompts):
            improvements = [p.get('performance_metrics', {}).get('avg_improvement', 0) for p in prompts]
            return np.mean(improvements) if improvements else 0
        
        print(f"\n📈 Average Performance by Type:")
        print(f"  Initial: {get_avg_improvement(initial_prompts):.4f}")
        print(f"  Mutations: {get_avg_improvement(mutation_prompts):.4f}")
        print(f"  Crossovers: {get_avg_improvement(crossover_prompts):.4f}")
        
        # Analyze fallback usage
        fallback_mutations = [p for p in mutation_prompts if p['prompt_text'] == p.get('parent_prompt_text', '')]
        fallback_crossovers = [p for p in crossover_prompts if len(p['prompt_text'].split()) < 10]  # Heuristic for simple combination
        
        print(f"\n⚠️  Fallback Analysis:")
        print(f"  Mutation fallbacks: {len(fallback_mutations)}/{len(mutation_prompts)} ({len(fallback_mutations)/len(mutation_prompts)*100:.1f}%)")
        print(f"  Crossover fallbacks: {len(fallback_crossovers)}/{len(crossover_prompts)} ({len(fallback_crossovers)/len(crossover_prompts)*100:.1f}%)")
        
        return mutation_prompts, crossover_prompts, initial_prompts
    
    def analyze_criteria_performance(self):
        """Analyze performance across the 20 assessment criteria"""
        print("\n" + "="*60)
        print("🎯 CRITERIA PERFORMANCE ANALYSIS")
        print("="*60)
        
        criteria_names = [
            "ask_for_help", "stay_calm", "listen_actively", "express_clearly", "show_empathy",
            "ask_clarifying", "give_constructive", "handle_conflict", "build_confidence", "encourage_participation",
            "respect_boundaries", "offer_support", "celebrate_success", "address_concerns", "foster_connection",
            "model_behavior", "provide_feedback", "create_safety", "promote_growth", "maintain_balance"
        ]
        
        # Get best prompt from each generation
        best_per_gen = self.data['optimization']['best_per_generation']
        
        print(f"\n📊 Criteria Performance by Generation:")
        print(f"{'Generation':<12} {'Avg Improvement':<15} {'Best Criteria':<20} {'Worst Criteria':<20}")
        print("-" * 80)
        
        for i, prompt in enumerate(best_per_gen):
            metrics = prompt.get('performance_metrics', {})
            avg_improvement = metrics.get('avg_improvement', 0)
            
            # Get criteria scores
            criteria_scores = []
            for criterion in criteria_names:
                score = metrics.get(f'improvement_{criterion}', 0)
                criteria_scores.append((criterion, score))
            
            # Sort by performance
            criteria_scores.sort(key=lambda x: x[1], reverse=True)
            best_criterion = criteria_scores[0][0] if criteria_scores else "N/A"
            worst_criterion = criteria_scores[-1][0] if criteria_scores else "N/A"
            
            print(f"Gen {i:<10} {avg_improvement:<15.4f} {best_criterion:<20} {worst_criterion:<20}")
        
        # Overall criteria analysis
        print(f"\n📈 Overall Criteria Performance:")
        criteria_avg = {}
        for criterion in criteria_names:
            scores = []
            for prompt in best_per_gen:
                metrics = prompt.get('performance_metrics', {})
                score = metrics.get(f'improvement_{criterion}', 0)
                scores.append(score)
            criteria_avg[criterion] = np.mean(scores)
        
        # Sort by average performance
        sorted_criteria = sorted(criteria_avg.items(), key=lambda x: x[1], reverse=True)
        
        print(f"\n🏆 Top 5 Performing Criteria:")
        for criterion, score in sorted_criteria[:5]:
            print(f"  {criterion}: {score:.4f}")
            
        print(f"\n🔻 Bottom 5 Performing Criteria:")
        for criterion, score in sorted_criteria[-5:]:
            print(f"  {criterion}: {score:.4f}")
            
        return criteria_avg, sorted_criteria
    
    def analyze_prompt_evolution_patterns(self):
        """Analyze patterns in how prompts evolve"""
        print("\n" + "="*60)
        print("🔄 PROMPT EVOLUTION PATTERNS")
        print("="*60)
        
        all_prompts = self.data['optimization']['all_prompts']
        
        # Analyze prompt length evolution
        print(f"\n📏 Prompt Length Evolution:")
        for gen in range(6):  # Assuming 6 generations
            gen_prompts = [p for p in all_prompts if p['generation'] == gen]
            if gen_prompts:
                lengths = [len(p['prompt_text']) for p in gen_prompts]
                print(f"  Gen {gen}: Avg length {np.mean(lengths):.1f} chars (min: {min(lengths)}, max: {max(lengths)})")
        
        # Analyze prompt text patterns
        print(f"\n🔍 Common Prompt Patterns:")
        
        # Extract common phrases
        all_texts = [p['prompt_text'] for p in all_prompts]
        common_phrases = self._extract_common_phrases(all_texts)
        
        print(f"\n📝 Most Common Phrases:")
        for phrase, count in common_phrases[:10]:
            print(f"  \"{phrase}\": {count} occurrences")
            
        # Analyze prompt complexity
        print(f"\n🧮 Prompt Complexity Analysis:")
        for gen in range(6):
            gen_prompts = [p for p in all_prompts if p['generation'] == gen]
            if gen_prompts:
                complexities = []
                for prompt in gen_prompts:
                    text = prompt['prompt_text']
                    # Simple complexity metrics
                    word_count = len(text.split())
                    sentence_count = len([s for s in text.split('.') if s.strip()])
                    avg_words_per_sentence = word_count / max(sentence_count, 1)
                    complexities.append(avg_words_per_sentence)
                
                print(f"  Gen {gen}: Avg {np.mean(complexities):.1f} words per sentence")
        
        return common_phrases
    
    def _extract_common_phrases(self, texts: List[str], min_length: int = 3) -> List[Tuple[str, int]]:
        """Extract common phrases from prompt texts"""
        phrase_counts = Counter()
        
        for text in texts:
            words = text.lower().split()
            for i in range(len(words) - min_length + 1):
                phrase = ' '.join(words[i:i+min_length])
                phrase_counts[phrase] += 1
        
        return phrase_counts.most_common(20)
    
    def identify_improvement_opportunities(self):
        """Identify specific opportunities for improvement"""
        print("\n" + "="*60)
        print("💡 IMPROVEMENT OPPORTUNITIES")
        print("="*60)
        
        # Analyze the optimization history
        optimization_history = self.data['optimization']['optimization_history']
        
        print(f"\n📊 Optimization History Analysis:")
        print(f"  Total optimization steps: {len(optimization_history)}")
        
        # Analyze success vs failure patterns
        successful_improvements = [r for r in optimization_history if r.get('improvement', 0) > 0]
        failed_improvements = [r for r in optimization_history if r.get('improvement', 0) <= 0]
        
        print(f"  Successful improvements: {len(successful_improvements)} ({len(successful_improvements)/len(optimization_history)*100:.1f}%)")
        print(f"  Failed improvements: {len(failed_improvements)} ({len(failed_improvements)/len(optimization_history)*100:.1f}%)")
        
        # Analyze reflection insights
        print(f"\n🧠 Reflection Insights Analysis:")
        insights = [r.get('reflection_insights', '') for r in optimization_history if r.get('reflection_insights')]
        if insights:
            print(f"  Prompts with insights: {len(insights)}/{len(optimization_history)}")
            
            # Extract common insight themes
            insight_words = []
            for insight in insights:
                if isinstance(insight, str):
                    words = re.findall(r'\b\w+\b', insight.lower())
                    insight_words.extend(words)
                elif isinstance(insight, list):
                    for item in insight:
                        if isinstance(item, str):
                            words = re.findall(r'\b\w+\b', item.lower())
                            insight_words.extend(words)
            
            common_insight_words = Counter(insight_words).most_common(10)
            print(f"  Common insight themes: {[word for word, count in common_insight_words]}")
        
        # Analyze success/failure factors
        print(f"\n🎯 Success/Failure Factor Analysis:")
        success_factors = [r.get('success_factors', []) for r in successful_improvements if r.get('success_factors')]
        failure_factors = [r.get('failure_factors', []) for r in failed_improvements if r.get('failure_factors')]
        
        if success_factors:
            flat_success = [factor for factors in success_factors for factor in factors]
            success_counter = Counter(flat_success)
            print(f"  Top success factors: {[factor for factor, count in success_counter.most_common(5)]}")
        
        if failure_factors:
            flat_failure = [factor for factors in failure_factors for factor in failure_factors]
            failure_counter = Counter(flat_failure)
            print(f"  Top failure factors: {[factor for factor, count in failure_counter.most_common(5)]}")
        
        return successful_improvements, failed_improvements
    
    def generate_recommendations(self):
        """Generate specific recommendations for improvement"""
        print("\n" + "="*60)
        print("🎯 RECOMMENDATIONS FOR IMPROVEMENT")
        print("="*60)
        
        recommendations = []
        
        # Analyze the data to generate recommendations
        best_per_gen, improvements = self.analyze_generation_progression()
        gen_prompts = self.analyze_prompt_diversity()
        mutation_prompts, crossover_prompts, initial_prompts = self.analyze_llm_evolution_effectiveness()
        criteria_avg, sorted_criteria = self.analyze_criteria_performance()
        
        print(f"\n💡 Key Recommendations:")
        
        # 1. Diversity issues
        total_prompts = sum(len(prompts) for prompts in gen_prompts.values())
        unique_prompts = len(set(p['prompt_text'] for p in self.data['optimization']['all_prompts']))
        diversity_ratio = unique_prompts / total_prompts
        
        if diversity_ratio < 0.8:
            recommendations.append({
                'issue': 'Low prompt diversity',
                'description': f'Only {diversity_ratio:.1%} of prompts are unique',
                'solution': 'Improve LLM mutation/crossover prompts to generate more diverse variations'
            })
        
        # 2. Performance stagnation
        if improvements[-1] - improvements[0] < 0.1:
            recommendations.append({
                'issue': 'Performance stagnation',
                'description': f'Improvement only increased by {improvements[-1] - improvements[0]:.4f} across generations',
                'solution': 'Increase mutation rate, improve LLM prompts, or add more exploration'
            })
        
        # 3. LLM fallback issues
        mutation_fallback_rate = len([p for p in mutation_prompts if p['prompt_text'] == p.get('parent_prompt_text', '')]) / len(mutation_prompts) if mutation_prompts else 0
        if mutation_fallback_rate > 0.3:
            recommendations.append({
                'issue': 'High LLM fallback rate',
                'description': f'{mutation_fallback_rate:.1%} of mutations fall back to parent prompt',
                'solution': 'Improve LLM API reliability, adjust prompts, or increase timeout'
            })
        
        # 4. Criteria performance gaps
        worst_criteria = [criterion for criterion, score in sorted_criteria[-3:]]
        if any(score < 0.2 for criterion, score in sorted_criteria[-3:]):
            recommendations.append({
                'issue': 'Poor performance on specific criteria',
                'description': f'Criteria {worst_criteria} performing poorly',
                'solution': 'Focus mutation/crossover on improving these specific areas'
            })
        
        # Print recommendations
        for i, rec in enumerate(recommendations, 1):
            print(f"\n{i}. {rec['issue'].upper()}")
            print(f"   Problem: {rec['description']}")
            print(f"   Solution: {rec['solution']}")
        
        if not recommendations:
            print("✅ No major issues identified. System appears to be working well!")
        
        return recommendations
    
    def create_visualizations(self):
        """Create visualizations of the analysis"""
        print("\n" + "="*60)
        print("📊 CREATING VISUALIZATIONS")
        print("="*60)
        
        try:
            # Set up the plotting style
            plt.style.use('default')
            fig, axes = plt.subplots(2, 2, figsize=(15, 12))
            fig.suptitle('Validation Test Results Analysis', fontsize=16, fontweight='bold')
            
            # 1. Generation progression
            best_per_gen = self.data['optimization']['best_per_generation']
            improvements = [p.get('performance_metrics', {}).get('avg_improvement', 0) for p in best_per_gen]
            
            axes[0, 0].plot(range(len(improvements)), improvements, 'o-', linewidth=2, markersize=8)
            axes[0, 0].set_title('Performance Progression Across Generations')
            axes[0, 0].set_xlabel('Generation')
            axes[0, 0].set_ylabel('Average Improvement')
            axes[0, 0].grid(True, alpha=0.3)
            
            # 2. Criteria performance heatmap
            criteria_names = [
                "ask_for_help", "stay_calm", "listen_actively", "express_clearly", "show_empathy",
                "ask_clarifying", "give_constructive", "handle_conflict", "build_confidence", "encourage_participation",
                "respect_boundaries", "offer_support", "celebrate_success", "address_concerns", "foster_connection",
                "model_behavior", "provide_feedback", "create_safety", "promote_growth", "maintain_balance"
            ]
            
            # Get criteria scores for each generation
            criteria_matrix = []
            for prompt in best_per_gen:
                metrics = prompt.get('performance_metrics', {})
                row = [metrics.get(f'improvement_{criterion}', 0) for criterion in criteria_names]
                criteria_matrix.append(row)
            
            im = axes[0, 1].imshow(criteria_matrix, cmap='RdYlGn', aspect='auto')
            axes[0, 1].set_title('Criteria Performance Heatmap')
            axes[0, 1].set_xlabel('Criteria')
            axes[0, 1].set_ylabel('Generation')
            axes[0, 1].set_xticks(range(len(criteria_names)))
            axes[0, 1].set_xticklabels([c.replace('_', '\n') for c in criteria_names], rotation=45, ha='right')
            plt.colorbar(im, ax=axes[0, 1])
            
            # 3. Prompt length distribution
            all_prompts = self.data['optimization']['all_prompts']
            lengths_by_gen = defaultdict(list)
            for prompt in all_prompts:
                lengths_by_gen[prompt['generation']].append(len(prompt['prompt_text']))
            
            for gen in sorted(lengths_by_gen.keys()):
                axes[1, 0].hist(lengths_by_gen[gen], alpha=0.7, label=f'Gen {gen}', bins=10)
            axes[1, 0].set_title('Prompt Length Distribution by Generation')
            axes[1, 0].set_xlabel('Prompt Length (characters)')
            axes[1, 0].set_ylabel('Frequency')
            axes[1, 0].legend()
            axes[1, 0].grid(True, alpha=0.3)
            
            # 4. Performance distribution
            all_improvements = [p.get('performance_metrics', {}).get('avg_improvement', 0) for p in all_prompts]
            axes[1, 1].hist(all_improvements, bins=20, alpha=0.7, color='skyblue', edgecolor='black')
            axes[1, 1].set_title('Overall Performance Distribution')
            axes[1, 1].set_xlabel('Average Improvement')
            axes[1, 1].set_ylabel('Frequency')
            axes[1, 1].axvline(np.mean(all_improvements), color='red', linestyle='--', label=f'Mean: {np.mean(all_improvements):.3f}')
            axes[1, 1].legend()
            axes[1, 1].grid(True, alpha=0.3)
            
            plt.tight_layout()
            plt.savefig('validation_analysis.png', dpi=300, bbox_inches='tight')
            print("✅ Visualizations saved as 'validation_analysis.png'")
            
        except Exception as e:
            print(f"⚠️  Could not create visualizations: {e}")
    
    def run_full_analysis(self):
        """Run the complete analysis"""
        print("🚀 Starting comprehensive validation results analysis...")
        print(f"📁 Analyzing: {self.results_file}")
        
        # Run all analysis components
        self.analyze_generation_progression()
        self.analyze_prompt_diversity()
        self.analyze_llm_evolution_effectiveness()
        self.analyze_criteria_performance()
        self.analyze_prompt_evolution_patterns()
        self.identify_improvement_opportunities()
        recommendations = self.generate_recommendations()
        self.create_visualizations()
        
        print("\n" + "="*60)
        print("✅ ANALYSIS COMPLETE")
        print("="*60)
        
        return recommendations

def main():
    """Main function to run the analysis"""
    analyzer = ValidationAnalyzer('data/validation_test_results.json')
    recommendations = analyzer.run_full_analysis()
    
    print(f"\n📋 SUMMARY:")
    print(f"  - Analyzed {len(analyzer.data['optimization']['all_prompts'])} total prompts")
    print(f"  - Found {len(recommendations)} key improvement opportunities")
    print(f"  - Generated visualizations in 'validation_analysis.png'")
    
    return analyzer, recommendations

if __name__ == "__main__":
    analyzer, recommendations = main()
