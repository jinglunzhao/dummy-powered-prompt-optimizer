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
        """Ask the dummy AI to answer assessment questions through multi-turn conversation"""
        
        # Create a conversation session with the dummy
        messages = [
            {
                "role": "system", 
                "content": f"""You are {dummy.name}, a {dummy.major} student with these characteristics:
- Extraversion: {dummy.personality.extraversion}/10
- Agreeableness: {dummy.personality.agreeableness}/10  
- Conscientiousness: {dummy.personality.conscientiousness}/10
- Anxiety Level: {dummy.social_anxiety.anxiety_level}/10
- Challenges: {', '.join(dummy.challenges[:3])}

You are taking a self-assessment about your social skills. Be honest about your current feelings and self-perception."""
            }
        ]
        
        # If this is a post-assessment, add coaching conversation context
        if conversation_context:
            messages.append({
                "role": "assistant",
                "content": f"I just had a helpful coaching conversation. Here's what happened: {conversation_context}"
            })
            messages.append({
                "role": "user", 
                "content": "How did that coaching conversation make you feel? Did it change your perspective on your social skills or confidence?"
            })
        
        # Start the assessment conversation
        messages.append({
            "role": "user",
            "content": "Now I'd like you to take a self-assessment. I'll ask you about various social skills, and you should rate yourself from 1 (Not True) to 4 (Very True). Let's start with the first few questions:\n\n1. I ask for help when I need it.\n2. I stay calm when dealing with problems.\n3. I help my friends when they are having a problem.\n\nPlease rate yourself honestly on these three questions."
        })

        # Conduct multi-turn conversation to build self-awareness
        all_responses = []
        
        try:
            async with aiohttp.ClientSession() as session:
                # First round - get initial self-reflection
                response = await session.post(
                    "https://api.deepseek.com/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {Config.DEEPSEEK_API_KEY}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": Config.DEEPSEEK_REASONER_MODEL,
                        "messages": messages,
                        "max_tokens": 300,
                        "temperature": 0.3  # Higher for more human-like responses
                    },
                    timeout=aiohttp.ClientTimeout(total=30)
                )
                
                if response.status == 200:
                    data = await response.json()
                    dummy_response = data["choices"][0]["message"]["content"].strip()
                    messages.append({"role": "assistant", "content": dummy_response})
                    all_responses.append(dummy_response)
                    
                    # Second round - continue assessment with more questions
                    messages.append({
                        "role": "user",
                        "content": "Good, thank you for those honest answers. Now let's continue with more questions:\n\n4. I work well with my classmates.\n5. I do the right thing without being told.\n6. I do my part in a group.\n7. I stay calm when I disagree with others.\n8. I stand up for others when they are not treated well.\n\nPlease rate yourself on these questions as well."
                    })
                    
                    response = await session.post(
                        "https://api.deepseek.com/v1/chat/completions",
                        headers={
                            "Authorization": f"Bearer {Config.DEEPSEEK_API_KEY}",
                            "Content-Type": "application/json"
                        },
                        json={
                            "model": Config.DEEPSEEK_REASONER_MODEL,
                            "messages": messages,
                            "max_tokens": 300,
                            "temperature": 0.3
                        },
                        timeout=aiohttp.ClientTimeout(total=30)
                    )
                    
                    if response.status == 200:
                        data = await response.json()
                        dummy_response = data["choices"][0]["message"]["content"].strip()
                        messages.append({"role": "assistant", "content": dummy_response})
                        all_responses.append(dummy_response)
                        
                        # Third round - finish remaining questions
                        messages.append({
                            "role": "user",
                            "content": "Excellent. Let's finish with the remaining questions:\n\n9. I look at people when I talk to them.\n10. I am careful when I use things that aren't mine.\n11. I let people know when there's a problem.\n12. I pay attention when the teacher talks to the class.\n13. I try to make others feel better.\n14. I say \"thank you\" when someone helps me.\n15. I keep my promises.\n16. I pay attention when others present their ideas.\n17. I try to find a good way to end a disagreement.\n18. I try to think about how others feel.\n19. I try to forgive others when they say \"sorry\".\n20. I follow school rules.\n\nPlease rate yourself on these final questions."
                        })
                        
                        response = await session.post(
                            "https://api.deepseek.com/v1/chat/completions",
                            headers={
                                "Authorization": f"Bearer {Config.DEEPSEEK_API_KEY}",
                                "Content-Type": "application/json"
                            },
                            json={
                                "model": Config.DEEPSEEK_REASONER_MODEL,
                                "messages": messages,
                                "max_tokens": 400,
                                "temperature": 0.3
                            },
                            timeout=aiohttp.ClientTimeout(total=30)
                        )
                        
                        if response.status == 200:
                            data = await response.json()
                            dummy_response = data["choices"][0]["message"]["content"].strip()
                            all_responses.append(dummy_response)
                            
                            # Combine all responses
                            return "\n\n".join(all_responses)
                        else:
                            print(f"❌ API error in round 3 {response.status}: {await response.text()}")
                            return self._generate_fallback_assessment()
                    else:
                        print(f"❌ API error in round 2 {response.status}: {await response.text()}")
                        return self._generate_fallback_assessment()
                else:
                    print(f"❌ API error in round 1 {response.status}: {await response.text()}")
                    return self._generate_fallback_assessment()
                    
        except Exception as e:
            print(f"❌ Error in multi-turn assessment: {e}")
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
