#!/usr/bin/env python3
"""
Regenerate AI Dummies with College Student Profiles
Creates 100 college/graduate student dummies with proper gender distribution
"""

import json
import os
import random
import uuid
from datetime import datetime
from typing import List, Dict, Any
from models import AIDummy, PersonalityProfile, SocialAnxietyProfile

class DateTimeEncoder(json.JSONEncoder):
    """Custom JSON encoder to handle datetime objects"""
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

class CharacterGenerator:
    def __init__(self):
        self.universities = [
            "State University", "Community College", "Ivy League University",
            "Technical Institute", "Liberal Arts College", "Business School",
            "Art Academy", "Medical School", "Law School", "Engineering University",
            "Agricultural College", "Online University", "Public Research University",
            "Private University", "Vocational School"
        ]
        self.majors = [
            "Computer Science", "Psychology", "Biology", "Engineering", "Business Administration",
            "English Literature", "History", "Political Science", "Sociology", "Economics",
            "Nursing", "Education", "Art History", "Music Performance", "Philosophy",
            "Chemistry", "Physics", "Mathematics", "Environmental Science", "Journalism",
            "Communications", "Marketing", "Finance", "Accounting", "Graphic Design",
            "Architecture", "Pre-Med", "Pre-Law", "Data Science", "Cybersecurity",
            "Public Health", "International Relations", "Anthropology", "Linguistics",
            "Theater Arts", "Film Studies"
        ]
        self.common_fears = [
            "Academic failure and poor grades", "Student loan debt and financial stress",
            "Finding a job after graduation", "Imposter syndrome in classes",
            "Social anxiety in large lecture halls", "Time management with coursework",
            "Living away from family for the first time", "Public speaking in class",
            "Networking with professionals", "Making new friends", "Balancing social life and studies",
            "Dealing with roommate conflicts", "Homesickness", "Choosing the right career path",
            "Missing deadlines"
        ]
        self.common_goals = [
            "Graduate with honors", "Get accepted to graduate school", "Land a dream internship",
            "Build a strong professional network", "Develop leadership skills", "Study abroad",
            "Start a student organization", "Learn a new language", "Improve public speaking",
            "Get a research position", "Publish a paper", "Secure a full-time job offer",
            "Learn coding and programming", "Improve time management", "Learn about different cultures"
        ]
        self.common_challenges = [
            "Balancing extracurricular activities with studies", "Managing student loans",
            "Dealing with academic pressure", "Preparing for presentations", "Building time management",
            "Overcoming procrastination", "Coping with stress and burnout", "Navigating campus politics",
            "Finding a mentor", "Developing effective study habits", "Dealing with homesickness",
            "Making friends in a new environment", "Adjusting to college workload", "Financial planning",
            "Career exploration"
        ]
        self.common_behaviors = [
            "Studies in the library regularly", "Participates in study groups",
            "Uses campus resources like tutoring", "Attends professor office hours",
            "Joins student clubs and organizations", "Volunteers for campus events",
            "Uses social media for networking", "Attends career fairs", "Goes to campus events",
            "Seeks out leadership roles", "Procrastinates on assignments", "Stays up late studying",
            "Exercises regularly", "Eats at the dining hall", "Calls family frequently"
        ]
        self.social_anxiety_triggers = [
            "Campus social events", "Large lecture halls", "Networking events", "Office hours",
            "Group projects", "Presentations", "Meeting new people", "Job interviews",
            "Dining hall during peak hours", "Fraternity/Sorority events"
        ]

    def generate_personality(self) -> PersonalityProfile:
        return PersonalityProfile(
            extraversion=random.randint(1, 10),
            agreeableness=random.randint(1, 10),
            conscientiousness=random.randint(1, 10),
            neuroticism=random.randint(1, 10),
            openness=random.randint(1, 10)
        )

    def generate_social_anxiety(self) -> SocialAnxietyProfile:
        anxiety_level = random.randint(1, 10)
        social_comfort = random.randint(1, 10)
        communication_style = random.choice(["Direct", "Indirect", "Passive", "Aggressive"])
        triggers = random.sample(self.social_anxiety_triggers, k=random.randint(1, 4))
        return SocialAnxietyProfile(
            anxiety_level=anxiety_level,
            social_comfort=social_comfort,
            communication_style=communication_style,
            triggers=triggers
        )

    def generate_college_student_dummy(self) -> AIDummy:
        student_type = random.choices(["Undergraduate", "Graduate"], weights=[0.65, 0.35], k=1)[0]
        
        if student_type == "Undergraduate":
            age = random.choices(range(17, 23), weights=[1, 5, 5, 5, 3, 1], k=1)[0] # Weighted towards 18-21
        else: # Graduate
            age = random.choices(range(22, 27), weights=[3, 5, 5, 3, 1], k=1)[0] # Weighted towards 22-24

        # FIXED: Gender distribution - 1% non-binary, 49.5% male, 49.5% female
        gender = random.choices(["Male", "Female", "Non-binary"], weights=[49.5, 49.5, 1.0], k=1)[0]
        
        university = random.choice(self.universities)
        major = random.choice(self.majors)

        fears = random.sample(self.common_fears, k=random.randint(2, 4))
        goals = random.sample(self.common_goals, k=random.randint(2, 4))
        challenges = random.sample(self.common_challenges, k=random.randint(2, 4))
        behaviors = random.sample(self.common_behaviors, k=random.randint(3, 5))

        return AIDummy(
            id=str(uuid.uuid4()),
            name=f"{random.choice(['Alex', 'Jordan', 'Taylor', 'Casey', 'Jamie', 'Morgan', 'Dakota', 'Riley', 'Skylar', 'Sofia', 'Zachary', 'Mark', 'Sarah', 'Nancy', 'Lisa', 'Kimberly', 'Gregory', 'Kevin'])} {random.choice(['Smith', 'Jones', 'Williams', 'Brown', 'Davis', 'Miller', 'Wilson', 'Moore', 'Taylor', 'Anderson', 'Thomas', 'Jackson', 'White', 'Harris', 'Martin', 'Thompson', 'Garcia', 'Martinez', 'Robinson', 'Clark', 'Rodriguez', 'Lewis', 'Lee', 'Walker', 'Hall', 'Allen', 'Young', 'Hernandez', 'King', 'Wright', 'Lopez', 'Goldberg', 'Brooks'])}",
            age=age,
            gender=gender,
            university=university,
            major=major,
            student_type=student_type,
            personality=self.generate_personality(),
            social_anxiety=self.generate_social_anxiety(),
            fears=fears,
            goals=goals,
            challenges=challenges,
            behaviors=behaviors
        )

def regenerate_dummies(num_dummies: int = 100, output_file: str = "data/ai_dummies.json"):
    print(f"🎓 Generating {num_dummies} College/Graduate Student Dummies...")
    print("📊 Age range: 17-26 (weighted toward 18-22 for undergrads)")
    print("🏫 Includes both undergraduate and graduate students")
    print("🎯 Fears, goals, and behaviors aligned with student identity")
    print("⚖️  Gender distribution: 49.5% Male, 49.5% Female, 1% Non-binary")

    generator = CharacterGenerator()
    dummies = [generator.generate_college_student_dummy() for _ in range(num_dummies)]

    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump([dummy.model_dump() for dummy in dummies], f, indent=2, ensure_ascii=False, cls=DateTimeEncoder)

    print(f"✅ Generated {num_dummies} college student dummies")
    print(f"📁 Saved to: {output_file}")

    # Basic statistics
    undergrads = sum(1 for d in dummies if d.student_type == "Undergraduate")
    grads = num_dummies - undergrads
    min_age = min(d.age for d in dummies)
    max_age = max(d.age for d in dummies)
    unique_universities = len(set(d.university for d in dummies))
    unique_majors = len(set(d.major for d in dummies))
    
    # Gender statistics
    male_count = sum(1 for d in dummies if d.gender == "Male")
    female_count = sum(1 for d in dummies if d.gender == "Female")
    non_binary_count = sum(1 for d in dummies if d.gender == "Non-binary")

    print("\n📊 Statistics:")
    print(f"   • Undergraduates: {undergrads}")
    print(f"   • Graduate students: {grads}")
    print(f"   • Age range: {min_age}-{max_age}")
    print(f"   • Universities: {unique_universities}")
    print(f"   • Majors: {unique_majors}")
    print(f"   • Gender distribution:")
    print(f"     - Male: {male_count} ({male_count/num_dummies*100:.1f}%)")
    print(f"     - Female: {female_count} ({female_count/num_dummies*100:.1f}%)")
    print(f"     - Non-binary: {non_binary_count} ({non_binary_count/num_dummies*100:.1f}%)")

    # Sample one dummy
    print("\n👤 Sample Dummy:")
    sample_dummy = random.choice(dummies)
    print(f"   Name: {sample_dummy.name}")
    print(f"   Age: {sample_dummy.age} ({sample_dummy.student_type})")
    print(f"   Gender: {sample_dummy.gender}")
    print(f"   University: {sample_dummy.university}")
    print(f"   Major: {sample_dummy.major}")
    print(f"   Top Fear: {sample_dummy.fears[0]}")
    print(f"   Top Goal: {sample_dummy.goals[0]}")

if __name__ == "__main__":
    regenerate_dummies(100)
