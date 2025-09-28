#!/usr/bin/env python3
"""
Assessment System V3 - Quantitative Conversation Effectiveness Measurement

This system measures the quantitative impact of conversation on dummy's social skills:
1. Consistency: Same dummy + same conversation = same score
2. Quantitative Response: Conversation effectiveness → proportional score change
3. Effectiveness Measurement: Measures HOW MUCH the conversation helped/hurt
4. Baseline Stability: No conversation = stable baseline score
"""

import asyncio
import json
import re
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from models import AIDummy, Assessment, AssessmentResponse, PersonalityProfile, SocialAnxietyProfile, Conversation, ConversationTurn

class AssessmentSystemV3:
    """Quantitative conversation effectiveness measurement system"""
    
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
        
        # Define social skills categories for targeted effectiveness measurement
        self.skill_categories = {
            "communication": [
                "I ask for help when I need it.",
                "I let people know when there's a problem.",
                "I look at people when I talk to them.",
                "I pay attention when others present their ideas.",
                "I pay attention when the teacher talks to the class."
            ],
            "emotional_regulation": [
                "I stay calm when dealing with problems.",
                "I stay calm when I disagree with others.",
                "I try to find a good way to end a disagreement."
            ],
            "empathy_support": [
                "I help my friends when they are having a problem.",
                "I stand up for others when they are not treated well.",
                "I try to make others feel better.",
                "I try to think about how others feel.",
                "I try to forgive others when they say \"sorry\"."
            ],
            "cooperation_responsibility": [
                "I work well with my classmates.",
                "I do my part in a group.",
                "I say \"thank you\" when someone helps me.",
                "I keep my promises.",
                "I follow school rules.",
                "I do the right thing without being told.",
                "I am careful when I use things that aren't mine."
            ]
        }
    
    async def generate_pre_assessment(self, dummy: AIDummy) -> Assessment:
        """Generate baseline assessment using deterministic personality-based scoring"""
        print(f"📝 {dummy.name} is taking the baseline assessment...")
        
        responses = []
        for question in self.questions:
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
        """Generate post-conversation assessment with quantitative effectiveness measurement"""
        
        if not conversation:
            return await self.generate_pre_assessment(dummy)
        
        print(f"📝 {dummy.name} is taking the post-conversation assessment...")
        
        # Measure quantitative conversation effectiveness
        effectiveness_scores = self._measure_conversation_effectiveness(conversation)
        print(f"Conversation effectiveness: {effectiveness_scores}")
        
        responses = []
        for question in self.questions:
            # Get baseline score
            baseline_score = self._calculate_deterministic_score(dummy, question)
            
            # Calculate quantitative impact for this specific question
            question_impact = self._calculate_quantitative_impact(
                question, effectiveness_scores, dummy, conversation
            )
            
            # Apply impact to baseline
            final_score = baseline_score + question_impact
            
            # Ensure score stays within bounds (1-4) and convert to integer
            final_score = max(1, min(4, round(final_score)))
            
            confidence = self._calculate_confidence(dummy, question)
            
            response = AssessmentResponse(
                question=question,
                score=final_score,
                confidence=confidence,
                reasoning=f"Baseline: {baseline_score:.1f}, Effectiveness impact: {question_impact:+.2f}"
            )
            responses.append(response)
        
        total_score = sum(r.score for r in responses)
        average_score = total_score / len(responses)
        
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
    
    def _calculate_deterministic_score(self, dummy: AIDummy, question: str) -> float:
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
        
        # Convert to 1-4 scale with decimal precision
        average_trait_score = total_score / total_weight
        score = (average_trait_score / 10) * 3 + 1  # Map 0-10 to 1-4
        
        # Ensure bounds and return as integer
        return max(1, min(4, round(score)))
    
    def _calculate_confidence(self, dummy: AIDummy, question: str) -> int:
        """Calculate confidence based on personality stability"""
        confidence = round((dummy.personality.conscientiousness / 10) * 3 + 1)
        return max(1, min(4, confidence))
    
    def _measure_conversation_effectiveness(self, conversation: Conversation) -> Dict[str, float]:
        """Measure quantitative effectiveness of conversation across skill categories"""
        
        # Extract all messages
        all_messages = " ".join([turn.message for turn in conversation.turns])
        
        effectiveness_scores = {}
        
        for category, questions in self.skill_categories.items():
            effectiveness_scores[category] = self._measure_category_effectiveness(
                category, all_messages, questions
            )
        
        # Calculate overall effectiveness
        effectiveness_scores["overall"] = sum(effectiveness_scores.values()) / len(effectiveness_scores)
        
        return effectiveness_scores
    
    def _measure_category_effectiveness(self, category: str, messages: str, questions: List[str]) -> float:
        """Measure effectiveness for a specific skill category"""
        
        messages_lower = messages.lower()
        
        # Define category-specific effectiveness indicators
        category_indicators = {
            "communication": {
                "positive": [
                    "confident", "clear", "articulate", "expressive", "outgoing", "talkative",
                    "eye contact", "listening", "asking questions", "speaking up", "communicating",
                    "voice", "presentation", "explanation", "discussion", "conversation"
                ],
                "negative": [
                    "quiet", "shy", "mumbling", "avoiding", "not speaking", "withdrawn",
                    "poor communication", "unclear", "inarticulate", "tongue-tied"
                ],
                "coaching_quality": [
                    "practice", "technique", "skill", "improvement", "development",
                    "training", "guidance", "feedback", "advice", "tip", "strategy"
                ]
            },
            "emotional_regulation": {
                "positive": [
                    "calm", "relaxed", "composed", "controlled", "stable", "balanced",
                    "managing emotions", "self-control", "patience", "tolerance"
                ],
                "negative": [
                    "angry", "upset", "frustrated", "stressed", "anxious", "panicked",
                    "out of control", "emotional", "reactive", "volatile"
                ],
                "coaching_quality": [
                    "breathing", "mindfulness", "relaxation", "coping", "stress management",
                    "emotional intelligence", "self-awareness", "regulation"
                ]
            },
            "empathy_support": {
                "positive": [
                    "helpful", "supportive", "caring", "kind", "compassionate", "understanding",
                    "empathetic", "considerate", "thoughtful", "generous", "forgiving"
                ],
                "negative": [
                    "selfish", "uncaring", "insensitive", "harsh", "critical", "judgmental",
                    "mean", "unkind", "unsupportive", "cold"
                ],
                "coaching_quality": [
                    "perspective-taking", "understanding others", "emotional support",
                    "helping skills", "relationship building", "social connection"
                ]
            },
            "cooperation_responsibility": {
                "positive": [
                    "responsible", "reliable", "dependable", "organized", "disciplined",
                    "teamwork", "cooperation", "collaboration", "contributing", "helpful"
                ],
                "negative": [
                    "irresponsible", "unreliable", "lazy", "disorganized", "undisciplined",
                    "uncooperative", "selfish", "unhelpful", "negligent"
                ],
                "coaching_quality": [
                    "organization", "planning", "goal-setting", "responsibility", "accountability",
                    "teamwork skills", "leadership", "initiative"
                ]
            }
        }
        
        indicators = category_indicators.get(category, {"positive": [], "negative": [], "coaching_quality": []})
        
        # Count effectiveness indicators
        positive_count = sum(1 for word in indicators["positive"] if word in messages_lower)
        negative_count = sum(1 for word in indicators["negative"] if word in messages_lower)
        coaching_quality_count = sum(1 for word in indicators["coaching_quality"] if word in messages_lower)
        
        # Calculate effectiveness score
        total_words = len(messages.split())
        
        # Base effectiveness from positive/negative indicators
        if total_words > 0:
            positive_ratio = positive_count / total_words
            negative_ratio = negative_count / total_words
            coaching_ratio = coaching_quality_count / total_words
            
            # Calculate effectiveness (positive impact minus negative impact, plus coaching quality)
            effectiveness = (positive_ratio - negative_ratio) * 20 + coaching_ratio * 10  # Increased multipliers
            
            # Normalize to reasonable range (-3.0 to +3.0) for more dramatic negative impact
            effectiveness = max(-3.0, min(3.0, effectiveness))
        else:
            effectiveness = 0.0
        
        return round(effectiveness, 2)
    
    def _calculate_quantitative_impact(self, question: str, effectiveness_scores: Dict[str, float], 
                                     dummy: AIDummy, conversation: Conversation) -> float:
        """Calculate quantitative impact for a specific question based on conversation effectiveness"""
        
        # Determine which category this question belongs to
        question_category = None
        for category, questions in self.skill_categories.items():
            if question in questions:
                question_category = category
                break
        
        if not question_category:
            question_category = "cooperation_responsibility"  # Default fallback
        
        # Get category-specific effectiveness
        category_effectiveness = effectiveness_scores.get(question_category, 0.0)
        
        # Calculate question-specific impact multiplier based on personality
        impact_multiplier = self._calculate_question_sensitivity(question, dummy)
        
        # Apply personality-based sensitivity
        final_impact = category_effectiveness * impact_multiplier
        
        # Add some randomness based on conversation length and complexity
        conversation_complexity = len(conversation.turns) / 10.0  # Normalize by typical conversation length
        complexity_multiplier = 1.0 + (conversation_complexity - 0.5) * 0.2  # ±10% based on complexity
        
        final_impact *= complexity_multiplier
        
        return round(final_impact, 2)
    
    def _calculate_question_sensitivity(self, question: str, dummy: AIDummy) -> float:
        """Calculate how sensitive this question is to conversation impact based on dummy's personality"""
        
        # Base sensitivity by question type
        high_sensitivity_questions = [
            "I ask for help when I need it.",
            "I stay calm when dealing with problems.",
            "I work well with my classmates.",
            "I stay calm when I disagree with others.",
            "I look at people when I talk to them.",
            "I let people know when there's a problem.",
            "I try to make others feel better.",
            "I try to find a good way to end a disagreement.",
            "I try to think about how others feel."
        ]
        
        medium_sensitivity_questions = [
            "I help my friends when they are having a problem.",
            "I do my part in a group.",
            "I stand up for others when they are not treated well.",
            "I pay attention when others present their ideas.",
            "I pay attention when the teacher talks to the class.",
            "I try to forgive others when they say \"sorry\"."
        ]
        
        # Determine base sensitivity (increased for more noticeable impact)
        if question in high_sensitivity_questions:
            base_sensitivity = 2.0  # High sensitivity to conversation
        elif question in medium_sensitivity_questions:
            base_sensitivity = 1.5  # Medium sensitivity
        else:
            base_sensitivity = 1.0  # Low sensitivity
        
        # Adjust sensitivity based on personality traits
        # Higher openness = more responsive to coaching
        openness_multiplier = 1.0 + (dummy.personality.openness - 5) * 0.1
        
        # Higher neuroticism = more responsive to emotional coaching
        neuroticism_multiplier = 1.0 + (dummy.personality.neuroticism - 5) * 0.05
        
        # Lower anxiety = more responsive to social coaching
        anxiety_multiplier = 1.0 + (5 - dummy.social_anxiety.anxiety_level) * 0.05
        
        final_sensitivity = base_sensitivity * openness_multiplier * neuroticism_multiplier * anxiety_multiplier
        
        return round(final_sensitivity, 2)

# Test the quantitative system
async def test_quantitative_system():
    """Test the quantitative conversation effectiveness measurement system"""
    
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
    
    assessment_system = AssessmentSystemV3()
    
    print("🧪 Testing Quantitative Conversation Effectiveness System V3")
    print("=" * 70)
    
    # Test 1: Baseline assessment
    print("\n📝 Test 1: Baseline Assessment")
    baseline = await assessment_system.generate_pre_assessment(dummy)
    print(f"Baseline average: {baseline.average_score:.2f}")
    
    # Test 2: Consistency test
    print("\n📝 Test 2: Consistency Test")
    baseline2 = await assessment_system.generate_pre_assessment(dummy)
    print(f"Baseline 2 average: {baseline2.average_score:.2f}")
    print(f"Consistency: {abs(baseline.average_score - baseline2.average_score):.3f}")
    
    # Test 3: High effectiveness conversation
    print("\n📝 Test 3: High Effectiveness Conversation")
    high_effectiveness_conversation = Conversation(
        id="high-effectiveness-test",
        dummy_id=dummy.id,
        scenario="High effectiveness coaching",
        system_prompt="Expert social skills coach",
        turns=[
            ConversationTurn(
                speaker="coach",
                message="You've made incredible progress in your communication skills! Your confidence has improved dramatically, and you're now much more articulate and expressive. I've noticed you're making excellent eye contact and asking thoughtful questions. Your emotional regulation has also improved - you stay calm and composed even in difficult situations.",
                metadata={"round": 1}
            ),
            ConversationTurn(
                speaker="dummy",
                message="Thank you! I do feel much more confident and relaxed now. The breathing techniques you taught me really help me stay calm, and I'm finding it easier to express myself clearly.",
                metadata={"round": 1}
            ),
            ConversationTurn(
                speaker="coach",
                message="Exactly! And I can see how much more empathetic and supportive you've become. You're now helping others feel better and thinking about how they feel. Your teamwork and cooperation skills have also developed significantly. You're becoming a natural leader!",
                metadata={"round": 2}
            ),
            ConversationTurn(
                speaker="dummy",
                message="I'm really proud of my progress! I feel like I can now handle social situations with confidence and help others too. Thank you for all your guidance and support.",
                metadata={"round": 2}
            )
        ]
    )
    
    high_effectiveness_post = await assessment_system.generate_post_assessment(dummy, baseline, high_effectiveness_conversation)
    print(f"High effectiveness average: {high_effectiveness_post.average_score:.2f}")
    print(f"Improvement: {high_effectiveness_post.average_score - baseline.average_score:+.2f}")
    
    # Test 4: Low effectiveness conversation
    print("\n📝 Test 4: Low Effectiveness Conversation")
    low_effectiveness_conversation = Conversation(
        id="low-effectiveness-test",
        dummy_id=dummy.id,
        scenario="Low effectiveness coaching",
        system_prompt="Ineffective coach",
        turns=[
            ConversationTurn(
                speaker="coach",
                message="I'm not sure what to tell you. Maybe you should just try harder to be more social. I don't really have any specific advice for you.",
                metadata={"round": 1}
            ),
            ConversationTurn(
                speaker="dummy",
                message="I don't understand what you mean. Can you be more specific?",
                metadata={"round": 1}
            ),
            ConversationTurn(
                speaker="coach",
                message="Well, you know, just... be better at talking to people. That's all I can say.",
                metadata={"round": 2}
            ),
            ConversationTurn(
                speaker="dummy",
                message="I'm still confused. This isn't very helpful.",
                metadata={"round": 2}
            )
        ]
    )
    
    low_effectiveness_post = await assessment_system.generate_post_assessment(dummy, baseline, low_effectiveness_conversation)
    print(f"Low effectiveness average: {low_effectiveness_post.average_score:.2f}")
    print(f"Change: {low_effectiveness_post.average_score - baseline.average_score:+.2f}")
    
    # Test 5: Negative effectiveness conversation
    print("\n📝 Test 5: Negative Effectiveness Conversation")
    negative_effectiveness_conversation = Conversation(
        id="negative-effectiveness-test",
        dummy_id=dummy.id,
        scenario="Negative effectiveness coaching",
        system_prompt="Damaging coach",
        turns=[
            ConversationTurn(
                speaker="coach",
                message="I'm really disappointed in your social skills. You're terrible at communication, you're always anxious and stressed, and you're completely unhelpful to others. You're selfish and uncooperative, and frankly, I don't think you'll ever improve.",
                metadata={"round": 1}
            ),
            ConversationTurn(
                speaker="dummy",
                message="I feel terrible about myself now. I guess I'm just not good at socializing.",
                metadata={"round": 1}
            ),
            ConversationTurn(
                speaker="coach",
                message="Exactly! You're hopeless. You should just avoid social situations altogether since you're so bad at them.",
                metadata={"round": 2}
            ),
            ConversationTurn(
                speaker="dummy",
                message="You're right... I should just give up. I'm never going to be good at this.",
                metadata={"round": 2}
            )
        ]
    )
    
    negative_effectiveness_post = await assessment_system.generate_post_assessment(dummy, baseline, negative_effectiveness_conversation)
    print(f"Negative effectiveness average: {negative_effectiveness_post.average_score:.2f}")
    print(f"Decline: {negative_effectiveness_post.average_score - baseline.average_score:+.2f}")
    
    print(f"\n🎯 QUANTITATIVE EFFECTIVENESS RESULTS:")
    print("=" * 50)
    print(f"Baseline: {baseline.average_score:.2f}")
    print(f"High effectiveness change: {high_effectiveness_post.average_score - baseline.average_score:+.2f}")
    print(f"Low effectiveness change: {low_effectiveness_post.average_score - baseline.average_score:+.2f}")
    print(f"Negative effectiveness change: {negative_effectiveness_post.average_score - baseline.average_score:+.2f}")
    print(f"Consistency: {abs(baseline.average_score - baseline2.average_score):.3f}")
    
    # Check if system meets quantitative requirements
    consistency_ok = abs(baseline.average_score - baseline2.average_score) < 0.01
    high_improvement = high_effectiveness_post.average_score > baseline.average_score + 0.3
    low_minimal_change = abs(low_effectiveness_post.average_score - baseline.average_score) < 0.2
    negative_decline = negative_effectiveness_post.average_score < baseline.average_score - 0.3
    
    print(f"\n✅ QUANTITATIVE REQUIREMENTS CHECK:")
    print(f"Consistency: {'✅' if consistency_ok else '❌'}")
    print(f"High effectiveness → improvement: {'✅' if high_improvement else '❌'}")
    print(f"Low effectiveness → minimal change: {'✅' if low_minimal_change else '❌'}")
    print(f"Negative effectiveness → decline: {'✅' if negative_decline else '❌'}")
    
    if consistency_ok and high_improvement and low_minimal_change and negative_decline:
        print("🎉 ALL QUANTITATIVE REQUIREMENTS MET! System measures conversation effectiveness correctly!")
    else:
        print("⚠️ Some requirements not met. System needs further tuning.")

if __name__ == "__main__":
    asyncio.run(test_quantitative_system())
