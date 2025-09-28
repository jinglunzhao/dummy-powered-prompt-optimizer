#!/usr/bin/env python3
"""
Assessment System - LLM-Based Self-Assessment Simulation

This system uses LLM to simulate how a dummy would self-assess after coaching conversations.
The LLM acts as the dummy taking the assessment, considering:
1. Dummy's personality profile and baseline traits
2. Conversation history and coaching received
3. How the conversation might have influenced their self-perception

Key Features:
- Consistent: Same dummy + same conversation = similar results
- Realistic: LLM simulates dummy's self-assessment behavior
- Impact-aware: Conversation content influences assessment responses
- Personality-driven: Responses reflect dummy's traits and growth
"""

import asyncio
import json
import re
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from models import AIDummy, Assessment, AssessmentResponse, PersonalityProfile, SocialAnxietyProfile, Conversation, ConversationTurn
import aiohttp

class AssessmentSystemLLMBased:
    """LLM-based self-assessment simulation system"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or "your-deepseek-api-key"  # Will be set from config
        
        # 20 social skills assessment questions (1-4 scale)
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
    
    async def generate_pre_assessment(self, dummy: AIDummy) -> Assessment:
        """Generate baseline assessment using LLM to simulate dummy's self-assessment"""
        print(f"📝 {dummy.name} is taking the baseline assessment...")
        
        # Create system prompt for assessment method
        system_prompt = self._create_assessment_system_prompt()
        
        # Create user prompt with dummy profile
        user_prompt = self._create_baseline_user_prompt(dummy)
        
        # Get LLM assessment
        assessment_data = await self._get_llm_assessment(system_prompt, user_prompt, dummy)
        
        # Parse and create assessment object
        assessment = self._parse_assessment_response(assessment_data, dummy, "pre")
        
        print(f"✅ {dummy.name} completed baseline assessment: {assessment.average_score:.2f} average")
        return assessment
    
    async def generate_post_assessment(self, dummy: AIDummy, pre_assessment: Assessment, 
                                     conversation: Conversation = None) -> Assessment:
        """Generate post-conversation assessment using LLM to simulate dummy's self-assessment after coaching"""
        
        if not conversation:
            return await self.generate_pre_assessment(dummy)
        
        print(f"📝 {dummy.name} is taking the post-conversation assessment...")
        
        # Create system prompt for assessment method
        system_prompt = self._create_assessment_system_prompt()
        
        # Create user prompt with dummy profile and conversation history
        user_prompt = self._create_post_conversation_user_prompt(dummy, conversation, pre_assessment)
        
        # Get LLM assessment
        assessment_data = await self._get_llm_assessment(system_prompt, user_prompt, dummy)
        
        # Parse and create assessment object
        assessment = self._parse_assessment_response(assessment_data, dummy, "post")
        
        print(f"✅ {dummy.name} completed post-conversation assessment: {assessment.average_score:.2f} average")
        return assessment
    
    def _create_assessment_system_prompt(self) -> str:
        """Create system prompt with objective assessment methodology"""
        return """You are administering a social skills self-assessment questionnaire. Your role is to help a student evaluate themselves honestly and consistently.

ASSESSMENT METHODOLOGY:
- This is a self-assessment with 20 questions about social skills
- Each question should be rated on a scale of 1-4:
  * 1 = Not true of me (I rarely/never do this)
  * 2 = Somewhat true of me (I do this sometimes)
  * 3 = Mostly true of me (I do this often)
  * 4 = Very true of me (I almost always do this)

IMPORTANT INSTRUCTIONS:
1. Be consistent with the student's personality and baseline traits
2. Consider how coaching conversations might have influenced their self-perception
3. Responses should reflect genuine self-reflection, not external assessment
4. Maintain personality consistency while allowing for growth from coaching
5. Each question should receive exactly one integer score from 1-4

RESPONSE FORMAT:
For each of the 20 questions, provide only the numeric score (1-4) followed by a brief explanation (1-2 sentences) of why the student would rate themselves that way.

Example:
1. I ask for help when I need it.
Score: 2
Explanation: I usually try to figure things out myself first, but I'm getting better at asking for help when I'm really stuck.

2. I stay calm when dealing with problems.
Score: 3
Explanation: I've learned some strategies to stay calm, though I still get stressed with really big problems."""

    def _create_baseline_user_prompt(self, dummy: AIDummy) -> str:
        """Create user prompt for baseline assessment with dummy profile"""
        
        # Get personality description
        personality_desc = self._get_personality_description(dummy.personality)
        anxiety_desc = self._get_anxiety_description(dummy.social_anxiety)
        
        return f"""STUDENT PROFILE:
Name: {dummy.name}
Age: {dummy.age}
Major: {dummy.major}
University: {dummy.university}

PERSONALITY TRAITS:
{personality_desc}

SOCIAL ANXIETY:
{anxiety_desc}

PERSONAL DETAILS:
- Fears: {', '.join(dummy.fears)}
- Goals: {', '.join(dummy.goals)}
- Challenges: {', '.join(dummy.challenges)}
- Behaviors: {', '.join(dummy.behaviors)}

BASELINE ASSESSMENT:
This is {dummy.name}'s initial self-assessment before any coaching conversations. Please help them evaluate themselves honestly based on their current personality traits, anxiety level, and typical behaviors.

Rate each of the 20 social skills questions from 1-4 based on how {dummy.name} would realistically assess themselves given their personality profile."""

    def _create_post_conversation_user_prompt(self, dummy: AIDummy, conversation: Conversation, 
                                            pre_assessment: Assessment) -> str:
        """Create user prompt for post-conversation assessment with conversation history"""
        
        # Get personality description
        personality_desc = self._get_personality_description(dummy.personality)
        anxiety_desc = self._get_anxiety_description(dummy.social_anxiety)
        
        # Summarize conversation
        conversation_summary = self._summarize_conversation(conversation)
        
        # Get baseline scores for reference
        baseline_scores = self._get_baseline_scores_summary(pre_assessment)
        
        return f"""STUDENT PROFILE:
Name: {dummy.name}
Age: {dummy.age}
Major: {dummy.major}
University: {dummy.university}

PERSONALITY TRAITS:
{personality_desc}

SOCIAL ANXIETY:
{anxiety_desc}

PERSONAL DETAILS:
- Fears: {', '.join(dummy.fears)}
- Goals: {', '.join(dummy.goals)}
- Challenges: {', '.join(dummy.challenges)}
- Behaviors: {', '.join(dummy.behaviors)}

COACHING CONVERSATION SUMMARY:
{conversation_summary}

BASELINE ASSESSMENT REFERENCE:
{baseline_scores}

POST-COACHING ASSESSMENT:
This is {dummy.name}'s self-assessment after having coaching conversations. The coaching may have influenced their self-perception, confidence, and awareness of their social skills.

Please help them evaluate themselves honestly, considering:
1. Their baseline personality and typical behaviors
2. How the coaching conversation might have affected their self-awareness
3. Any insights, encouragement, or strategies they received
4. How they might feel more confident or aware of their abilities now

Rate each of the 20 social skills questions from 1-4 based on how {dummy.name} would assess themselves after this coaching experience."""

    def _get_personality_description(self, personality: PersonalityProfile) -> str:
        """Create personality description for LLM context"""
        return f"""- Extraversion: {personality.extraversion}/10 ({'Very outgoing and social' if personality.extraversion >= 7 else 'Moderately social' if personality.extraversion >= 4 else 'Introverted and prefers quiet activities'})
- Agreeableness: {personality.agreeableness}/10 ({'Very cooperative and helpful' if personality.agreeableness >= 7 else 'Moderately agreeable' if personality.agreeableness >= 4 else 'More competitive and independent'})
- Conscientiousness: {personality.conscientiousness}/10 ({'Very organized and responsible' if personality.conscientiousness >= 7 else 'Moderately organized' if personality.conscientiousness >= 4 else 'More spontaneous and flexible'})
- Neuroticism: {personality.neuroticism}/10 ({'Very sensitive to stress and emotions' if personality.neuroticism >= 7 else 'Moderately sensitive' if personality.neuroticism >= 4 else 'Very emotionally stable and calm'})
- Openness: {personality.openness}/10 ({'Very creative and curious' if personality.openness >= 7 else 'Moderately open to new experiences' if personality.openness >= 4 else 'More traditional and practical'})"""

    def _get_anxiety_description(self, anxiety: SocialAnxietyProfile) -> str:
        """Create anxiety description for LLM context"""
        return f"""- Anxiety Level: {anxiety.anxiety_level}/10 ({'Severe social anxiety' if anxiety.anxiety_level >= 7 else 'Moderate social anxiety' if anxiety.anxiety_level >= 5 else 'Low social anxiety'})
- Communication Style: {anxiety.communication_style}
- Triggers: {', '.join(anxiety.triggers)}
- Social Comfort: {anxiety.social_comfort}/10"""

    def _summarize_conversation(self, conversation: Conversation) -> str:
        """Summarize the conversation for LLM context"""
        if not conversation.turns:
            return "No conversation turns available."
        
        # Get key coaching moments (AI responses)
        ai_responses = [turn.message for turn in conversation.turns if turn.speaker == "ai"]
        
        if not ai_responses:
            return "No coaching responses in conversation."
        
        # Summarize coaching themes
        summary = f"Conversation had {len(conversation.turns)} total turns with {len(ai_responses)} coaching responses.\n\n"
        summary += "Key coaching themes:\n"
        
        # Extract key coaching points (first few AI responses)
        for i, response in enumerate(ai_responses[:3], 1):
            summary += f"{i}. {response[:150]}{'...' if len(response) > 150 else ''}\n"
        
        if len(ai_responses) > 3:
            summary += f"... and {len(ai_responses) - 3} more coaching responses.\n"
        
        return summary

    def _get_baseline_scores_summary(self, pre_assessment: Assessment) -> str:
        """Get baseline scores summary for reference"""
        low_scores = [r for r in pre_assessment.responses if r.score <= 2]
        high_scores = [r for r in pre_assessment.responses if r.score >= 3]
        
        summary = f"Baseline average score: {pre_assessment.average_score:.2f}/4.0\n\n"
        
        if low_scores:
            summary += "Areas rated lower (1-2):\n"
            for response in low_scores[:3]:
                summary += f"- {response.question}: {response.score}/4\n"
        
        if high_scores:
            summary += "\nAreas rated higher (3-4):\n"
            for response in high_scores[:3]:
                summary += f"- {response.question}: {response.score}/4\n"
        
        return summary

    async def _get_llm_assessment(self, system_prompt: str, user_prompt: str, dummy: AIDummy) -> str:
        """Get assessment from LLM"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "https://api.deepseek.com/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "deepseek-chat",
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt}
                        ],
                        "max_tokens": 2000,
                        "temperature": 0.3  # Lower temperature for consistency
                    }
                ) as response:
                    result = await response.json()
                    return result['choices'][0]['message']['content'].strip()
        except Exception as e:
            print(f"❌ Error getting LLM assessment: {e}")
            # Fallback to default scores
            return self._create_fallback_response()

    def _create_fallback_response(self) -> str:
        """Create fallback response if LLM fails"""
        response = ""
        for i, question in enumerate(self.questions, 1):
            response += f"{i}. {question}\nScore: 2\nExplanation: Default response due to system error.\n\n"
        return response

    def _parse_assessment_response(self, assessment_data: str, dummy: AIDummy, assessment_type: str) -> Assessment:
        """Parse LLM response into Assessment object"""
        responses = []
        
        # Parse the response to extract scores and explanations
        lines = assessment_data.split('\n')
        current_question = None
        current_score = None
        current_explanation = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if this is a question (starts with number)
            if re.match(r'^\d+\.', line):
                # Save previous question if exists
                if current_question and current_score is not None:
                    responses.append(AssessmentResponse(
                        question=current_question,
                        score=current_score,
                        confidence=8,  # Default confidence (0-10 scale)
                        reasoning=current_explanation or "LLM-based assessment"
                    ))
                
                # Start new question
                current_question = line.split('.', 1)[1].strip()
                current_score = None
                current_explanation = None
            
            # Check if this is a score line
            elif line.startswith('Score:'):
                try:
                    current_score = int(line.split(':', 1)[1].strip())
                    # Ensure score is within bounds
                    current_score = max(1, min(4, current_score))
                except (ValueError, IndexError):
                    current_score = 2  # Default fallback
            
            # Check if this is an explanation line
            elif line.startswith('Explanation:'):
                current_explanation = line.split(':', 1)[1].strip()
        
        # Handle the last question
        if current_question and current_score is not None:
            responses.append(AssessmentResponse(
                question=current_question,
                score=current_score,
                confidence=8,
                reasoning=current_explanation or "LLM-based assessment"
            ))
        
        # Ensure we have all 20 questions
        while len(responses) < len(self.questions):
            question_idx = len(responses)
            responses.append(AssessmentResponse(
                question=self.questions[question_idx],
                score=2,  # Default score
                confidence=5,
                reasoning="Default response - LLM parsing issue"
            ))
        
        # Calculate totals
        total_score = sum(r.score for r in responses)
        average_score = total_score / len(responses)
        improvement_areas = [r.question for r in responses if r.score <= 2][:3]
        
        return Assessment(
            dummy_id=dummy.id,
            assessment_type=assessment_type,
            responses=responses,
            total_score=total_score,
            average_score=average_score,
            improvement_areas=improvement_areas,
            timestamp=datetime.now()
        )
