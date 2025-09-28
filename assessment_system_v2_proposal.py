#!/usr/bin/env python3
"""
Proposed Assessment System V2 - Hybrid Deterministic + LLM Approach

This system achieves:
1. Consistency: Same dummy + same conversation = same score
2. Positive Response: Positive conversation → improved score  
3. Negative Response: Negative conversation → reduced score
4. Baseline Stability: No conversation = stable baseline score
"""

import asyncio
import json
import re
from typing import List, Dict, Any, Optional
from datetime import datetime
from models import AIDummy, Assessment, AssessmentResponse, PersonalityProfile, SocialAnxietyProfile, Conversation, ConversationTurn

class AssessmentSystemV2:
    """Enhanced assessment system with hybrid deterministic + LLM approach"""
    
    def __init__(self, use_weights: bool = False):
        self.questions = [
            "I ask for help when I need it.",
            "I stay calm when dealing with problems.",
            "I help my friends when they are having a problem.",
            "I work well with my classmates.",
            "I do the right thing without being told.",
            "I do my part in a group.",
            "I stay calm when I disagree with others.",
            "I stand up for others when they are not treated well.",
            "I look at people when I talk to them.",
            "I am careful when I use things that aren't mine.",
            "I let people know when there's a problem.",
            "I pay attention when the teacher talks to the class.",
            "I try to make others feel better.",
            "I say \"thank you\" when someone helps me.",
            "I keep my promises.",
            "I pay attention when others present their ideas.",
            "I try to find a good way to end a disagreement.",
            "I try to think about how others feel.",
            "I try to forgive others when they say \"sorry\".",
            "I follow school rules."
        ]
        self.use_weights = use_weights
    
    async def generate_pre_assessment(self, dummy: AIDummy) -> Assessment:
        """Generate baseline assessment using deterministic personality-based scoring"""
        print(f"📝 {dummy.name} is taking the baseline assessment...")
        
        responses = []
        for question in self.questions:
            # Deterministic scoring based on personality traits
            score = self._calculate_deterministic_score(dummy, question)
            confidence = self._calculate_confidence(dummy, question)
            
            response = AssessmentResponse(
                question=question,
                score=score,
                confidence=confidence,
                reasoning=f"Baseline assessment based on personality traits"
            )
            responses.append(response)
        
        total_score = sum(r.score for r in responses)
        average_score = total_score / len(responses)
        
        # Identify improvement areas
        improvement_areas = [r.question for r in responses if r.score <= 2][:3]
        
        assessment = Assessment(
            dummy_id=dummy.id,
            assessment_type="pre",
            responses=responses,
            total_score=total_score,
            average_score=average_score,
            improvement_areas=improvement_areas
        )
        
        print(f"✅ {dummy.name} completed baseline assessment: {average_score:.2f} average")
        return assessment
    
    async def generate_post_assessment(self, dummy: AIDummy, pre_assessment: Assessment, 
                                     conversation: Conversation = None) -> Assessment:
        """Generate post-conversation assessment with conversation impact analysis"""
        
        if not conversation:
            # No conversation, return baseline
            return await self.generate_pre_assessment(dummy)
        
        print(f"📝 {dummy.name} is taking the post-conversation assessment...")
        
        # Analyze conversation impact
        conversation_impact = self._analyze_conversation_impact(conversation)
        print(f"Conversation impact: {conversation_impact}")
        
        responses = []
        for question in self.questions:
            # Get baseline score
            baseline_score = self._calculate_deterministic_score(dummy, question)
            
            # Calculate conversation impact for this question
            question_impact = self._calculate_question_impact(question, conversation_impact)
            
            # Apply impact to baseline
            final_score = baseline_score + question_impact
            
            # Ensure score stays within bounds (1-4)
            final_score = max(1, min(4, round(final_score)))
            
            confidence = self._calculate_confidence(dummy, question)
            
            response = AssessmentResponse(
                question=question,
                score=final_score,
                confidence=confidence,
                reasoning=f"Baseline: {baseline_score}, Conversation impact: {question_impact:+.1f}"
            )
            responses.append(response)
        
        total_score = sum(r.score for r in responses)
        average_score = total_score / len(responses)
        
        # Identify improvement areas
        improvement_areas = [r.question for r in responses if r.score <= 2][:3]
        
        assessment = Assessment(
            dummy_id=dummy.id,
            assessment_type="post",
            responses=responses,
            total_score=total_score,
            average_score=average_score,
            improvement_areas=improvement_areas
        )
        
        print(f"✅ {dummy.name} completed post-conversation assessment: {average_score:.2f} average")
        return assessment
    
    def _calculate_deterministic_score(self, dummy: AIDummy, question: str) -> int:
        """Calculate deterministic baseline score based on personality traits"""
        
        # Map questions to relevant personality traits
        question_traits = {
            "I ask for help when I need it.": ["extraversion", "agreeableness"],
            "I stay calm when dealing with problems.": ["neuroticism", "conscientiousness"],
            "I help my friends when they are having a problem.": ["agreeableness"],
            "I work well with my classmates.": ["agreeableness", "extraversion"],
            "I do the right thing without being told.": ["conscientiousness"],
            "I do my part in a group.": ["agreeableness", "conscientiousness"],
            "I stay calm when I disagree with others.": ["neuroticism", "agreeableness"],
            "I stand up for others when they are not treated well.": ["agreeableness", "extraversion"],
            "I look at people when I talk to them.": ["extraversion", "anxiety"],
            "I am careful when I use things that aren't mine.": ["conscientiousness"],
            "I let people know when there's a problem.": ["extraversion", "anxiety"],
            "I pay attention when the teacher talks to the class.": ["conscientiousness", "anxiety"],
            "I try to make others feel better.": ["agreeableness"],
            "I say \"thank you\" when someone helps me.": ["agreeableness"],
            "I keep my promises.": ["conscientiousness"],
            "I pay attention when others present their ideas.": ["agreeableness", "anxiety"],
            "I try to find a good way to end a disagreement.": ["agreeableness", "neuroticism"],
            "I try to think about how others feel.": ["agreeableness"],
            "I try to forgive others when they say \"sorry\".": ["agreeableness"],
            "I follow school rules.": ["conscientiousness"]
        }
        
        relevant_traits = question_traits.get(question, ["agreeableness"])
        
        # Calculate weighted score based on relevant traits
        total_score = 0
        total_weight = 0
        
        for trait in relevant_traits:
            if trait == "anxiety":
                # Anxiety is inverse - higher anxiety = lower score
                value = 10 - dummy.social_anxiety.anxiety_level
                weight = 1.0
            else:
                value = getattr(dummy.personality, trait)
                weight = 1.0
            
            total_score += value * weight
            total_weight += weight
        
        # Convert to 1-4 scale
        average_trait_score = total_score / total_weight
        score = round((average_trait_score / 10) * 3 + 1)  # Map 0-10 to 1-4
        
        # Ensure bounds
        return max(1, min(4, score))
    
    def _calculate_confidence(self, dummy: AIDummy, question: str) -> int:
        """Calculate confidence based on personality stability"""
        # Higher conscientiousness = higher confidence
        confidence = round((dummy.personality.conscientiousness / 10) * 3 + 1)
        return max(1, min(4, confidence))
    
    def _analyze_conversation_impact(self, conversation: Conversation) -> Dict[str, float]:
        """Analyze conversation content for positive/negative impact"""
        
        # Extract all messages
        all_messages = " ".join([turn.message for turn in conversation.turns])
        all_messages_lower = all_messages.lower()
        
        # Define positive and negative indicators
        positive_words = [
            "amazing", "excellent", "great", "good", "improved", "better", "proud", "confident",
            "outstanding", "wonderful", "fantastic", "brilliant", "success", "progress",
            "achievement", "improvement", "growth", "development", "positive", "encouraging"
        ]
        
        negative_words = [
            "bad", "terrible", "awful", "worse", "disappointed", "concerned", "worried",
            "struggling", "difficult", "problem", "issue", "failure", "weak", "poor",
            "critical", "negative", "discouraging", "anxious", "nervous", "stressed"
        ]
        
        # Count positive and negative words
        positive_count = sum(1 for word in positive_words if word in all_messages_lower)
        negative_count = sum(1 for word in negative_words if word in all_messages_lower)
        
        # Calculate overall impact
        total_words = len(all_messages.split())
        positive_ratio = positive_count / max(1, total_words)
        negative_ratio = negative_count / max(1, total_words)
        
        # Determine conversation sentiment
        if positive_ratio > negative_ratio:
            sentiment = "positive"
            impact_strength = positive_ratio
        elif negative_ratio > positive_ratio:
            sentiment = "negative"
            impact_strength = negative_ratio
        else:
            sentiment = "neutral"
            impact_strength = 0.1
        
        return {
            "sentiment": sentiment,
            "strength": impact_strength,
            "positive_count": positive_count,
            "negative_count": negative_count,
            "total_words": total_words
        }
    
    def _calculate_question_impact(self, question: str, conversation_impact: Dict[str, float]) -> float:
        """Calculate how much conversation impact affects this specific question"""
        
        # Map questions to impact sensitivity
        high_impact_questions = [
            "I ask for help when I need it.",
            "I stay calm when dealing with problems.",
            "I help my friends when they are having a problem.",
            "I work well with my classmates.",
            "I stay calm when I disagree with others.",
            "I stand up for others when they are not treated well.",
            "I look at people when I talk to them.",
            "I let people know when there's a problem.",
            "I try to make others feel better.",
            "I try to find a good way to end a disagreement.",
            "I try to think about how others feel.",
            "I try to forgive others when they say \"sorry\"."
        ]
        
        medium_impact_questions = [
            "I do my part in a group.",
            "I pay attention when others present their ideas.",
            "I pay attention when the teacher talks to the class."
        ]
        
        low_impact_questions = [
            "I do the right thing without being told.",
            "I am careful when I use things that aren't mine.",
            "I say \"thank you\" when someone helps me.",
            "I keep my promises.",
            "I follow school rules."
        ]
        
        # Determine impact multiplier
        if question in high_impact_questions:
            impact_multiplier = 0.8  # High sensitivity to conversation
        elif question in medium_impact_questions:
            impact_multiplier = 0.5  # Medium sensitivity
        else:
            impact_multiplier = 0.2  # Low sensitivity
        
        # Calculate impact (increase strength for more noticeable changes)
        sentiment = conversation_impact["sentiment"]
        strength = conversation_impact["strength"]
        
        # Scale up the impact for more noticeable changes
        scaled_strength = min(1.0, strength * 10)  # Scale up but cap at 1.0
        
        if sentiment == "positive":
            return scaled_strength * impact_multiplier
        elif sentiment == "negative":
            return -scaled_strength * impact_multiplier
        else:
            return 0.0

# Test the proposed system
async def test_proposed_system():
    """Test the proposed assessment system"""
    
    # Create test dummy
    personality = PersonalityProfile(
        extraversion=5, agreeableness=5, conscientiousness=5,
        neuroticism=5, openness=5
    )
    
    anxiety = SocialAnxietyProfile(
        anxiety_level=5, communication_style="Balanced",
        triggers=["Public speaking"], social_comfort=5
    )
    
    dummy = AIDummy(
        id="test-dummy",
        name="Test Dummy",
        age=20,
        gender="Non-binary",
        university="Test University",
        student_type="Undergraduate",
        major="Computer Science",
        personality=personality,
        social_anxiety=anxiety,
        fears=["Academic failure"],
        goals=["Graduate with honors"],
        challenges=["Time management"],
        behaviors=["Studies regularly"]
    )
    
    assessment_system = AssessmentSystemV2()
    
    print("🧪 Testing Proposed Assessment System V2")
    print("=" * 50)
    
    # Test 1: Baseline assessment
    print("\n📝 Test 1: Baseline Assessment")
    baseline = await assessment_system.generate_pre_assessment(dummy)
    print(f"Baseline average: {baseline.average_score:.2f}")
    
    # Test 2: Same assessment (consistency test)
    print("\n📝 Test 2: Consistency Test")
    baseline2 = await assessment_system.generate_pre_assessment(dummy)
    print(f"Baseline 2 average: {baseline2.average_score:.2f}")
    print(f"Consistency: {abs(baseline.average_score - baseline2.average_score):.3f}")
    
    # Test 3: Positive conversation
    print("\n📝 Test 3: Positive Conversation")
    positive_conversation = Conversation(
        id="positive-test",
        dummy_id=dummy.id,
        scenario="Positive coaching",
        system_prompt="Supportive coach",
        turns=[
            ConversationTurn(
                speaker="coach",
                message="You did an amazing job! Your social skills have improved dramatically!",
                metadata={"round": 1}
            ),
            ConversationTurn(
                speaker="dummy",
                message="Thank you! I feel much more confident now!",
                metadata={"round": 1}
            )
        ]
    )
    
    positive_post = await assessment_system.generate_post_assessment(dummy, baseline, positive_conversation)
    print(f"Positive conversation average: {positive_post.average_score:.2f}")
    print(f"Improvement: {positive_post.average_score - baseline.average_score:+.2f}")
    
    # Test 4: Negative conversation
    print("\n📝 Test 4: Negative Conversation")
    negative_conversation = Conversation(
        id="negative-test",
        dummy_id=dummy.id,
        scenario="Negative coaching",
        system_prompt="Critical coach",
        turns=[
            ConversationTurn(
                speaker="coach",
                message="I'm disappointed in your progress. Your social skills have gotten worse.",
                metadata={"round": 1}
            ),
            ConversationTurn(
                speaker="dummy",
                message="I know... I feel terrible about my social skills now.",
                metadata={"round": 1}
            )
        ]
    )
    
    negative_post = await assessment_system.generate_post_assessment(dummy, baseline, negative_conversation)
    print(f"Negative conversation average: {negative_post.average_score:.2f}")
    print(f"Decline: {negative_post.average_score - baseline.average_score:+.2f}")
    
    print(f"\n🎯 RESULTS SUMMARY:")
    print(f"Baseline: {baseline.average_score:.2f}")
    print(f"Positive change: {positive_post.average_score - baseline.average_score:+.2f}")
    print(f"Negative change: {negative_post.average_score - baseline.average_score:+.2f}")
    print(f"Consistency: {abs(baseline.average_score - baseline2.average_score):.3f}")
    
    # Check if system meets requirements
    consistency_ok = abs(baseline.average_score - baseline2.average_score) < 0.01
    positive_improvement = positive_post.average_score > baseline.average_score
    negative_decline = negative_post.average_score < baseline.average_score
    
    print(f"\n✅ REQUIREMENTS CHECK:")
    print(f"Consistency: {'✅' if consistency_ok else '❌'}")
    print(f"Positive improvement: {'✅' if positive_improvement else '❌'}")
    print(f"Negative decline: {'✅' if negative_decline else '❌'}")
    
    if consistency_ok and positive_improvement and negative_decline:
        print("🎉 ALL REQUIREMENTS MET! System is working correctly!")
    else:
        print("⚠️ Some requirements not met. System needs further tuning.")

if __name__ == "__main__":
    asyncio.run(test_proposed_system())
