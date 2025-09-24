"""
Assessment System for AI Dummy Social Skills Testing
Generates and evaluates social skills assessments
"""
import random
import json
import os
import asyncio
import aiohttp
from typing import List, Dict, Any, Optional
from datetime import datetime
from models import AIDummy, Assessment, AssessmentResponse, PersonalityProfile, SocialAnxietyProfile
from config import Config

class AssessmentSystem:
    """Manages social skills assessments for AI dummies"""
    
    def __init__(self, use_weights: bool = False):
        self.questions = Config.SOCIAL_SKILLS_QUESTIONS
        self.use_weights = use_weights
        self.question_weights = self._generate_question_weights() if use_weights else {}
    
    def _generate_question_weights(self) -> Dict[str, float]:
        """Generate weights for questions based on importance"""
        # Weight questions based on skill category importance
        weights = {
            # Communication Skills (higher weight)
            "I ask for help when I need it.": 1.3,
            "I let people know when there's a problem.": 1.2,
            "I pay attention when others present their ideas.": 1.1,
            "I work well with my classmates.": 1.2,
            "I look at people when I talk to them.": 1.1,
            "I pay attention when the teacher talks to the class.": 1.0,
            
            # Emotional Regulation (highest weight - critical for social skills)
            "I stay calm when dealing with problems.": 1.4,
            "I stay calm when I disagree with others.": 1.4,
            "I try to find a good way to end a disagreement.": 1.3,
            
            # Empathy & Social Support (high weight)
            "I help my friends when they are having a problem.": 1.2,
            "I stand up for others when they are not treated well.": 1.3,
            "I try to make others feel better.": 1.2,
            "I try to think about how others feel.": 1.3,
            "I say \"thank you\" when someone helps me.": 1.1,
            "I try to forgive others when they say \"sorry\".": 1.1,
            
            # Responsibility & Cooperation (medium weight)
            "I do my part in a group.": 1.1,
            "I do the right thing without being told.": 1.0,
            "I am careful when I use things that aren't mine.": 1.0,
            "I keep my promises.": 1.1,
            "I follow school rules.": 1.0
        }
        return weights
    
    async def generate_pre_assessment(self, dummy: AIDummy) -> Assessment:
        """Generate a pre-intervention self-assessment where the dummy actually answers questions"""
        responses = []
        
        print(f"📝 {dummy.name} is taking the pre-assessment...")
        
        for i, question in enumerate(self.questions):
            print(f"   Question {i+1}/{len(self.questions)}: {question[:50]}...")
            
            # Have the dummy answer the question
            dummy_response = await self._ask_dummy_assessment_question(dummy, question)
            
            # Parse the response to get a score (1-4)
            score = self._parse_dummy_response_to_score(dummy_response, question)
            
            # Generate confidence based on response quality
            confidence = self._generate_confidence_from_response(dummy_response)
            
            # Generate notes from the dummy's response
            notes = self._generate_notes_from_response(dummy_response, question, score)
            
            response = AssessmentResponse(
                question=question,
                score=score,
                confidence=confidence,
                notes=notes
            )
            responses.append(response)
        
        # Calculate scores
        scores = self._calculate_weighted_scores(responses)
        
        # Identify improvement areas
        improvement_areas = self._identify_improvement_areas(responses)
        
        print(f"✅ {dummy.name} completed pre-assessment: {scores['average_score']:.2f} average")
        
        return Assessment(
            dummy_id=dummy.id,
            responses=responses,
            total_score=scores["total_score"],
            average_score=scores["average_score"],
            improvement_areas=improvement_areas
        )
    
    async def generate_post_assessment(self, dummy: AIDummy, pre_assessment: Assessment, 
                                     conversation: 'Conversation' = None,
                                     improvement_factor: float = 0.3) -> Assessment:
        """Generate a post-intervention self-assessment where the dummy answers questions after coaching"""
        responses = []
        
        print(f"📝 {dummy.name} is taking the post-assessment...")
        
        # Analyze conversation content if available for context
        conversation_context = self._summarize_conversation_for_assessment(conversation) if conversation else ""
        
        for i, pre_response in enumerate(pre_assessment.responses):
            print(f"   Question {i+1}/{len(pre_assessment.responses)}: {pre_response.question[:50]}...")
            
            # Have the dummy answer the question with conversation context
            dummy_response = await self._ask_dummy_assessment_question(
                dummy, 
                pre_response.question, 
                conversation_context=conversation_context,
                previous_score=pre_response.score
            )
            
            # Parse the response to get a score (1-4)
            score = self._parse_dummy_response_to_score(dummy_response, pre_response.question)
            
            # Generate confidence based on response quality
            confidence = self._generate_confidence_from_response(dummy_response)
            
            # Generate notes from the dummy's response
            notes = self._generate_notes_from_response(dummy_response, pre_response.question, score)
            
            response = AssessmentResponse(
                question=pre_response.question,
                score=score,
                confidence=confidence,
                notes=notes
            )
            responses.append(response)
        
        # Calculate new scores
        scores = self._calculate_weighted_scores(responses)
        
        # Update improvement areas
        improvement_areas = self._identify_improvement_areas(responses)
        
        print(f"✅ {dummy.name} completed post-assessment: {scores['average_score']:.2f} average")
        
        return Assessment(
            dummy_id=dummy.id,
            responses=responses,
            total_score=scores["total_score"],
            average_score=scores["average_score"],
            improvement_areas=improvement_areas
        )
    
    def _calculate_base_score(self, dummy: AIDummy) -> float:
        """Calculate base score based on personality and anxiety profile."""
        # Base score starts at 2.0 (middle of 4-point scale)
        base_score = 2.0
        
        # Personality adjustments
        extraversion_bonus = (dummy.personality.extraversion - 5) * 0.1  # -0.4 to +0.5
        agreeableness_bonus = (dummy.personality.agreeableness - 5) * 0.1  # -0.4 to +0.5
        conscientiousness_bonus = (dummy.personality.conscientiousness - 5) * 0.1  # -0.4 to +0.5
        
        # Anxiety penalty (higher anxiety = lower base score)
        anxiety_penalty = (dummy.social_anxiety.anxiety_level - 5) * 0.15  # -0.6 to +0.6
        
        # Calculate final base score (clamped between 1.0 and 4.0)
        final_score = base_score + extraversion_bonus + agreeableness_bonus + conscientiousness_bonus - anxiety_penalty
        return max(1.0, min(4.0, final_score))
    
    def _generate_assessment_notes(self, question: str, score: int, confidence: int, dummy: AIDummy) -> str:
        """Generate assessment notes based on 4-point scale."""
        if score == 1:
            return f"Struggles with {question.lower()}. Needs significant support and practice."
        elif score == 2:
            return f"Some difficulty with {question.lower()}. Shows potential for improvement with guidance."
        elif score == 3:
            return f"Generally good with {question.lower()}. Consistent performance with room for growth."
        else:  # score == 4
            return f"Excellent performance with {question.lower()}. Demonstrates strong social skills."
    
    def _generate_post_assessment_notes(self, question: str, score: int, confidence: int, dummy: AIDummy) -> str:
        """Generate post-assessment notes based on 4-point scale."""
        if score == 1:
            return f"Still struggles with {question.lower()}. May need additional support and practice."
        elif score == 2:
            return f"Some improvement in {question.lower()}. Shows positive development."
        elif score == 3:
            return f"Good progress in {question.lower()}. Demonstrates learning and practice."
        else:  # score == 4
            return f"Excellent improvement in {question.lower()}. Shows mastery of this skill."
    
    def _identify_improvement_areas(self, responses: List[AssessmentResponse]) -> List[str]:
        """Identify areas for improvement based on 4-point scale."""
        improvement_areas = []
        
        for response in responses:
            if response.score <= 2:  # Scores of 1-2 indicate areas needing improvement
                improvement_areas.append(f"Improve {response.question.lower()}")
        
        # Add general improvement suggestions
        if len(improvement_areas) > 0:
            improvement_areas.append("Continue practicing social skills through regular interaction")
            improvement_areas.append("Focus on emotional regulation and conflict resolution")
        
        return improvement_areas
    
    async def _ask_dummy_assessment_question(self, dummy: AIDummy, question: str, 
                                           conversation_context: str = "", 
                                           previous_score: int = None) -> str:
        """Ask the dummy AI to answer an assessment question"""
        
        # Build context for the assessment
        context_parts = [
            f"You are {dummy.name}, a {dummy.major} student.",
            f"Your personality traits: {', '.join(dummy.personality.get_dominant_traits())}",
            f"Your social anxiety level: {dummy.social_anxiety.get_anxiety_category()}",
            f"Your current challenges: {', '.join(dummy.challenges[:3])}"
        ]
        
        if conversation_context:
            context_parts.append(f"Recent coaching conversation context: {conversation_context}")
        
        if previous_score:
            context_parts.append(f"Your previous score for this area: {previous_score}/4")
        
        context = "\n".join(context_parts)
        
        # Create the assessment prompt
        prompt = f"""{context}

You are taking a self-assessment about your social skills. Please answer this question honestly based on your character and experiences:

"{question}"

Please respond with:
1. Your self-rating (1=Not True, 2=Somewhat True, 3=Mostly True, 4=Very True)
2. A brief explanation of why you rated yourself this way

Be honest and authentic to your character. Consider your personality, anxiety level, and recent experiences."""

        try:
            async with aiohttp.ClientSession() as session:
                response = await session.post(
                    "https://api.deepseek.com/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {Config.DEEPSEEK_API_KEY}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": Config.OPENAI_MODEL,
                        "messages": [{"role": "user", "content": prompt}],
                        "max_tokens": 200,
                        "temperature": 0.7
                    },
                    timeout=aiohttp.ClientTimeout(total=30)
                )
                
                if response.status == 200:
                    data = await response.json()
                    return data["choices"][0]["message"]["content"].strip()
                else:
                    print(f"❌ API error {response.status}: {await response.text()}")
                    return f"I would rate myself as 2/4. I'm not sure about this skill."
                    
        except Exception as e:
            print(f"❌ Error asking assessment question: {e}")
            return f"I would rate myself as 2/4. I'm not sure about this skill."
    
    def _parse_dummy_response_to_score(self, response: str, question: str) -> int:
        """Parse the dummy's response to extract a 1-4 score"""
        response_lower = response.lower()
        
        # Look for explicit rating numbers
        if "4" in response_lower or "four" in response_lower or "very true" in response_lower:
            return 4
        elif "3" in response_lower or "three" in response_lower or "mostly true" in response_lower:
            return 3
        elif "2" in response_lower or "two" in response_lower or "somewhat true" in response_lower:
            return 2
        elif "1" in response_lower or "one" in response_lower or "not true" in response_lower:
            return 1
        
        # Fallback: analyze sentiment and keywords
        positive_words = ["good", "well", "confident", "comfortable", "easy", "strong", "excellent"]
        negative_words = ["difficult", "hard", "struggle", "uncomfortable", "anxious", "weak", "poor"]
        
        positive_count = sum(1 for word in positive_words if word in response_lower)
        negative_count = sum(1 for word in negative_words if word in response_lower)
        
        if positive_count > negative_count and positive_count >= 2:
            return 4
        elif positive_count > negative_count:
            return 3
        elif negative_count > positive_count and negative_count >= 2:
            return 1
        else:
            return 2
    
    def _generate_confidence_from_response(self, response: str) -> int:
        """Generate confidence score based on response quality"""
        response_lower = response.lower()
        
        # Higher confidence indicators
        if any(word in response_lower for word in ["definitely", "absolutely", "certainly", "always", "never"]):
            return 4
        elif any(word in response_lower for word in ["usually", "often", "generally", "pretty"]):
            return 3
        elif any(word in response_lower for word in ["sometimes", "maybe", "depends", "varies"]):
            return 2
        else:
            return 3  # Default moderate confidence
    
    def _generate_notes_from_response(self, response: str, question: str, score: int) -> str:
        """Generate assessment notes from the dummy's response"""
        # Clean up the response for notes
        cleaned_response = response.replace("I would rate myself as", "").replace("1/4", "").replace("2/4", "").replace("3/4", "").replace("4/4", "").strip()
        cleaned_response = cleaned_response.replace("Not True", "").replace("Somewhat True", "").replace("Mostly True", "").replace("Very True", "").strip()
        
        if cleaned_response:
            return f"Self-assessment: {cleaned_response[:200]}..."
        else:
            return f"Rated {score}/4 on {question.lower()}"
    
    def _summarize_conversation_for_assessment(self, conversation: 'Conversation') -> str:
        """Create a brief summary of the conversation for assessment context"""
        if not conversation or not conversation.turns:
            return ""
        
        # Get key themes from the conversation
        all_text = " ".join([turn.message for turn in conversation.turns])
        
        # Extract key topics
        topics = []
        if "help" in all_text.lower():
            topics.append("help-seeking")
        if "confident" in all_text.lower() or "confidence" in all_text.lower():
            topics.append("confidence building")
        if "social" in all_text.lower() or "friend" in all_text.lower():
            topics.append("social skills")
        if "anxiety" in all_text.lower() or "nervous" in all_text.lower():
            topics.append("anxiety management")
        
        if topics:
            return f"Recent coaching focused on: {', '.join(topics[:3])}"
        else:
            return "Recent coaching session completed"
    
    def _calculate_weighted_scores(self, responses: List[AssessmentResponse]) -> Dict[str, float]:
        """Calculate scores with optional weighting"""
        total_score = 0
        total_weight = 0
        
        for response in responses:
            weight = self.question_weights.get(response.question, 1.0) if self.use_weights else 1.0
            total_score += response.score * weight
            total_weight += weight
        
        average_score = total_score / total_weight if total_weight > 0 else 0
        
        return {
            "total_score": total_score,
            "average_score": round(average_score, 2)
        }
    
    def _analyze_conversation_for_skills(self, conversation: 'Conversation') -> Dict[str, float]:
        """Analyze conversation content to identify skill development indicators"""
        if not conversation or not conversation.turns:
            return {}
        
        # Skill indicators based on conversation content
        skill_indicators = {
            "help_seeking": 0.0,
            "emotional_regulation": 0.0,
            "empathy": 0.0,
            "communication": 0.0,
            "responsibility": 0.0
        }
        
        # Analyze dummy responses for skill development
        dummy_turns = [turn for turn in conversation.turns if turn.speaker == "dummy"]
        
        for turn in dummy_turns:
            message_lower = turn.message.lower()
            
            # Help-seeking indicators
            if any(phrase in message_lower for phrase in ["help", "don't know", "struggling", "difficult", "need"]):
                skill_indicators["help_seeking"] += 0.2
            
            # Emotional regulation indicators
            if any(phrase in message_lower for phrase in ["calm", "okay", "better", "feel good", "confident"]):
                skill_indicators["emotional_regulation"] += 0.2
            elif any(phrase in message_lower for phrase in ["angry", "frustrated", "upset", "stressed"]):
                skill_indicators["emotional_regulation"] -= 0.1
            
            # Empathy indicators
            if any(phrase in message_lower for phrase in ["understand", "feel", "others", "friends", "help others"]):
                skill_indicators["empathy"] += 0.2
            
            # Communication indicators
            if any(phrase in message_lower for phrase in ["talk", "say", "express", "tell", "share"]):
                skill_indicators["communication"] += 0.1
            
            # Responsibility indicators
            if any(phrase in message_lower for phrase in ["try", "practice", "work on", "improve", "learn"]):
                skill_indicators["responsibility"] += 0.2
        
        # Normalize indicators (0.0 to 1.0 scale)
        for skill in skill_indicators:
            skill_indicators[skill] = max(0.0, min(1.0, skill_indicators[skill]))
        
        return skill_indicators
    
    def _calculate_skill_improvement(self, question: str, conversation_analysis: Dict[str, float], 
                                   dummy: AIDummy, improvement_factor: float) -> float:
        """Calculate improvement for a specific skill based on conversation analysis"""
        
        # Map questions to skill categories
        skill_mapping = {
            "I ask for help when I need it.": "help_seeking",
            "I stay calm when dealing with problems.": "emotional_regulation",
            "I stay calm when I disagree with others.": "emotional_regulation",
            "I help my friends when they are having a problem.": "empathy",
            "I stand up for others when they are not treated well.": "empathy",
            "I try to make others feel better.": "empathy",
            "I try to think about how others feel.": "empathy",
            "I work well with my classmates.": "communication",
            "I look at people when I talk to them.": "communication",
            "I let people know when there's a problem.": "communication",
            "I pay attention when others present their ideas.": "communication",
            "I do my part in a group.": "responsibility",
            "I do the right thing without being told.": "responsibility",
            "I am careful when I use things that aren't mine.": "responsibility",
            "I keep my promises.": "responsibility",
            "I follow school rules.": "responsibility",
            "I say \"thank you\" when someone helps me.": "empathy",
            "I try to forgive others when they say \"sorry\".": "empathy",
            "I try to find a good way to end a disagreement.": "emotional_regulation",
            "I pay attention when the teacher talks to the class.": "communication"
        }
        
        # Get relevant skill from conversation analysis
        relevant_skill = skill_mapping.get(question, "communication")
        conversation_improvement = conversation_analysis.get(relevant_skill, 0.0)
        
        # Base improvement from conversation (0.0 to 0.5 points)
        base_improvement = conversation_improvement * 0.5
        
        # Add some realistic variation based on dummy's personality
        personality_modifier = (dummy.personality.conscientiousness - 5) * 0.02  # -0.08 to +0.08
        
        # Combine factors
        total_improvement = base_improvement + personality_modifier + random.uniform(-0.1, 0.1)
        
        # Ensure realistic improvement range (-0.2 to +0.8 points)
        return max(-0.2, min(0.8, total_improvement))
    
    def calculate_improvement_metrics(self, pre: Assessment, post: Assessment) -> Dict[str, Any]:
        """Calculate improvement metrics between pre and post assessments."""
        if len(pre.responses) != len(post.responses):
            raise ValueError("Pre and post assessments must have the same number of responses")
        
        improvements = []
        total_pre = 0
        total_post = 0
        
        for pre_resp, post_resp in zip(pre.responses, post.responses):
            if pre_resp.question != post_resp.question:
                raise ValueError("Question mismatch between pre and post assessments")
            
            improvement = post_resp.score - pre_resp.score
            improvements.append(improvement)
            total_pre += pre_resp.score
            total_post += post_resp.score
        
        # Calculate metrics for 4-point scale
        avg_pre = total_pre / len(pre.responses)
        avg_post = total_post / len(post.responses)
        avg_improvement = avg_post - avg_pre
        improvement_percentage = (avg_improvement / avg_pre) * 100 if avg_pre > 0 else 0
        
        # Count improvement categories
        significant_improvements = sum(1 for imp in improvements if imp >= 1)
        moderate_improvements = sum(1 for imp in improvements if imp == 1)
        slight_improvements = sum(1 for imp in improvements if imp == 0.5)
        no_change = sum(1 for imp in improvements if imp == 0)
        declines = sum(1 for imp in improvements if imp < 0)
        
        return {
            "total_pre_score": total_pre,
            "total_post_score": total_post,
            "average_pre_score": round(avg_pre, 2),
            "average_post_score": round(avg_post, 2),
            "average_improvement": round(avg_improvement, 2),
            "improvement_percentage": round(improvement_percentage, 1),
            "significant_improvements": significant_improvements,
            "moderate_improvements": moderate_improvements,
            "slight_improvements": slight_improvements,
            "no_change": no_change,
            "declines": declines,
            "improvements_by_question": [
                {
                    "question": pre.responses[i].question,
                    "pre_score": pre.responses[i].score,
                    "post_score": post.responses[i].score,
                    "improvement": improvements[i]
                }
                for i in range(len(pre.responses))
            ]
        }
    
    def save_assessment(self, assessment: Assessment, filename: str = None):
        """Save assessment to JSON file"""
        if filename is None:
            filename = os.path.join(Config.DATA_DIR, Config.ASSESSMENTS_FILE)
        
        # Create data directory if it doesn't exist
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        # Load existing assessments with error handling
        existing_assessments = []
        if os.path.exists(filename):
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if content:  # Only try to parse if file has content
                        existing_assessments = json.loads(content)
                    else:
                        existing_assessments = []
            except (json.JSONDecodeError, ValueError) as e:
                print(f"Warning: Corrupted assessments file detected. Starting fresh. Error: {e}")
                existing_assessments = []
        
        # Add new assessment
        assessment_data = assessment.dict()
        existing_assessments.append(assessment_data)
        
        # Save updated file
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(existing_assessments, f, indent=2, default=str, ensure_ascii=False)
        
        print(f"Saved assessment for dummy {assessment.dummy_id}")
    
    def load_assessments(self, filename: str = None) -> List[Assessment]:
        """Load assessments from JSON file"""
        if filename is None:
            filename = os.path.join(Config.DATA_DIR, Config.ASSESSMENTS_FILE)
        
        if not os.path.exists(filename):
            print(f"File {filename} not found. No assessments available.")
            return []
        
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if not content:
                    print("File {filename} is empty. No assessments available.")
                    return []
                assessments_data = json.loads(content)
        except (json.JSONDecodeError, ValueError) as e:
            print(f"Error loading assessments from {filename}: {e}")
            return []
        
        assessments = [Assessment(**assessment_data) for assessment_data in assessments_data]
        print(f"Loaded {len(assessments)} assessments from {filename}")
        return assessments

def main():
    """Test the assessment system"""
    print("Testing Assessment System...")
    
    # This would typically be used with actual dummies
    # For testing, we'll create a sample dummy
    from character_generator import CharacterGenerator
    
    generator = CharacterGenerator()
    dummy = generator.generate_character()
    
    print(f"Generated test dummy: {dummy.name}")
    print(f"Anxiety level: {dummy.social_anxiety.get_anxiety_category()}")
    
    # Create assessment system
    assessment_system = AssessmentSystem()
    
    # Generate pre-assessment
    pre_assessment = assessment_system.generate_pre_assessment(dummy)
    print(f"\nPre-assessment average score: {pre_assessment.average_score:.2f}")
    
    # Generate post-assessment
    post_assessment = assessment_system.generate_post_assessment(dummy, pre_assessment)
    print(f"Post-assessment average score: {post_assessment.average_score:.2f}")
    
    # Calculate improvement metrics
    metrics = assessment_system.calculate_improvement_metrics(pre_assessment, post_assessment)
    print(f"Overall improvement: {metrics['average_improvement']:.2f} points")
    print(f"Improvement percentage: {metrics['improvement_percentage']:.1f}%")
    
    print("\nAssessment system test complete!")

if __name__ == "__main__":
    main()
