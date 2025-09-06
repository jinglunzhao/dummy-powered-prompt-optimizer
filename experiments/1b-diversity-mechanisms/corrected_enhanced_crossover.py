#!/usr/bin/env python3
"""
Corrected Enhanced Crossover: Performance + Diversity Balance
============================================================

This module correctly balances:
1. Preserving parent ASSESSMENT PERFORMANCE patterns (not literal words)
2. Encouraging semantic diversity in prompt generation
3. Maintaining effectiveness while adding variety

Key insight: Strengths are measured by 20-criteria assessment improvements, not literal words.
"""

import json
import time
import logging
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass
import re
from collections import Counter
import math

@dataclass
class ParentPerformanceProfile:
    """Performance profile based on 20-criteria assessment improvements"""
    prompt_text: str
    performance_metrics: Dict[str, float]  # 20 criteria + avg_improvement
    top_performing_criteria: List[Tuple[str, float]]  # (criterion, improvement_score)
    weak_criteria: List[Tuple[str, float]]  # (criterion, improvement_score)
    performance_pattern: Dict[str, Any]  # Analysis of what makes this prompt effective
    generation: int
    length: int

class CorrectedEnhancedCrossover:
    """Enhanced crossover that correctly balances assessment performance and diversity"""
    
    def __init__(self):
        self.criteria_names = [
            "ask_for_help", "stay_calm", "listen_actively", "express_clearly", "show_empathy",
            "ask_clarifying", "give_constructive", "handle_conflict", "build_confidence", "encourage_participation",
            "respect_boundaries", "offer_support", "celebrate_success", "address_concerns", "foster_connection",
            "model_behavior", "provide_feedback", "create_safety", "promote_growth", "maintain_balance"
        ]
    
    def analyze_parent_performance(self, prompt_text: str, performance_metrics: Dict[str, float], generation: int) -> ParentPerformanceProfile:
        """Analyze parent based on actual assessment performance, not literal words"""
        
        # Extract 20-criteria performance data
        criterion_scores = []
        for criterion in self.criteria_names:
            score = performance_metrics.get(f'improvement_{criterion}', 0)
            criterion_scores.append((criterion, score))
        
        # Sort by performance to identify strengths and weaknesses
        criterion_scores.sort(key=lambda x: x[1], reverse=True)
        top_performing = criterion_scores[:5]  # Top 5 performing criteria
        weak_criteria = criterion_scores[-3:]  # Bottom 3 performing criteria
        
        # Analyze what makes this prompt effective (performance pattern analysis)
        performance_pattern = self._analyze_performance_pattern(prompt_text, criterion_scores)
        
        return ParentPerformanceProfile(
            prompt_text=prompt_text,
            performance_metrics=performance_metrics,
            top_performing_criteria=top_performing,
            weak_criteria=weak_criteria,
            performance_pattern=performance_pattern,
            generation=generation,
            length=len(prompt_text)
        )
    
    def _analyze_performance_pattern(self, prompt_text: str, criterion_scores: List[Tuple[str, float]]) -> Dict[str, Any]:
        """Analyze what makes this prompt effective based on assessment performance"""
        
        # Find the top 3 performing criteria
        top_3_criteria = [criterion for criterion, score in criterion_scores[:3]] if criterion_scores else []
        
        # Analyze prompt characteristics that might contribute to these strengths
        prompt_lower = prompt_text.lower()
        
        # Check for different coaching approaches that might affect different criteria
        approach_indicators = {
            'questioning_approach': ['?', 'what', 'how', 'why', 'which', 'ask'],
            'supportive_approach': ['supportive', 'encouraging', 'helpful', 'patient', 'gentle'],
            'practical_approach': ['practical', 'step', 'action', 'concrete', 'specific'],
            'collaborative_approach': ['together', 'we', 'us', 'let\'s', 'guide', 'mentor'],
            'confidence_focused': ['confidence', 'believe', 'assurance', 'self-esteem', 'strength'],
            'empathy_focused': ['empathy', 'understand', 'feel', 'emotion', 'listen'],
            'feedback_focused': ['feedback', 'constructive', 'improve', 'develop', 'grow']
        }
        
        approach_scores = {}
        for approach, indicators in approach_indicators.items():
            score = sum(1 for indicator in indicators if indicator in prompt_lower)
            approach_scores[approach] = score
        
        # Determine dominant approach
        dominant_approach = max(approach_scores, key=approach_scores.get) if approach_scores else 'general'
        
        # Analyze sentence structure
        structure_analysis = {
            'has_question': '?' in prompt_text,
            'has_action_verb': any(word in prompt_lower for word in ['help', 'guide', 'support', 'provide', 'offer', 'build']),
            'has_qualifier': any(word in prompt_lower for word in ['practical', 'step-by-step', 'constructive', 'effective', 'confident']),
            'is_directive': prompt_text.startswith(('Be ', 'You are', 'I am', 'Help', 'Guide')),
            'is_collaborative': any(word in prompt_lower for word in ['together', 'we', 'us', 'let\'s'])
        }
        
        # Map top performing criteria to potential prompt characteristics
        criteria_to_characteristics = {
            'ask_for_help': ['questioning_approach', 'collaborative_approach'],
            'stay_calm': ['supportive_approach', 'empathy_focused'],
            'listen_actively': ['empathy_focused', 'collaborative_approach'],
            'express_clearly': ['practical_approach', 'feedback_focused'],
            'show_empathy': ['empathy_focused', 'supportive_approach'],
            'build_confidence': ['confidence_focused', 'supportive_approach'],
            'encourage_participation': ['collaborative_approach', 'supportive_approach'],
            'provide_feedback': ['feedback_focused', 'practical_approach'],
            'handle_conflict': ['practical_approach', 'empathy_focused'],
            'foster_connection': ['collaborative_approach', 'empathy_focused']
        }
        
        # Identify which characteristics might be contributing to top performance
        contributing_characteristics = []
        for criterion in top_3_criteria:
            if criterion in criteria_to_characteristics:
                contributing_characteristics.extend(criteria_to_characteristics[criterion])
        
        # Remove duplicates
        contributing_characteristics = list(set(contributing_characteristics))
        
        return {
            'top_3_criteria': top_3_criteria,
            'approach_scores': approach_scores,
            'dominant_approach': dominant_approach,
            'structure_analysis': structure_analysis,
            'contributing_characteristics': contributing_characteristics,
            'avg_improvement': 0.0  # Default value since we don't have performance_metrics here
        }
    
    def create_performance_diversity_crossover_prompt(self, parent1_profile: ParentPerformanceProfile, 
                                                    parent2_profile: ParentPerformanceProfile,
                                                    existing_prompts: List[str],
                                                    diversity_weight: float = 0.7) -> str:
        """Create crossover prompt that preserves assessment performance while encouraging diversity"""
        
        # Analyze existing population for diversity
        existing_patterns = self._analyze_existing_patterns(existing_prompts)
        
        # Create performance preservation instructions based on assessment results
        performance_instructions = self._create_performance_instructions(parent1_profile, parent2_profile)
        
        # Create diversity instructions
        diversity_instructions = self._create_diversity_instructions(existing_patterns, diversity_weight)
        
        # Combine both approaches
        crossover_prompt = f"""
You are an expert prompt engineer creating a child prompt that EXCELLS in both performance and diversity.

PARENT 1: "{parent1_profile.prompt_text}"
PARENT 1 TOP PERFORMING CRITERIA: {', '.join([f"{criterion}: {score:.3f}" for criterion, score in parent1_profile.top_performing_criteria[:3]])}
PARENT 1 EFFECTIVE PATTERN: {parent1_profile.performance_pattern['dominant_approach']} approach, {parent1_profile.performance_pattern['contributing_characteristics']}

PARENT 2: "{parent2_profile.prompt_text}"
PARENT 2 TOP PERFORMING CRITERIA: {', '.join([f"{criterion}: {score:.3f}" for criterion, score in parent2_profile.top_performing_criteria[:3]])}
PARENT 2 EFFECTIVE PATTERN: {parent2_profile.performance_pattern['dominant_approach']} approach, {parent2_profile.performance_pattern['contributing_characteristics']}

{performance_instructions}

{diversity_instructions}

BALANCE REQUIREMENTS:
- Preserve the ASSESSMENT PERFORMANCE that made both parents successful
- Create a UNIQUE approach that differs from existing patterns
- Maintain effectiveness while adding diversity
- Target length: {max(parent1_profile.length, parent2_profile.length)} characters (±20%)

EXAMPLES of performance-diversity balance:
- "What social challenges are you facing? Let's work through them together" (preserves questioning + collaboration performance)
- "I'm your social skills coach - let's build your confidence step by step" (preserves confidence-building performance)
- "Guide students through social interactions with empathy and practical strategies" (preserves guidance + empathy performance)

CRITICAL: The child must maintain the ASSESSMENT IMPROVEMENTS that made parents successful while being semantically unique.

Respond with ONLY the new prompt text, no explanations.
"""
        
        return crossover_prompt
    
    def _create_performance_instructions(self, parent1_profile: ParentPerformanceProfile, 
                                       parent2_profile: ParentPerformanceProfile) -> str:
        """Create performance preservation instructions based on assessment results"""
        
        # Find unique strengths from each parent
        p1_criteria = [criterion for criterion, score in parent1_profile.top_performing_criteria[:3]]
        p2_criteria = [criterion for criterion, score in parent2_profile.top_performing_criteria[:3]]
        
        unique_p1_criteria = [c for c in p1_criteria if c not in p2_criteria]
        unique_p2_criteria = [c for c in p2_criteria if c not in p1_criteria]
        shared_criteria = [c for c in p1_criteria if c in p2_criteria]
        
        # Map criteria to coaching strategies
        criteria_to_strategies = {
            'ask_for_help': 'encourage questioning and seeking assistance',
            'stay_calm': 'promote calmness and emotional regulation',
            'listen_actively': 'emphasize active listening and attention',
            'express_clearly': 'focus on clear communication and expression',
            'show_empathy': 'demonstrate understanding and emotional connection',
            'build_confidence': 'boost self-esteem and belief in abilities',
            'encourage_participation': 'motivate engagement and involvement',
            'provide_feedback': 'offer constructive guidance and improvement',
            'handle_conflict': 'address disagreements and difficult situations',
            'foster_connection': 'build relationships and social bonds'
        }
        
        performance_instructions = f"""
PERFORMANCE PRESERVATION (Based on Assessment Results):
- Parent 1 excels at: {', '.join(unique_p1_criteria) if unique_p1_criteria else 'general effectiveness'}
- Parent 2 excels at: {', '.join(unique_p2_criteria) if unique_p2_criteria else 'general effectiveness'}
- Both excel at: {', '.join(shared_criteria) if shared_criteria else 'general effectiveness'}

COACHING STRATEGIES TO PRESERVE:
- Parent 1 effective pattern: {parent1_profile.performance_pattern['contributing_characteristics']}
- Parent 2 effective pattern: {parent2_profile.performance_pattern['contributing_characteristics']}

REQUIREMENT: The child must maintain the ASSESSMENT IMPROVEMENTS that made parents successful.
Focus on the coaching approaches that led to high performance in the top criteria.
"""
        
        return performance_instructions
    
    def _create_diversity_instructions(self, existing_patterns: Dict[str, Any], diversity_weight: float) -> str:
        """Create diversity instructions based on existing patterns"""
        
        if not existing_patterns:
            return """
DIVERSITY REQUIREMENT:
- Create a unique approach not seen before
- Vary the tone, structure, and focus from common patterns
- Use different action words and sentence structures
"""
        
        common_phrases = existing_patterns.get('common_phrases', [])
        common_structures = existing_patterns.get('common_structures', [])
        common_approaches = existing_patterns.get('common_approaches', [])
        
        diversity_instructions = f"""
DIVERSITY REQUIREMENT (Weight: {diversity_weight:.1f}):
- AVOID these overused phrases: {', '.join(common_phrases[:3]) if common_phrases else 'none detected'}
- AVOID these common structures: {', '.join(common_structures[:2]) if common_structures else 'none detected'}
- AVOID these common approaches: {', '.join(common_approaches[:2]) if common_approaches else 'none detected'}

DIVERSITY STRATEGIES:
- Use different action words: "guide" vs "help" vs "support" vs "mentor" vs "coach"
- Vary sentence structure: questions vs statements vs commands vs invitations
- Focus on different aspects: emotional vs practical vs social vs technical vs confidence
- Use different tones: encouraging vs direct vs gentle vs confident vs collaborative
- Vary length and complexity within reason

EXAMPLES of diverse approaches:
- "What social challenges are you facing? Let's work through them together"
- "I'm your social skills coach - let's build your confidence step by step"
- "Guide students through social interactions with empathy and practical strategies"
- "Help students develop authentic social connections through practice and reflection"
"""
        
        return diversity_instructions
    
    def _analyze_existing_patterns(self, existing_prompts: List[str]) -> Dict[str, Any]:
        """Analyze existing prompts to identify common patterns"""
        
        if not existing_prompts:
            return {}
        
        # Common phrases analysis
        all_words = []
        for prompt in existing_prompts:
            words = re.findall(r'\b\w+\b', prompt.lower())
            all_words.extend(words)
        
        word_counts = Counter(all_words)
        common_phrases = [word for word, count in word_counts.most_common(10) if count > 1]
        
        # Common structures analysis
        structures = []
        for prompt in existing_prompts:
            if prompt.startswith("Be "):
                structures.append("Be + adjective")
            elif "?" in prompt:
                structures.append("Question format")
            elif "help" in prompt.lower():
                structures.append("Help-focused")
            elif "guide" in prompt.lower():
                structures.append("Guide-focused")
        
        structure_counts = Counter(structures)
        common_structures = [struct for struct, count in structure_counts.most_common(5) if count > 1]
        
        # Common approaches analysis
        approaches = []
        for prompt in existing_prompts:
            if "practical" in prompt.lower():
                approaches.append("practical")
            if "supportive" in prompt.lower():
                approaches.append("supportive")
            if "confidence" in prompt.lower():
                approaches.append("confidence")
            if "social" in prompt.lower():
                approaches.append("social")
        
        approach_counts = Counter(approaches)
        common_approaches = [approach for approach, count in approach_counts.most_common(5) if count > 1]
        
        return {
            'common_phrases': common_phrases,
            'common_structures': common_structures,
            'common_approaches': common_approaches,
            'total_prompts': len(existing_prompts)
        }
    
    def calculate_performance_diversity_score(self, child_text: str, parent1_profile: ParentPerformanceProfile, 
                                            parent2_profile: ParentPerformanceProfile, 
                                            existing_prompts: List[str]) -> Dict[str, float]:
        """Calculate both performance and diversity scores for the child"""
        
        # Performance score: how well it preserves parent performance patterns
        performance_score = self._calculate_performance_score(child_text, parent1_profile, parent2_profile)
        
        # Diversity score: how different it is from existing prompts
        diversity_score = self._calculate_diversity_score(child_text, existing_prompts)
        
        # Combined score: weighted average
        combined_score = 0.6 * performance_score + 0.4 * diversity_score
        
        return {
            'performance_score': performance_score,
            'diversity_score': diversity_score,
            'combined_score': combined_score
        }
    
    def _calculate_performance_score(self, child_text: str, parent1_profile: ParentPerformanceProfile, 
                                   parent2_profile: ParentPerformanceProfile) -> float:
        """Calculate how well the child preserves parent performance patterns"""
        
        child_lower = child_text.lower()
        
        # Check if child contains characteristics that contributed to parent success
        p1_characteristics = parent1_profile.performance_pattern['contributing_characteristics']
        p2_characteristics = parent2_profile.performance_pattern['contributing_characteristics']
        
        # Map characteristics to text indicators
        characteristic_indicators = {
            'questioning_approach': ['?', 'what', 'how', 'why', 'which', 'ask'],
            'supportive_approach': ['supportive', 'encouraging', 'helpful', 'patient', 'gentle'],
            'practical_approach': ['practical', 'step', 'action', 'concrete', 'specific'],
            'collaborative_approach': ['together', 'we', 'us', 'let\'s', 'guide', 'mentor'],
            'confidence_focused': ['confidence', 'believe', 'assurance', 'self-esteem', 'strength'],
            'empathy_focused': ['empathy', 'understand', 'feel', 'emotion', 'listen'],
            'feedback_focused': ['feedback', 'constructive', 'improve', 'develop', 'grow']
        }
        
        # Calculate preservation of parent 1 characteristics
        p1_preservation = 0
        for char in p1_characteristics:
            if char in characteristic_indicators:
                indicators = characteristic_indicators[char]
                if any(indicator in child_lower for indicator in indicators):
                    p1_preservation += 1
        p1_preservation = p1_preservation / len(p1_characteristics) if p1_characteristics else 0
        
        # Calculate preservation of parent 2 characteristics
        p2_preservation = 0
        for char in p2_characteristics:
            if char in characteristic_indicators:
                indicators = characteristic_indicators[char]
                if any(indicator in child_lower for indicator in indicators):
                    p2_preservation += 1
        p2_preservation = p2_preservation / len(p2_characteristics) if p2_characteristics else 0
        
        # Calculate style preservation
        style_preservation = self._calculate_style_preservation(child_text, parent1_profile, parent2_profile)
        
        # Combined performance score
        performance_score = (p1_preservation + p2_preservation + style_preservation) / 3
        
        return min(performance_score, 1.0)  # Cap at 1.0
    
    def _calculate_style_preservation(self, child_text: str, parent1_profile: ParentPerformanceProfile, 
                                    parent2_profile: ParentPerformanceProfile) -> float:
        """Calculate how well the child preserves parent style characteristics"""
        
        # Create dummy criterion scores for child analysis
        child_criterion_scores = []
        for criterion in self.criteria_names:
            child_criterion_scores.append((criterion, 0.0))  # Dummy scores for analysis
        
        child_approach = self._analyze_performance_pattern(child_text, child_criterion_scores)
        
        # Compare with parent approaches
        p1_approach_match = 1.0 if child_approach['dominant_approach'] == parent1_profile.performance_pattern['dominant_approach'] else 0.5
        p2_approach_match = 1.0 if child_approach['dominant_approach'] == parent2_profile.performance_pattern['dominant_approach'] else 0.5
        
        # Check structure preservation
        structure_match = 0
        structure_elements = ['has_question', 'has_action_verb', 'has_qualifier', 'is_directive', 'is_collaborative']
        for element in structure_elements:
            if child_approach['structure_analysis'][element] == parent1_profile.performance_pattern['structure_analysis'][element]:
                structure_match += 1
        structure_match /= len(structure_elements)
        
        return (p1_approach_match + p2_approach_match + structure_match) / 3
    
    def _calculate_diversity_score(self, child_text: str, existing_prompts: List[str]) -> float:
        """Calculate how different the child is from existing prompts"""
        
        if not existing_prompts:
            return 1.0  # Perfect diversity if no existing prompts
        
        # Calculate similarity to each existing prompt
        similarities = []
        for existing_prompt in existing_prompts:
            similarity = self._calculate_text_similarity(child_text, existing_prompt)
            similarities.append(similarity)
        
        # Diversity = 1 - average_similarity
        avg_similarity = sum(similarities) / len(similarities)
        diversity_score = 1.0 - avg_similarity
        
        return max(diversity_score, 0.0)  # Ensure non-negative
    
    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Calculate semantic similarity between two texts using word overlap"""
        words1 = set(re.findall(r'\b\w+\b', text1.lower()))
        words2 = set(re.findall(r'\b\w+\b', text2.lower()))
        
        if not words1 and not words2:
            return 1.0
        if not words1 or not words2:
            return 0.0
            
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        return intersection / union if union > 0 else 0.0

# Example usage and testing
if __name__ == "__main__":
    # Test the corrected enhanced crossover
    crossover = CorrectedEnhancedCrossover()
    
    # Example parent performance profiles based on actual assessment results
    parent1_profile = ParentPerformanceProfile(
        prompt_text="Be supportive and provide practical, confidence-building advice",
        performance_metrics={
            'improvement_build_confidence': 0.85,
            'improvement_show_empathy': 0.78,
            'improvement_provide_feedback': 0.72,
            'improvement_encourage_participation': 0.68,
            'improvement_ask_for_help': 0.45,
            'avg_improvement': 0.65
        },
        top_performing_criteria=[('build_confidence', 0.85), ('show_empathy', 0.78), ('provide_feedback', 0.72)],
        weak_criteria=[('ask_for_help', 0.45)],
        performance_pattern={
            'top_3_criteria': ['build_confidence', 'show_empathy', 'provide_feedback'],
            'contributing_characteristics': ['supportive_approach', 'confidence_focused', 'feedback_focused'],
            'dominant_approach': 'supportive_approach'
        },
        generation=2,
        length=67
    )
    
    parent2_profile = ParentPerformanceProfile(
        prompt_text="Guide students through social challenges with empathy and practical strategies",
        performance_metrics={
            'improvement_show_empathy': 0.92,
            'improvement_guide': 0.88,
            'improvement_handle_conflict': 0.85,
            'improvement_foster_connection': 0.82,
            'improvement_ask_for_help': 0.78,
            'avg_improvement': 0.80
        },
        top_performing_criteria=[('show_empathy', 0.92), ('guide', 0.88), ('handle_conflict', 0.85)],
        weak_criteria=[('build_confidence', 0.70)],
        performance_pattern={
            'top_3_criteria': ['show_empathy', 'guide', 'handle_conflict'],
            'contributing_characteristics': ['collaborative_approach', 'empathy_focused', 'practical_approach'],
            'dominant_approach': 'collaborative_approach'
        },
        generation=2,
        length=78
    )
    
    existing_prompts = [
        "Be supportive and provide practical, confidence-building advice",
        "Be supportive and provide practical, growth-oriented advice"
    ]
    
    # Create corrected crossover prompt
    prompt = crossover.create_performance_diversity_crossover_prompt(
        parent1_profile, parent2_profile, existing_prompts
    )
    
    print("Corrected Enhanced Crossover Prompt:")
    print(prompt)
