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
        """Generate a pre-intervention self-assessment where the dummy answers all questions at once"""
        
        print(f"📝 {dummy.name} is taking the pre-assessment...")
        
        # Ask all 20 questions in one API call
        assessment_response = await self._ask_dummy_all_assessment_questions(dummy)
        
        # Parse the complete assessment response
        responses = self._parse_complete_assessment_response(assessment_response, dummy)
        
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
        """Generate a post-intervention self-assessment where the dummy answers all questions at once"""
        
        print(f"📝 {dummy.name} is taking the post-assessment...")
        
        # Analyze conversation content if available for context
        conversation_context = self._summarize_conversation_for_assessment(conversation) if conversation else ""
        
        # Ask all 20 questions in one API call with conversation context
        assessment_response = await self._ask_dummy_all_assessment_questions(
            dummy, conversation_context=conversation_context, pre_assessment=pre_assessment
        )
        
        # Parse the complete assessment response
        responses = self._parse_complete_assessment_response(assessment_response, dummy)
        
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
    
    async def _ask_dummy_all_assessment_questions(self, dummy: AIDummy, 
                                                conversation_context: str = "",
                                                pre_assessment: Assessment = None) -> str:
        """Ask the dummy AI to answer all assessment questions in one call, with conversation memory"""
        
        # Create the complete assessment prompt
        questions_text = "\n".join([f"{i+1}. {q}" for i, q in enumerate(self.questions)])
        
        # Determine base personality influence
        extraversion_score = dummy.personality.extraversion
        agreeableness_score = dummy.personality.agreeableness
        conscientiousness_score = dummy.personality.conscientiousness
        anxiety_score = dummy.social_anxiety.anxiety_level
        
        # Build the conversation memory context with previous assessment grounding
        if conversation_context and pre_assessment:
            # Create detailed previous assessment reference
            previous_scores = []
            for i, response in enumerate(pre_assessment.responses):
                previous_scores.append(f"{i+1}. {response.question} → {response.score}/4")
            
            previous_scores_text = "\n".join(previous_scores)
            memory_context = f"""

YOUR PREVIOUS ASSESSMENT RESULTS: In your last assessment, you rated yourself as follows:
{previous_scores_text}
(Your overall previous average was: {pre_assessment.average_score:.2f}/4)

CONVERSATION MEMORY: You have been having ongoing conversations about your social skills. Here's what you've discussed:

{conversation_context}

CRITICAL ASSESSMENT RULES: Rate yourself again for each question, following these strict guidelines:
1. For each question, look at your previous score and the conversation content
2. If the conversation was relevant to that skill, you may rate yourself 1 point higher (e.g., 2→3, 3→4)
3. If the conversation was NOT relevant to that skill, maintain your previous score (±0 points)
4. NEVER rate yourself more than 1 point lower than your previous score
5. NEVER rate yourself more than 1 point higher than your previous score
6. Your core personality and baseline abilities remain stable - only coaching-relevant skills should improve slightly

Remember: You are the same person with the same baseline abilities. Coaching should only cause small, realistic improvements in relevant areas."""
        elif conversation_context:
            memory_context = f"""

CONVERSATION MEMORY: You have been having ongoing conversations about your social skills. Here's what you've discussed:

{conversation_context}

Based on these conversations, how has your perspective and confidence changed? Rate yourself based on your current self-perception after these interactions."""
        else:
            memory_context = """

BASELINE ASSESSMENT: This is your initial self-assessment. Be honest about your current abilities and confidence level."""
        
        prompt = f"""You are {dummy.name}, a {dummy.major} student with these characteristics:
- Extraversion: {extraversion_score}/10 ({'Very outgoing and social' if extraversion_score >= 8 else 'Moderately outgoing' if extraversion_score >= 5 else 'More reserved and quiet'})
- Agreeableness: {agreeableness_score}/10 ({'Highly cooperative and helpful' if agreeableness_score >= 8 else 'Moderately cooperative' if agreeableness_score >= 5 else 'More independent and competitive'})
- Conscientiousness: {conscientiousness_score}/10 ({'Very organized and responsible' if conscientiousness_score >= 8 else 'Moderately organized' if conscientiousness_score >= 5 else 'More flexible and spontaneous'})
- Anxiety Level: {anxiety_score}/10 ({'High anxiety in social situations' if anxiety_score >= 8 else 'Moderate anxiety' if anxiety_score >= 5 else 'Low anxiety and calm'})
- Challenges: {', '.join(dummy.challenges[:3])}
{memory_context}

You are taking a self-assessment about your social skills. Rate yourself from 1 (Not True) to 4 (Very True) for each question.

Questions:
{questions_text}

Respond in this exact format:
1. [Rating: X/4] [Your honest self-assessment and reasoning]
2. [Rating: X/4] [Your honest self-assessment and reasoning]
... (continue for all 20 questions)

Rate yourself based on your current feelings, confidence, and self-perception."""

        try:
            async with aiohttp.ClientSession() as session:
                response = await session.post(
                    "https://api.deepseek.com/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {Config.DEEPSEEK_API_KEY}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": Config.DEEPSEEK_REASONER_MODEL,
                        "messages": [{"role": "user", "content": prompt}],
                        "max_tokens": 800,
                        "temperature": 0.3  # Higher for human-like responses
                    },
                    timeout=aiohttp.ClientTimeout(total=60)
                )
                
                if response.status == 200:
                    data = await response.json()
                    return data["choices"][0]["message"]["content"].strip()
                else:
                    print(f"❌ API error {response.status}: {await response.text()}")
                    return self._generate_fallback_assessment()
                    
        except Exception as e:
            print(f"❌ Error asking assessment questions: {e}")
            return self._generate_fallback_assessment()
    
    def _parse_complete_assessment_response(self, response: str, dummy: AIDummy) -> List[AssessmentResponse]:
        """Parse the complete assessment response to extract all 20 scores"""
        responses = []
        lines = response.split('\n')
        
        for i, question in enumerate(self.questions):
            # Try to find the corresponding line in the response
            score = 2  # Default fallback
            confidence = 3
            notes = "Default response"
            
            # Look for the question number in the response
            for line in lines:
                if line.strip().startswith(f"{i+1}.") or f"{i+1}." in line:
                    # Parse the line for rating
                    if "rating:" in line.lower():
                        # Extract rating
                        import re
                        rating_match = re.search(r'rating:\s*(\d)/4', line.lower())
                        if rating_match:
                            score = int(rating_match.group(1))
                        else:
                            # Fallback: look for number
                            numbers = re.findall(r'\b[1-4]\b', line)
                            if numbers:
                                score = int(numbers[0])
                    
                    # Generate confidence and notes from the line
                    confidence = self._generate_confidence_from_response(line)
                    notes = f"Self-assessment: {line.strip()[:200]}..."
                    break
            
            response_obj = AssessmentResponse(
                question=question,
                score=score,
                confidence=confidence,
                notes=notes
            )
            responses.append(response_obj)
        
        return responses
    
    def _generate_fallback_assessment(self) -> str:
        """Generate a fallback assessment when API fails"""
        fallback = ""
        for i, question in enumerate(self.questions):
            fallback += f"{i+1}. Rating: 2/4 I'm not sure about this skill.\n"
        return fallback
    
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
    
    def _summarize_conversation_for_assessment(self, conversation: 'Conversation') -> str:
        """Create a detailed summary of the conversation for assessment context"""
        if not conversation or not conversation.turns:
            return ""
        
        # Create a detailed conversation summary
        conversation_summary = []
        
        # Add conversation overview
        conversation_summary.append(f"You had a {len(conversation.turns)}-turn coaching conversation.")
        
        # Extract key conversation exchanges
        dummy_turns = [turn for turn in conversation.turns if turn.speaker == "dummy"]
        ai_turns = [turn for turn in conversation.turns if turn.speaker == "ai"]
        
        # Summarize what the dummy shared
        if dummy_turns:
            dummy_concerns = []
            for turn in dummy_turns[:3]:  # First 3 dummy turns
                if len(turn.message) > 50:
                    dummy_concerns.append(turn.message[:100] + "...")
                else:
                    dummy_concerns.append(turn.message)
            
            if dummy_concerns:
                conversation_summary.append(f"You shared: {' '.join(dummy_concerns)}")
        
        # Summarize key coaching advice
        if ai_turns:
            coaching_points = []
            for turn in ai_turns[:2]:  # First 2 AI turns
                if len(turn.message) > 50:
                    coaching_points.append(turn.message[:100] + "...")
                else:
                    coaching_points.append(turn.message)
            
            if coaching_points:
                conversation_summary.append(f"Your coach advised: {' '.join(coaching_points)}")
        
        # Add conversation impact
        conversation_summary.append("This conversation helped you reflect on your social skills and provided new strategies.")
        
        return " ".join(conversation_summary)
    
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
