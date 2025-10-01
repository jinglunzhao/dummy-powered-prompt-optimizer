#!/usr/bin/env python3
"""
Test Personality Materialization

Tests the personality materialization system to identify and fix API issues.
"""

import asyncio
import json
from models import AIDummy, PersonalityProfile, SocialAnxietyProfile, Conversation, ConversationTurn
from personality_materializer import personality_materializer

async def test_materialization():
    print('🧬 TESTING PERSONALITY MATERIALIZATION')
    print('=' * 50)
    
    # Create test dummy
    dummy = AIDummy(
        name='MaterializationTest',
        age=20,
        gender='female',
        major='Psychology',
        university='Test University',
        student_type='undergraduate',
        personality=PersonalityProfile(
            extraversion=4,
            agreeableness=7,
            conscientiousness=6,
            neuroticism=7,
            openness=6
        ),
        social_anxiety=SocialAnxietyProfile(
            anxiety_level=7,
            communication_style='hesitant',
            triggers=['large groups', 'presentations'],
            social_comfort=3
        ),
        fears=['being ignored', 'saying wrong things'],
        challenges=['joining discussions', 'asking questions'],
        behaviors=['staying quiet', 'avoiding eye contact'],
        goals=['build confidence', 'participate more']
    )
    
    # Create test conversation
    conversation = Conversation(
        id='test-conversation',
        dummy_id=dummy.id,
        scenario='Social skills coaching session',
        system_prompt='You are a helpful social skills coach.',
        turns=[
            ConversationTurn(
                speaker='dummy',
                message='I really struggle with speaking up in class discussions. I have ideas but I\'m afraid of saying something wrong.',
                timestamp='2025-01-01T10:00:00'
            ),
            ConversationTurn(
                speaker='ai',
                message='I understand that fear. Many students feel this way. What specifically makes you worried about speaking up?',
                timestamp='2025-01-01T10:01:00'
            ),
            ConversationTurn(
                speaker='dummy',
                message='I guess I\'m worried that my ideas aren\'t good enough or that I\'ll look stupid in front of everyone.',
                timestamp='2025-01-01T10:02:00'
            ),
            ConversationTurn(
                speaker='ai',
                message='That\'s a very common concern. Let\'s work on building your confidence step by step. What if we started with asking one clarifying question per class?',
                timestamp='2025-01-01T10:03:00'
            )
        ]
    )
    
    print(f'📝 Test Dummy: {dummy.name}')
    print(f'💬 Test Conversation: {len(conversation.turns)} turns')
    print()
    
    # Test 1: Check materialization prompt creation
    print('1. Testing materialization prompt creation...')
    try:
        prompt = personality_materializer._create_materialization_prompt(dummy, conversation)
        print(f'   ✅ Prompt created: {len(prompt)} characters')
        print(f'   📊 Contains dummy data: {"social rejection" in prompt.lower()}')
        print(f'   📊 Contains conversation: {"speaking up" in prompt.lower()}')
    except Exception as e:
        print(f'   ❌ Prompt creation failed: {e}')
        return
    
    # Test 2: Test API call directly
    print('2. Testing materialization API call...')
    try:
        evolution_stage = await personality_materializer.materialize_personality_from_conversation(
            dummy=dummy,
            conversation=conversation,
            prompt_id='test_prompt',
            prompt_name='Test Prompt',
            generation=1,
            pre_assessment_score=2.0,
            post_assessment_score=2.5
        )
        
        if evolution_stage:
            print(f'   ✅ Materialization successful!')
            print(f'   📊 Stage number: {evolution_stage.stage_number}')
            print(f'   📝 Summary: {evolution_stage.conversation_summary[:50]}...')
            print(f'   😰 Anxiety change: {evolution_stage.anxiety_change}')
            print(f'   🎯 New anxiety level: {evolution_stage.new_anxiety_level}')
            print(f'   📈 Improvement: {evolution_stage.improvement_score}')
            
            # Show materialized traits
            if evolution_stage.fears_materialized:
                print(f'   🔥 Fears materialized: {len(evolution_stage.fears_materialized)}')
                for original, evolved in evolution_stage.fears_materialized.items():
                    print(f'      "{original}" → "{evolved}"')
            
            if evolution_stage.challenges_materialized:
                print(f'   🎯 Challenges materialized: {len(evolution_stage.challenges_materialized)}')
                for original, evolved in evolution_stage.challenges_materialized.items():
                    print(f'      "{original}" → "{evolved}"')
        else:
            print(f'   ❌ Materialization returned None')
            
    except Exception as e:
        print(f'   ❌ Materialization failed: {e}')
        import traceback
        traceback.print_exc()
    
    print('=' * 50)

if __name__ == "__main__":
    asyncio.run(test_materialization())
