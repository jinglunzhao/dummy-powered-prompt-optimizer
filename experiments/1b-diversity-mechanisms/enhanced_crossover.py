#!/usr/bin/env python3
"""
Enhanced Crossover: Performance + Diversity Balance
==================================================

This module implements a hybrid approach that:
1. Preserves parent performance strengths
2. Encourages diversity and uniqueness
3. Balances both objectives optimally

Key strategies:
- Performance-weighted crossover
- Diversity-aware generation
- Strength preservation mechanisms
- Multi-objective optimization
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
class ParentAnalysis:
    """Analysis of parent prompt strengths and characteristics"""
    prompt_text: str
    performance_metrics: Dict[str, float]
    strengths: List[Tuple[str, float]]  # (criterion, score)
    weaknesses: List[Tuple[str, float]]
    style_characteristics: Dict[str, Any]
    length: int
    generation: int

class EnhancedCrossover:
    """Enhanced crossover that balances performance and diversity"""
    
    def __init__(self):
        self.criteria_names = [
            "ask_for_help", "stay_calm", "listen_actively", "express_clearly", "show_empathy",
            "ask_clarifying", "give_constructive", "handle_conflict", "build_confidence", "encourage_participation",
            "respect_boundaries", "offer_support", "celebrate_success", "address_concerns", "foster_connection",
            "model_behavior", "provide_feedback", "create_safety", "promote_growth", "maintain_balance"
        ]
    
    def analyze_parent(self, prompt_text: str, performance_metrics: Dict[str, float], generation: int) -> ParentAnalysis:
        """Analyze a parent prompt to extract its strengths and characteristics"""
        
        # Extract performance data
        criterion_scores = []
        for criterion in self.criteria_names:
            score = performance_metrics.get(f'improvement_{criterion}', 0)
            criterion_scores.append((criterion, score))
        
        # Sort by performance to identify strengths and weaknesses
        criterion_scores.sort(key=lambda x: x[1], reverse=True)
        strengths = criterion_scores[:5]  # Top 5 strengths
        weaknesses = criterion_scores[-3:]  # Bottom 3 weaknesses
        
        # Analyze style characteristics
        style_characteristics = self._analyze_style_characteristics(prompt_text)
        
        return ParentAnalysis(
            prompt_text=prompt_text,
            performance_metrics=performance_metrics,
            strengths=strengths,
            weaknesses=weaknesses,
            style_characteristics=style_characteristics,
            length=len(prompt_text),
            generation=generation
        )
    
    def _analyze_style_characteristics(self, prompt_text: str) -> Dict[str, Any]:
        """Analyze the style characteristics of a prompt"""
        
        # Tone analysis
        encouraging_words = ['supportive', 'encouraging', 'helpful', 'patient', 'gentle']
        direct_words = ['direct', 'clear', 'specific', 'focused', 'precise']
        collaborative_words = ['together', 'we', 'us', 'let\'s', 'guide', 'mentor']
        
        tone_score = {
            'encouraging': sum(1 for word in encouraging_words if word in prompt_text.lower()),
            'direct': sum(1 for word in direct_words if word in prompt_text.lower()),
            'collaborative': sum(1 for word in collaborative_words if word in prompt_text.lower())
        }
        
        # Structure analysis
        has_question = '?' in prompt_text
        has_action_verb = any(word in prompt_text.lower() for word in ['help', 'guide', 'support', 'provide', 'offer'])
        has_qualifier = any(word in prompt_text.lower() for word in ['practical', 'step-by-step', 'constructive', 'effective'])
        
        # Approach analysis
        approach_keywords = {
            'practical': ['practical', 'step-by-step', 'actionable', 'concrete'],
            'emotional': ['empathy', 'understanding', 'feelings', 'emotional'],
            'social': ['social', 'interaction', 'communication', 'relationship'],
            'confidence': ['confidence', 'self-esteem', 'belief', 'assurance']
        }
        
        approach_scores = {}
        for approach, keywords in approach_keywords.items():
            approach_scores[approach] = sum(1 for keyword in keywords if keyword in prompt_text.lower())
        
        return {
            'tone': tone_score,
            'structure': {
                'has_question': has_question,
                'has_action_verb': has_action_verb,
                'has_qualifier': has_qualifier
            },
            'approaches': approach_scores,
            'dominant_tone': max(tone_score, key=tone_score.get) if tone_score else 'encouraging',
            'dominant_approach': max(approach_scores, key=approach_scores.get) if approach_scores else 'practical'
        }
    
    def create_performance_diversity_crossover_prompt(self, parent1_analysis: ParentAnalysis, 
                                                    parent2_analysis: ParentAnalysis,
                                                    existing_prompts: List[str],
                                                    diversity_weight: float = 0.7) -> str:
        """Create a crossover prompt that balances performance and diversity"""
        
        # Analyze existing population for diversity
        existing_patterns = self._analyze_existing_patterns(existing_prompts)
        
        # Create performance-focused instructions
        performance_instructions = self._create_performance_instructions(parent1_analysis, parent2_analysis)
        
        # Create diversity-focused instructions
        diversity_instructions = self._create_diversity_instructions(existing_patterns, diversity_weight)
        
        # Combine both approaches
        crossover_prompt = f"""
You are an expert prompt engineer creating a SYSTEM PROMPT for an AI social skills coach that EXCELLS in both performance and diversity.

PARENT 1 SYSTEM PROMPT: "{parent1_analysis.prompt_text}"
PARENT 1 STRENGTHS: {', '.join([f"{criterion}: {score:.3f}" for criterion, score in parent1_analysis.strengths[:3]])}
PARENT 1 STYLE: {parent1_analysis.style_characteristics['dominant_tone']} tone, {parent1_analysis.style_characteristics['dominant_approach']} approach

PARENT 2 SYSTEM PROMPT: "{parent2_analysis.prompt_text}"
PARENT 2 STRENGTHS: {', '.join([f"{criterion}: {score:.3f}" for criterion, score in parent2_analysis.strengths[:3]])}
PARENT 2 STYLE: {parent2_analysis.style_characteristics['dominant_tone']} tone, {parent2_analysis.style_characteristics['dominant_approach']} approach

{performance_instructions}

{diversity_instructions}

SYSTEM PROMPT REQUIREMENTS:
- Create a SYSTEM PROMPT that defines the AI's role and behavior (not a conversation starter)
- Use "You are..." or "I am..." format to define the AI's identity
- Specify how the AI should behave and what approach to take
- Preserve the BEST performing elements from both parents
- Create a UNIQUE approach that differs from existing patterns
- Target length: {max(parent1_analysis.length, parent2_analysis.length)} characters (±20%)

EXAMPLES of good SYSTEM PROMPTS:
- "You are a supportive social skills coach who provides practical, confidence-building guidance to students."
- "I am a peer mentor who helps students develop social skills through empathy and step-by-step practice."
- "You are a social skills guide who uses storytelling and emotional intelligence to help students overcome social challenges."

EXAMPLES of BAD outputs (conversation starters, not system prompts):
- "What social challenges are you facing? Let's work through them together"
- "How can I help you build confidence today?"
- "Let's explore your social skills together"

CRITICAL: Generate a SYSTEM PROMPT that defines the AI's role, not a conversation starter. Use "You are..." or "I am..." format.

Respond with ONLY the system prompt text, no explanations.
"""
        
        return crossover_prompt
    
    def _create_performance_instructions(self, parent1_analysis: ParentAnalysis, parent2_analysis: ParentAnalysis) -> str:
        """Create performance-focused instructions based on parent strengths"""
        
        # Identify complementary strengths
        parent1_strengths = [criterion for criterion, score in parent1_analysis.strengths[:3]]
        parent2_strengths = [criterion for criterion, score in parent2_analysis.strengths[:3]]
        
        # Find unique strengths from each parent
        unique_p1_strengths = [s for s in parent1_strengths if s not in parent2_strengths]
        unique_p2_strengths = [s for s in parent2_strengths if s not in parent1_strengths]
        shared_strengths = [s for s in parent1_strengths if s in parent2_strengths]
        
        performance_instructions = f"""
PERFORMANCE PRESERVATION:
- Parent 1 excels at: {', '.join(unique_p1_strengths) if unique_p1_strengths else 'general effectiveness'}
- Parent 2 excels at: {', '.join(unique_p2_strengths) if unique_p2_strengths else 'general effectiveness'}
- Both excel at: {', '.join(shared_strengths) if shared_strengths else 'general effectiveness'}

REQUIREMENT: The child must maintain or improve these performance strengths while being unique.
"""
        
        return performance_instructions
    
    def _create_diversity_instructions(self, existing_patterns: Dict[str, Any], diversity_weight: float) -> str:
        """Create diversity-focused instructions based on existing patterns"""
        
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
    
    def calculate_performance_diversity_score(self, child_text: str, parent1_analysis: ParentAnalysis, 
                                            parent2_analysis: ParentAnalysis, 
                                            existing_prompts: List[str]) -> Dict[str, float]:
        """Calculate both performance and diversity scores for the child"""
        
        # Performance score: how well it preserves parent strengths
        performance_score = self._calculate_performance_score(child_text, parent1_analysis, parent2_analysis)
        
        # Diversity score: how different it is from existing prompts
        diversity_score = self._calculate_diversity_score(child_text, existing_prompts)
        
        # Combined score: weighted average
        combined_score = 0.6 * performance_score + 0.4 * diversity_score
        
        return {
            'performance_score': performance_score,
            'diversity_score': diversity_score,
            'combined_score': combined_score
        }
    
    def _calculate_performance_score(self, child_text: str, parent1_analysis: ParentAnalysis, 
                                   parent2_analysis: ParentAnalysis) -> float:
        """Calculate how well the child preserves parent performance strengths"""
        
        # Check if child contains elements from parent strengths
        parent1_strength_words = self._extract_strength_keywords(parent1_analysis)
        parent2_strength_words = self._extract_strength_keywords(parent2_analysis)
        
        child_lower = child_text.lower()
        
        # Calculate preservation of parent 1 strengths
        p1_preservation = sum(1 for word in parent1_strength_words if word in child_lower) / len(parent1_strength_words) if parent1_strength_words else 0
        
        # Calculate preservation of parent 2 strengths
        p2_preservation = sum(1 for word in parent2_strength_words if word in child_lower) / len(parent2_strength_words) if parent2_strength_words else 0
        
        # Calculate style preservation
        style_preservation = self._calculate_style_preservation(child_text, parent1_analysis, parent2_analysis)
        
        # Combined performance score
        performance_score = (p1_preservation + p2_preservation + style_preservation) / 3
        
        return min(performance_score, 1.0)  # Cap at 1.0
    
    def _extract_strength_keywords(self, parent_analysis: ParentAnalysis) -> List[str]:
        """Extract keywords related to parent strengths"""
        
        strength_keywords = {
            'ask_for_help': ['help', 'ask', 'question', 'clarify'],
            'stay_calm': ['calm', 'patient', 'gentle', 'peaceful'],
            'listen_actively': ['listen', 'hear', 'attention', 'focus'],
            'express_clearly': ['clear', 'express', 'communicate', 'articulate'],
            'show_empathy': ['empathy', 'understand', 'feel', 'emotion'],
            'build_confidence': ['confidence', 'believe', 'assurance', 'self-esteem'],
            'encourage_participation': ['encourage', 'participate', 'engage', 'involve'],
            'provide_feedback': ['feedback', 'constructive', 'improve', 'develop']
        }
        
        keywords = []
        for criterion, score in parent_analysis.strengths[:3]:  # Top 3 strengths
            if criterion in strength_keywords:
                keywords.extend(strength_keywords[criterion])
        
        return keywords
    
    def _calculate_style_preservation(self, child_text: str, parent1_analysis: ParentAnalysis, 
                                    parent2_analysis: ParentAnalysis) -> float:
        """Calculate how well the child preserves parent style characteristics"""
        
        child_style = self._analyze_style_characteristics(child_text)
        
        # Compare with parent styles
        p1_style_match = self._compare_styles(child_style, parent1_analysis.style_characteristics)
        p2_style_match = self._compare_styles(child_style, parent2_analysis.style_characteristics)
        
        # Return average style preservation
        return (p1_style_match + p2_style_match) / 2
    
    def _compare_styles(self, style1: Dict[str, Any], style2: Dict[str, Any]) -> float:
        """Compare two style characteristics and return similarity score"""
        
        # Compare dominant tone
        tone1 = style1.get('dominant_tone', 'encouraging')
        tone2 = style2.get('dominant_tone', 'encouraging')
        tone_match = 1.0 if tone1 == tone2 else 0.5
        
        # Compare dominant approach
        approach1 = style1.get('dominant_approach', 'practical')
        approach2 = style2.get('dominant_approach', 'practical')
        approach_match = 1.0 if approach1 == approach2 else 0.5
        
        # Compare structure elements
        structure_match = 0
        structure_elements = ['has_question', 'has_action_verb', 'has_qualifier']
        structure1 = style1.get('structure', {})
        structure2 = style2.get('structure', {})
        
        for element in structure_elements:
            if structure1.get(element, False) == structure2.get(element, False):
                structure_match += 1
        structure_match /= len(structure_elements)
        
        return (tone_match + approach_match + structure_match) / 3
    
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
    # Test the enhanced crossover
    crossover = EnhancedCrossover()
    
    # Example parent analyses
    parent1_analysis = ParentAnalysis(
        prompt_text="Be supportive and provide practical advice",
        performance_metrics={'improvement_build_confidence': 0.8, 'improvement_show_empathy': 0.7},
        strengths=[('build_confidence', 0.8), ('show_empathy', 0.7)],
        weaknesses=[('ask_clarifying', 0.3)],
        style_characteristics={'dominant_tone': 'encouraging', 'dominant_approach': 'practical'},
        length=45,
        generation=1
    )
    
    parent2_analysis = ParentAnalysis(
        prompt_text="Guide students through social challenges with empathy",
        performance_metrics={'improvement_show_empathy': 0.9, 'improvement_guide': 0.8},
        strengths=[('show_empathy', 0.9), ('guide', 0.8)],
        weaknesses=[('build_confidence', 0.4)],
        style_characteristics={'dominant_tone': 'collaborative', 'dominant_approach': 'emotional'},
        length=55,
        generation=1
    )
    
    existing_prompts = [
        "Be supportive and provide practical advice",
        "Be supportive and provide practical guidance"
    ]
    
    # Create enhanced crossover prompt
    prompt = crossover.create_performance_diversity_crossover_prompt(
        parent1_analysis, parent2_analysis, existing_prompts
    )
    
    print("Enhanced Crossover Prompt:")
    print(prompt)
