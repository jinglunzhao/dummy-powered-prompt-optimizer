"""
Assessment System for AI Dummy Social Skills Testing
Generates and evaluates social skills assessments
"""
import random
import json
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
from models import AIDummy, Assessment, AssessmentResponse, PersonalityProfile, SocialAnxietyProfile
from config import Config

class AssessmentSystem:
    """Manages social skills assessments for AI dummies"""
    
    def __init__(self):
        self.questions = Config.SOCIAL_SKILLS_QUESTIONS
        self.question_weights = self._generate_question_weights()
    
    def _generate_question_weights(self) -> Dict[str, float]:
        """Generate weights for questions based on importance"""
        # Questions about core social skills get higher weights
        weights = {
            "How comfortable are you starting conversations with strangers?": 1.2,
            "How well do you maintain eye contact during conversations?": 1.1,
            "How easily do you express your opinions in group settings?": 1.3,
            "How comfortable are you with public speaking?": 1.4,
            "How well do you handle criticism or disagreement?": 1.2,
            "How easily do you make new friends?": 1.1,
            "How comfortable are you in large social gatherings?": 1.0,
            "How well do you read social cues and body language?": 1.1,
            "How easily do you ask for help when needed?": 1.0,
            "How comfortable are you with small talk?": 1.0
        }
        return weights
    
    def generate_pre_assessment(self, dummy: AIDummy) -> Assessment:
        """Generate a pre-intervention assessment based on dummy's profile"""
        responses = []
        
        for question in self.questions:
            # Generate realistic score based on personality and anxiety
            base_score = self._calculate_base_score(dummy)
            
            # Add some realistic variation (±0.5 points)
            variation = random.uniform(-0.5, 0.5)
            final_score = base_score + variation
            
            # Round to nearest whole number and clamp to 1-4 range
            final_score = max(1, min(4, int(round(final_score))))
            
            # Generate confidence score (1-4 scale, higher for higher scores)
            confidence = max(1, min(4, int(round(final_score + random.uniform(-0.5, 0.5)))))
            
            # Generate notes based on score
            notes = self._generate_assessment_notes(question, final_score, confidence, dummy)
            
            response = AssessmentResponse(
                question=question,
                score=final_score,
                confidence=confidence,
                notes=notes
            )
            responses.append(response)
        
        # Calculate scores
        scores = Assessment.calculate_scores(responses)
        
        # Identify improvement areas
        improvement_areas = self._identify_improvement_areas(responses)
        
        return Assessment(
            dummy_id=dummy.id,
            responses=responses,
            total_score=scores["total_score"],
            average_score=scores["average_score"],
            improvement_areas=improvement_areas
        )
    
    def generate_post_assessment(self, dummy: AIDummy, pre_assessment: Assessment, 
                               improvement_factor: float = 0.3) -> Assessment:
        """Generate a post-intervention assessment showing improvement"""
        responses = []
        
        for pre_response in pre_assessment.responses:
            # Start with pre-assessment score
            pre_score = pre_response.score
            
            # Most scores improve by 0-1 points, some stay the same
            improvement_chance = random.random()
            if improvement_chance < 0.7:  # 70% chance of improvement
                improvement = random.choice([0, 1])  # 0 or 1 point improvement
                post_score = min(4, pre_score + improvement)
            else:  # 30% chance of no change
                post_score = pre_score
            
            # Generate confidence (usually improves with score improvement)
            confidence = max(1, min(4, int(round(post_score + random.uniform(-0.5, 0.5)))))
            
            # Generate notes showing improvement
            notes = self._generate_post_assessment_notes(pre_response.question, post_score, confidence, dummy)
            
            response = AssessmentResponse(
                question=pre_response.question,
                score=post_score,
                confidence=confidence,
                notes=notes
            )
            responses.append(response)
        
        # Calculate new scores
        scores = Assessment.calculate_scores(responses)
        
        # Update improvement areas
        improvement_areas = self._identify_improvement_areas(responses)
        
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
