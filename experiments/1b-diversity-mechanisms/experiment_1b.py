#!/usr/bin/env python3
"""
Experiment 1B: Diversity Mechanisms
===================================

This experiment tests different diversity mechanisms to prevent prompts from becoming too similar.
We'll implement and test:

1. Semantic Diversity: Force different approaches (coaching vs mentoring vs peer support)
2. Length Variation: Encourage short, medium, and long prompts  
3. Style Diversity: Vary tone (encouraging vs direct vs gentle)
4. Diversity Scoring: Measure prompt similarity using text analysis

The goal is to maintain genetic diversity in our prompt population while still improving performance.
"""

import json
import time
import logging
import requests
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass
from datetime import datetime
import re
from collections import Counter
import math

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('experiments/1b-diversity-mechanisms/diversity_analysis.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class PromptSample:
    """Sample prompt for diversity testing"""
    text: str
    length: int
    style: str  # 'coaching', 'mentoring', 'peer', 'direct', 'gentle'
    approach: str  # 'practical', 'emotional', 'technical', 'social'
    generation: int

class DiversityAnalyzer:
    """Analyze and implement diversity mechanisms for prompt evolution"""
    
    def __init__(self):
        self.analysis_results = {
            'total_tests': 0,
            'diversity_scores': [],
            'similarity_matrix': [],
            'style_distribution': {},
            'length_variation': {},
            'semantic_clusters': [],
            'improvement_correlation': {}
        }
    
    def calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Calculate semantic similarity between two texts using word overlap"""
        # Simple word-based similarity (could be enhanced with embeddings)
        words1 = set(re.findall(r'\b\w+\b', text1.lower()))
        words2 = set(re.findall(r'\b\w+\b', text2.lower()))
        
        if not words1 and not words2:
            return 1.0
        if not words1 or not words2:
            return 0.0
            
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        return intersection / union if union > 0 else 0.0
    
    def calculate_diversity_score(self, prompts: List[PromptSample]) -> float:
        """Calculate overall diversity score for a set of prompts"""
        if len(prompts) < 2:
            return 0.0
            
        similarities = []
        for i in range(len(prompts)):
            for j in range(i + 1, len(prompts)):
                sim = self.calculate_text_similarity(prompts[i].text, prompts[j].text)
                similarities.append(sim)
        
        # Diversity = 1 - average_similarity
        avg_similarity = sum(similarities) / len(similarities) if similarities else 0.0
        return 1.0 - avg_similarity
    
    def analyze_style_distribution(self, prompts: List[PromptSample]) -> Dict[str, int]:
        """Analyze the distribution of styles in the prompt set"""
        style_counts = Counter(prompt.style for prompt in prompts)
        return dict(style_counts)
    
    def analyze_length_variation(self, prompts: List[PromptSample]) -> Dict[str, Any]:
        """Analyze length variation in the prompt set"""
        lengths = [prompt.length for prompt in prompts]
        return {
            'min_length': min(lengths),
            'max_length': max(lengths),
            'avg_length': sum(lengths) / len(lengths),
            'length_std': math.sqrt(sum((x - sum(lengths)/len(lengths))**2 for x in lengths) / len(lengths)),
            'length_range': max(lengths) - min(lengths)
        }
    
    def create_diversity_enhanced_crossover_prompt(self, parent1: str, parent2: str, 
                                                 existing_prompts: List[str],
                                                 target_diversity: float = 0.7) -> str:
        """Create a crossover prompt that enhances diversity"""
        
        # Analyze existing prompts to understand current patterns
        existing_styles = self._analyze_existing_styles(existing_prompts)
        existing_lengths = [len(p) for p in existing_prompts]
        avg_existing_length = sum(existing_lengths) / len(existing_lengths) if existing_lengths else 100
        
        # Create diversity-aware crossover prompt
        diversity_prompt = f"""
You are an expert prompt engineer creating a diverse child prompt by combining two parent prompts.

PARENT 1: "{parent1}"
PARENT 2: "{parent2}"

DIVERSITY REQUIREMENTS:
- Current population average length: {avg_existing_length:.0f} characters
- Target diversity: {target_diversity:.1f} (higher = more different from existing prompts)
- Existing style patterns: {', '.join(existing_styles[:3]) if existing_styles else 'none detected'}

TASK: Create a new prompt that:
1. Combines the BEST elements from both parents
2. Is DIFFERENT from existing prompts (avoid common phrases like "Be supportive and provide practical advice")
3. Uses a UNIQUE approach or style not over-represented in the population
4. Varies in length from the average (shorter OR longer than {avg_existing_length:.0f} chars)
5. Maintains effectiveness for social skills coaching

DIVERSITY STRATEGIES:
- Use different action words: "guide" vs "help" vs "support" vs "mentor"
- Vary sentence structure: questions vs statements vs commands
- Focus on different aspects: emotional vs practical vs social vs technical
- Use different tones: encouraging vs direct vs gentle vs confident

EXAMPLES of diverse approaches:
- "Guide students through social challenges with empathy and practical steps"
- "What social skills would you like to develop? Let's explore together"
- "I'm here to help you build confidence in social situations through practice"
- "Together, we'll identify your social strengths and work on areas for growth"

CRITICAL: Make this prompt UNIQUE and DIFFERENT from common patterns. Avoid generic phrases.

Respond with ONLY the new prompt text, no explanations.
"""
        
        return diversity_prompt
    
    def _analyze_existing_styles(self, prompts: List[str]) -> List[str]:
        """Analyze existing prompt styles to identify patterns"""
        common_phrases = []
        for prompt in prompts:
            # Extract common patterns
            if "supportive" in prompt.lower():
                common_phrases.append("supportive")
            if "practical" in prompt.lower():
                common_phrases.append("practical")
            if "help" in prompt.lower():
                common_phrases.append("help")
            if "advice" in prompt.lower():
                common_phrases.append("advice")
            if "confidence" in prompt.lower():
                common_phrases.append("confidence")
        
        # Return most common patterns
        phrase_counts = Counter(common_phrases)
        return [phrase for phrase, count in phrase_counts.most_common(5)]
    
    def test_diversity_mechanism(self, parent1: str, parent2: str, 
                               existing_prompts: List[str]) -> Dict[str, Any]:
        """Test the diversity-enhanced crossover mechanism"""
        
        start_time = time.time()
        self.analysis_results['total_tests'] += 1
        
        logger.info(f"[DIVERSITY] Testing diversity mechanism #{self.analysis_results['total_tests']}")
        logger.info(f"   Parent 1: {parent1[:50]}...")
        logger.info(f"   Parent 2: {parent2[:50]}...")
        logger.info(f"   Existing prompts: {len(existing_prompts)}")
        
        # Create diversity-enhanced crossover prompt
        diversity_prompt = self.create_diversity_enhanced_crossover_prompt(
            parent1, parent2, existing_prompts
        )
        
        try:
            # Call LLM for diversity-enhanced crossover
            import sys
            import os
            sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
            from config import Config
            
            logger.info(f"   [API] Making diversity-enhanced crossover call...")
            response = requests.post(
                "https://api.deepseek.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {Config.DEEPSEEK_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "deepseek-chat",
                    "messages": [{"role": "user", "content": diversity_prompt}],
                    "temperature": 0.8,  # Higher temperature for more diversity
                    "max_tokens": 200
                },
                timeout=30
            )
            
            response_time = time.time() - start_time
            logger.info(f"   [TIME] Response time: {response_time:.2f}s")
            logger.info(f"   [STATUS] Status code: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"   [SUCCESS] API call successful")
                
                if 'choices' in result and len(result['choices']) > 0:
                    generated_text = result['choices'][0]['message']['content'].strip()
                    logger.info(f"   [TEXT] Generated: {generated_text[:100]}...")
                    
                    # Calculate diversity metrics
                    all_prompts = existing_prompts + [generated_text]
                    diversity_score = self.calculate_diversity_score([
                        PromptSample(text=p, length=len(p), style="unknown", approach="unknown", generation=0)
                        for p in all_prompts
                    ])
                    
                    # Calculate similarity to parents
                    sim_to_parent1 = self.calculate_text_similarity(generated_text, parent1)
                    sim_to_parent2 = self.calculate_text_similarity(generated_text, parent2)
                    
                    logger.info(f"   [DIVERSITY] Score: {diversity_score:.3f}")
                    logger.info(f"   [SIMILARITY] To parent1: {sim_to_parent1:.3f}, To parent2: {sim_to_parent2:.3f}")
                    
                    return {
                        'success': True,
                        'generated_text': generated_text,
                        'diversity_score': diversity_score,
                        'similarity_to_parent1': sim_to_parent1,
                        'similarity_to_parent2': sim_to_parent2,
                        'response_time': response_time,
                        'length': len(generated_text)
                    }
                else:
                    logger.error(f"   [ERROR] No choices in response")
                    return {'success': False, 'error': 'No choices in response'}
            else:
                logger.error(f"   [ERROR] API Error: {response.status_code}")
                return {'success': False, 'error': f'API Error: {response.status_code}'}
                
        except Exception as e:
            logger.error(f"   [ERROR] Exception: {e}")
            return {'success': False, 'error': str(e)}
    
    def run_diversity_analysis(self, test_cases: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Run comprehensive diversity analysis"""
        
        logger.info(f"[START] Starting diversity analysis with {len(test_cases)} test cases")
        
        results = []
        existing_prompts = []
        
        for i, test_case in enumerate(test_cases):
            logger.info(f"\n{'='*60}")
            logger.info(f"Test Case {i+1}/{len(test_cases)}")
            logger.info(f"{'='*60}")
            
            parent1 = test_case['parent1']
            parent2 = test_case['parent2']
            
            # Test diversity mechanism
            result = self.test_diversity_mechanism(parent1, parent2, existing_prompts)
            
            if result['success']:
                # Add to existing prompts for next iteration
                existing_prompts.append(result['generated_text'])
                
                # Track diversity metrics
                self.analysis_results['diversity_scores'].append(result['diversity_score'])
                
                results.append({
                    'test_case_id': i + 1,
                    'parent1': parent1,
                    'parent2': parent2,
                    'result': result
                })
                
                logger.info(f"   [SUCCESS] Diversity score: {result['diversity_score']:.3f}")
            else:
                logger.error(f"   [FAILED] {result.get('error', 'Unknown error')}")
                results.append({
                    'test_case_id': i + 1,
                    'parent1': parent1,
                    'parent2': parent2,
                    'result': result
                })
        
        # Calculate final statistics
        successful_results = [r for r in results if r['result']['success']]
        
        if successful_results:
            avg_diversity = sum(r['result']['diversity_score'] for r in successful_results) / len(successful_results)
            avg_similarity_p1 = sum(r['result']['similarity_to_parent1'] for r in successful_results) / len(successful_results)
            avg_similarity_p2 = sum(r['result']['similarity_to_parent2'] for r in successful_results) / len(successful_results)
            
            self.analysis_results['avg_diversity_score'] = avg_diversity
            self.analysis_results['avg_similarity_to_parent1'] = avg_similarity_p1
            self.analysis_results['avg_similarity_to_parent2'] = avg_similarity_p2
            self.analysis_results['success_rate'] = len(successful_results) / len(test_cases)
        else:
            self.analysis_results['avg_diversity_score'] = 0.0
            self.analysis_results['avg_similarity_to_parent1'] = 0.0
            self.analysis_results['avg_similarity_to_parent2'] = 0.0
            self.analysis_results['success_rate'] = 0.0
        
        # Generate report
        report = self._generate_diversity_report()
        
        return {
            'analysis_results': self.analysis_results,
            'test_results': results,
            'report': report
        }
    
    def _generate_diversity_report(self) -> str:
        """Generate a comprehensive diversity analysis report"""
        
        report = f"""
# Diversity Mechanisms Analysis Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary Statistics
- Total Tests: {self.analysis_results['total_tests']}
- Success Rate: {self.analysis_results.get('success_rate', 0):.1%}
- Average Diversity Score: {self.analysis_results.get('avg_diversity_score', 0):.3f}
- Average Similarity to Parent 1: {self.analysis_results.get('avg_similarity_to_parent1', 0):.3f}
- Average Similarity to Parent 2: {self.analysis_results.get('avg_similarity_to_parent2', 0):.3f}

## Diversity Analysis
- Higher diversity scores indicate more unique prompts
- Target diversity score: 0.7+ (70% unique)
- Current average: {self.analysis_results.get('avg_diversity_score', 0):.3f}

## Recommendations
"""
        
        avg_diversity = self.analysis_results.get('avg_diversity_score', 0)
        if avg_diversity < 0.5:
            report += "- LOW DIVERSITY: Prompts are too similar. Increase temperature and add more diversity constraints.\n"
        elif avg_diversity < 0.7:
            report += "- MODERATE DIVERSITY: Some improvement needed. Fine-tune diversity mechanisms.\n"
        else:
            report += "- HIGH DIVERSITY: Good diversity achieved. Consider maintaining current approach.\n"
        
        return report

def main():
    """Run the diversity mechanisms experiment"""
    
    # Test cases with different prompt combinations
    test_cases = [
        {
            'parent1': 'You are a helpful peer mentor for college students. Be supportive and provide practical advice.',
            'parent2': 'You are a supportive AI assistant helping students improve their social skills. Be encouraging, provide practical advice, and help them build confidence gradually.'
        },
        {
            'parent1': 'Be supportive and provide practical, growth-oriented advice.',
            'parent2': 'Be supportive and provide practical, confidence-building advice.'
        },
        {
            'parent1': 'You are a social skills coach who uses storytelling and metaphors to help students.',
            'parent2': 'You are a peer mentor who focuses on building emotional intelligence and self-awareness.'
        },
        {
            'parent1': 'Help students develop better communication skills through practice and feedback.',
            'parent2': 'Guide students in building social confidence and overcoming anxiety.'
        },
        {
            'parent1': 'Support students in their social skill development journey.',
            'parent2': 'Mentor students to improve their interpersonal relationships and social interactions.'
        }
    ]
    
    # Run diversity analysis
    analyzer = DiversityAnalyzer()
    results = analyzer.run_diversity_analysis(test_cases)
    
    # Save results
    with open('experiments/1b-diversity-mechanisms/diversity_results.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    # Save report
    with open('experiments/1b-diversity-mechanisms/diversity_report.md', 'w') as f:
        f.write(results['report'])
    
    print(f"\n[SUCCESS] Diversity analysis complete!")
    print(f"[STATS] Success rate: {results['analysis_results']['success_rate']:.1%}")
    print(f"[DIVERSITY] Average diversity score: {results['analysis_results']['avg_diversity_score']:.3f}")
    print(f"[FILES] Results saved to experiments/1b-diversity-mechanisms/")

if __name__ == "__main__":
    main()
