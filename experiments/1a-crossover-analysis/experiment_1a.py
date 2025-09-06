#!/usr/bin/env python3
"""
Experiment 1A: Crossover Fallback Analysis

Objective: Identify root cause of 83.8% fallback rate in crossover operations
Hypothesis: API failures, prompt issues, or validation problems are causing fallbacks

This experiment adds detailed logging to crossover LLM calls to understand:
1. API response times and error codes
2. Response quality and content
3. Validation failure reasons
4. Success vs failure patterns
"""

import json
import time
import requests
from typing import Dict, List, Any, Tuple
from datetime import datetime
import logging

# Set up detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('experiments/1a-crossover-analysis/crossover_analysis.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class CrossoverAnalyzer:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.analysis_results = {
            'total_attempts': 0,
            'successful_calls': 0,
            'failed_calls': 0,
            'validation_failures': 0,
            'api_errors': 0,
            'response_times': [],
            'error_types': {},
            'success_patterns': [],
            'failure_patterns': []
        }
    
    def analyze_crossover_call(self, parent1_text: str, parent2_text: str, 
                             parent1_metrics: Dict, parent2_metrics: Dict) -> Dict[str, Any]:
        """Analyze a single crossover LLM call with detailed logging"""
        
        start_time = time.time()
        self.analysis_results['total_attempts'] += 1
        
        logger.info(f"[ANALYZE] Analyzing crossover call #{self.analysis_results['total_attempts']}")
        logger.info(f"   Parent 1: {parent1_text[:50]}...")
        logger.info(f"   Parent 2: {parent2_text[:50]}...")
        
        # Create the crossover prompt
        crossover_prompt = self._create_crossover_prompt(parent1_text, parent2_text, parent1_metrics, parent2_metrics)
        
        # Make API call with detailed error handling
        try:
            response = requests.post(
                "https://api.deepseek.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "deepseek-chat",
                    "messages": [{"role": "user", "content": crossover_prompt}],
                    "max_tokens": 200,
                    "temperature": 0.7
                },
                timeout=30
            )
            
            response_time = time.time() - start_time
            self.analysis_results['response_times'].append(response_time)
            
            logger.info(f"   [TIME] Response time: {response_time:.2f}s")
            logger.info(f"   [STATUS] Status code: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"   [SUCCESS] API call successful")
                
                if 'choices' in result and len(result['choices']) > 0:
                    generated_text = result['choices'][0]['message']['content'].strip()
                    logger.info(f"   [TEXT] Generated text: {generated_text[:100]}...")
                    
                    # Validate the response
                    validation_result = self._validate_response(generated_text, parent1_text, parent2_text)
                    
                    if validation_result['is_valid']:
                        self.analysis_results['successful_calls'] += 1
                        self.analysis_results['success_patterns'].append({
                            'parent1_length': len(parent1_text),
                            'parent2_length': len(parent2_text),
                            'generated_length': len(generated_text),
                            'response_time': response_time,
                            'generated_text': generated_text
                        })
                        logger.info(f"   [PASS] Validation passed")
                        return {
                            'success': True,
                            'generated_text': generated_text,
                            'response_time': response_time,
                            'validation': validation_result
                        }
                    else:
                        self.analysis_results['validation_failures'] += 1
                        logger.warning(f"   [FAIL] Validation failed: {validation_result['reason']}")
                        return {
                            'success': False,
                            'error_type': 'validation_failure',
                            'reason': validation_result['reason'],
                            'response_time': response_time
                        }
                else:
                    self.analysis_results['api_errors'] += 1
                    logger.error(f"   [ERROR] No choices in response: {result}")
                    return {
                        'success': False,
                        'error_type': 'no_choices',
                        'response_time': response_time
                    }
            else:
                self.analysis_results['api_errors'] += 1
                error_msg = f"API call failed with status {response.status_code}: {response.text}"
                logger.error(f"   [ERROR] {error_msg}")
                self.analysis_results['error_types'][f'status_{response.status_code}'] = \
                    self.analysis_results['error_types'].get(f'status_{response.status_code}', 0) + 1
                return {
                    'success': False,
                    'error_type': 'api_error',
                    'status_code': response.status_code,
                    'error_message': response.text,
                    'response_time': response_time
                }
                
        except requests.exceptions.Timeout:
            self.analysis_results['api_errors'] += 1
            error_msg = "API call timed out after 30 seconds"
            logger.error(f"   ❌ {error_msg}")
            self.analysis_results['error_types']['timeout'] = \
                self.analysis_results['error_types'].get('timeout', 0) + 1
            return {
                'success': False,
                'error_type': 'timeout',
                'response_time': time.time() - start_time
            }
        except Exception as e:
            self.analysis_results['api_errors'] += 1
            error_msg = f"Unexpected error: {str(e)}"
            logger.error(f"   ❌ {error_msg}")
            self.analysis_results['error_types']['unexpected'] = \
                self.analysis_results['error_types'].get('unexpected', 0) + 1
            return {
                'success': False,
                'error_type': 'unexpected',
                'error_message': str(e),
                'response_time': time.time() - start_time
            }
    
    def _create_crossover_prompt(self, parent1_text: str, parent2_text: str, 
                               parent1_metrics: Dict, parent2_metrics: Dict) -> str:
        """Create the crossover prompt (current version)"""
        return f"""
You are an expert prompt engineer creating a child prompt by combining the best elements of two parent prompts.

Parent 1: "{parent1_text}"
Parent 1 Performance: {parent1_metrics}

Parent 2: "{parent2_text}"
Parent 2 Performance: {parent2_metrics}

Instructions:
- Analyze both parent prompts and their performance metrics
- Identify the strongest elements from each parent
- Create a new prompt that combines these strengths
- Focus on the highest-performing criteria from both parents
- Ensure the new prompt is coherent and effective
- Keep it concise but impactful

Respond with ONLY the new prompt text, no explanations.
"""
    
    def _validate_response(self, generated_text: str, parent1_text: str, parent2_text: str) -> Dict[str, Any]:
        """Validate the generated response"""
        
        # Check if response is empty or too short
        if not generated_text or len(generated_text.strip()) < 10:
            return {
                'is_valid': False,
                'reason': 'Response too short or empty'
            }
        
        # Check if response is too long (more than 3x the longer parent)
        max_parent_length = max(len(parent1_text), len(parent2_text))
        if len(generated_text) > max_parent_length * 3.0:
            return {
                'is_valid': False,
                'reason': f'Response too long: {len(generated_text)} chars vs max {max_parent_length * 3.0}'
            }
        
        # Check if response is just a copy of one parent
        if generated_text.strip() == parent1_text.strip() or generated_text.strip() == parent2_text.strip():
            return {
                'is_valid': False,
                'reason': 'Response is identical to one parent'
            }
        
        # Check if response contains common fallback patterns
        fallback_patterns = [
            "Be supportive and provide practical, growth-oriented advice.",
            "Be supportive and provide practical, confidence-building advice.",
            "Be supportive and provide practical, growth-focused advice."
        ]
        
        if generated_text.strip() in fallback_patterns:
            return {
                'is_valid': False,
                'reason': 'Response matches common fallback pattern'
            }
        
        return {
            'is_valid': True,
            'reason': 'All validations passed'
        }
    
    def run_analysis(self, test_cases: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Run analysis on multiple test cases"""
        
        logger.info(f"🚀 Starting crossover analysis with {len(test_cases)} test cases")
        
        results = []
        for i, test_case in enumerate(test_cases):
            logger.info(f"\n{'='*60}")
            logger.info(f"Test Case {i+1}/{len(test_cases)}")
            logger.info(f"{'='*60}")
            
            result = self.analyze_crossover_call(
                test_case['parent1_text'],
                test_case['parent2_text'],
                test_case['parent1_metrics'],
                test_case['parent2_metrics']
            )
            
            results.append({
                'test_case_id': i+1,
                'parent1_text': test_case['parent1_text'],
                'parent2_text': test_case['parent2_text'],
                'result': result
            })
        
        # Calculate summary statistics
        self.analysis_results['success_rate'] = (
            self.analysis_results['successful_calls'] / self.analysis_results['total_attempts'] * 100
            if self.analysis_results['total_attempts'] > 0 else 0
        )
        
        self.analysis_results['avg_response_time'] = (
            sum(self.analysis_results['response_times']) / len(self.analysis_results['response_times'])
            if self.analysis_results['response_times'] else 0
        )
        
        # Generate analysis report
        report = self._generate_analysis_report()
        
        return {
            'analysis_results': self.analysis_results,
            'test_results': results,
            'report': report
        }
    
    def _generate_analysis_report(self) -> str:
        """Generate a detailed analysis report"""
        
        report = f"""
# Crossover Fallback Analysis Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary Statistics
- Total Attempts: {self.analysis_results['total_attempts']}
- Successful Calls: {self.analysis_results['successful_calls']} ({self.analysis_results['success_rate']:.1f}%)
- Failed Calls: {self.analysis_results['failed_calls']}
- Validation Failures: {self.analysis_results['validation_failures']}
- API Errors: {self.analysis_results['api_errors']}

## Performance Metrics
- Average Response Time: {self.analysis_results['avg_response_time']:.2f}s
- Response Time Range: {min(self.analysis_results['response_times']):.2f}s - {max(self.analysis_results['response_times']):.2f}s

## Error Analysis
"""
        
        for error_type, count in self.analysis_results['error_types'].items():
            report += f"- {error_type}: {count} occurrences\n"
        
        report += f"""
## Success Patterns
- Average successful response length: {sum(r['generated_length'] for r in self.analysis_results['success_patterns']) / len(self.analysis_results['success_patterns']) if self.analysis_results['success_patterns'] else 0:.0f} characters
- Average response time for successful calls: {sum(r['response_time'] for r in self.analysis_results['success_patterns']) / len(self.analysis_results['success_patterns']) if self.analysis_results['success_patterns'] else 0:.2f}s

## Recommendations
"""
        
        if self.analysis_results['success_rate'] < 50:
            report += "- CRITICAL: Success rate is very low. Check API connectivity and prompt quality.\n"
        
        if self.analysis_results['validation_failures'] > self.analysis_results['api_errors']:
            report += "- Primary issue: Validation failures. Consider relaxing validation rules.\n"
        else:
            report += "- Primary issue: API errors. Check API key, rate limits, and network connectivity.\n"
        
        if self.analysis_results['avg_response_time'] > 10:
            report += "- Response times are high. Consider increasing timeout or optimizing prompts.\n"
        
        return report

def create_test_cases() -> List[Dict[str, Any]]:
    """Create test cases for crossover analysis"""
    
    return [
        {
            'parent1_text': "You are a helpful peer mentor for college students. Be supportive and provide practical advice.",
            'parent2_text': "You are a supportive AI assistant helping students improve their social skills. Be encouraging, provide practical advice, and help them build confidence gradually.",
            'parent1_metrics': {'avg_improvement': 0.3467, 'test_count': 15},
            'parent2_metrics': {'avg_improvement': 0.3800, 'test_count': 15}
        },
        {
            'parent1_text': "Be supportive and provide practical, growth-oriented advice.",
            'parent2_text': "Be supportive and provide practical, confidence-building advice.",
            'parent1_metrics': {'avg_improvement': 0.3800, 'test_count': 15},
            'parent2_metrics': {'avg_improvement': 0.3833, 'test_count': 15}
        },
        {
            'parent1_text': "You are a social skills coach who uses storytelling and metaphors to help students.",
            'parent2_text': "You are a peer mentor who focuses on building emotional intelligence and self-awareness.",
            'parent1_metrics': {'avg_improvement': 0.3500, 'test_count': 15},
            'parent2_metrics': {'avg_improvement': 0.3600, 'test_count': 15}
        }
    ]

def main():
    """Run the crossover analysis experiment"""
    
    # Load API key from config
    try:
        from config import Config
        api_key = Config.DEEPSEEK_API_KEY
    except ImportError:
        api_key = "sk-d64d89acb0904956a4f5e37d512ae950"  # Fallback
    
    # Create analyzer
    analyzer = CrossoverAnalyzer(api_key)
    
    # Create test cases
    test_cases = create_test_cases()
    
    # Run analysis
    results = analyzer.run_analysis(test_cases)
    
    # Save results
    with open('experiments/1a-crossover-analysis/analysis_results.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    # Save report
    with open('experiments/1a-crossover-analysis/analysis_report.md', 'w') as f:
        f.write(results['report'])
    
    print(f"\n[SUCCESS] Analysis complete!")
    print(f"[STATS] Success rate: {results['analysis_results']['success_rate']:.1f}%")
    print(f"[TIME] Average response time: {results['analysis_results']['avg_response_time']:.2f}s")
    print(f"[FILES] Results saved to experiments/1a-crossover-analysis/")

if __name__ == "__main__":
    main()

