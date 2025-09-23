"""
Conversation Simulator for AI Dummy Social Skills Testing
Manages interactions between AI dummies and AI models
"""
import json
import os
import time
import random
import asyncio
import aiohttp
from typing import List, Dict, Any, Optional
from datetime import datetime
from openai import OpenAI
from models import AIDummy, Conversation, ConversationTurn, SystemPrompt
from config import Config

class ConversationSimulator:
    """Simulates conversations between AI dummies and AI models"""
    
    def __init__(self, api_key: str = None):
        """Initialize the conversation simulator"""
        self.api_key = api_key or Config.OPENAI_API_KEY
        if self.api_key:
            # Initialize OpenAI client for DeepSeek Chat
            self.client = OpenAI(
                api_key=self.api_key,
                base_url="https://api.deepseek.com"
            )
            print("✅ DeepSeek Chat API configured successfully!")
        else:
            print("Warning: No API key provided. Conversations will be simulated.")
            self.client = None
        
        self.conversations = []
        self.scenarios = Config.CONVERSATION_SCENARIOS
    
    async def simulate_conversation_async(self, dummy: AIDummy, 
                                        scenario: str = None, 
                                        num_rounds: int = None,
                                        custom_system_prompt: str = None) -> Conversation:
        """Simulate a conversation between a dummy and AI model"""
        if scenario is None:
            scenario = random.choice(self.scenarios)
        
        if num_rounds is None:
            num_rounds = Config.CONVERSATION_ROUNDS
        
        # Create conversation
        system_prompt_text = custom_system_prompt or Config.SYSTEM_PROMPT
        conversation = Conversation(
            dummy_id=dummy.id,
            scenario=scenario,
            system_prompt=system_prompt_text,
            turns=[]  # Initialize empty turns list
        )
        
        # Generate initial context
        context = self._generate_conversation_context(dummy, scenario)
        
        # Start conversation
        conversation.add_turn("dummy", context["initial_message"], context)
        
        # Simulate conversation rounds
        for round_num in range(num_rounds):
            # AI response
            ai_response = await self._generate_ai_response_async(conversation, system_prompt_text, dummy)
            
            # Handle the new AI response format
            if isinstance(ai_response, dict) and "ai_reasoning" in ai_response:
                # New format with reasoning and final response
                ai_metadata = {
                    "round": round_num + 1,
                    "ai_reasoning": ai_response["ai_reasoning"],
                    "ai_final_response": ai_response["ai_final_response"]
                }
                conversation.add_turn("ai", ai_response["message"], ai_metadata)
            else:
                # Fallback to old format (simulated response)
                conversation.add_turn("ai", ai_response, {"round": round_num + 1})
            
            # Dummy response
            dummy_response = self._generate_dummy_response(conversation, dummy, scenario, round_num + 1)
            conversation.add_turn("dummy", dummy_response, {"round": round_num + 1})
        
        # End conversation
        conversation.end_time = datetime.now()
        conversation.duration_seconds = (conversation.end_time - conversation.start_time).total_seconds()
        
        return conversation
    
    def _generate_conversation_context(self, dummy: AIDummy, scenario: str) -> Dict[str, Any]:
        """Generate realistic conversation context based on dummy and scenario"""
        context = {
            "scenario": scenario,
            "dummy_personality": dummy.personality.dict(),
            "dummy_anxiety": dummy.social_anxiety.dict(),
            "dummy_goals": dummy.goals,
            "dummy_challenges": dummy.challenges
        }
        
        # Generate initial message based on scenario and dummy
        if "party" in scenario.lower():
            context["initial_message"] = self._generate_party_message(dummy)
        elif "directions" in scenario.lower():
            context["initial_message"] = self._generate_directions_message(dummy)
        elif "group conversation" in scenario.lower():
            context["initial_message"] = self._generate_group_message(dummy)
        elif "presentation" in scenario.lower():
            context["initial_message"] = self._generate_presentation_message(dummy)
        elif "conflict" in scenario.lower():
            context["initial_message"] = self._generate_conflict_message(dummy)
        elif "small talk" in scenario.lower():
            context["initial_message"] = self._generate_small_talk_message(dummy)
        elif "date" in scenario.lower():
            context["initial_message"] = self._generate_date_message(dummy)
        elif "networking" in scenario.lower():
            context["initial_message"] = self._generate_networking_message(dummy)
        elif "criticism" in scenario.lower():
            context["initial_message"] = self._generate_criticism_message(dummy)
        elif "disagreement" in scenario.lower():
            context["initial_message"] = self._generate_disagreement_message(dummy)
        else:
            context["initial_message"] = self._generate_generic_message(dummy, scenario)
        
        return context
    
    def _generate_party_message(self, dummy: AIDummy) -> str:
        """Generate party-related initial message"""
        anxiety_level = dummy.social_anxiety.anxiety_level
        extraversion = dummy.personality.extraversion
        
        if anxiety_level >= 7 and extraversion <= 4:
            return f"Hi, I'm {dummy.name}. I'm not really good at these things, but I'm trying to meet new people. Do you mind if I join your conversation?"
        elif anxiety_level >= 5:
            return f"Hello! I'm {dummy.name}. This is my first time at one of these events. I'm a bit nervous but excited to meet people. How are you enjoying the party?"
        else:
            return f"Hey there! I'm {dummy.name}. I love meeting new people at parties like this. What brings you here tonight?"
    
    def _generate_directions_message(self, dummy: AIDummy) -> str:
        """Generate directions-related initial message"""
        anxiety_level = dummy.social_anxiety.anxiety_level
        
        if anxiety_level >= 7:
            return f"Um, excuse me... I'm sorry to bother you, but I'm lost and I really need help finding my way. Could you possibly give me directions?"
        elif anxiety_level >= 5:
            return f"Hi, I'm sorry to interrupt, but I'm looking for the library and I'm not sure which way to go. Could you help me?"
        else:
            return f"Hi there! I'm looking for the library. Do you know which direction it's in?"
    
    def _generate_group_message(self, dummy: AIDummy) -> str:
        """Generate group conversation message"""
        anxiety_level = dummy.social_anxiety.anxiety_level
        extraversion = dummy.personality.extraversion
        
        if anxiety_level >= 7 and extraversion <= 4:
            return f"Hi everyone. I'm {dummy.name}. I hope it's okay if I join in. I'm not always great at group conversations, but I'm trying to improve."
        elif anxiety_level >= 5:
            return f"Hello! I'm {dummy.name}. I was listening to your discussion about [topic] and it sounds really interesting. Mind if I join?"
        else:
            return f"Hey! I'm {dummy.name}. I couldn't help but overhear your conversation about [topic]. I'd love to hear more about that!"
    
    def _generate_presentation_message(self, dummy: AIDummy) -> str:
        """Generate presentation-related message"""
        anxiety_level = dummy.social_anxiety.anxiety_level
        
        if anxiety_level >= 7:
            return f"I have to give a presentation tomorrow and I'm absolutely terrified. I keep thinking about all the things that could go wrong. How do people do this?"
        elif anxiety_level >= 5:
            return f"I'm giving a presentation next week and I'm feeling pretty nervous about it. Do you have any tips for managing presentation anxiety?"
        else:
            return f"I'm preparing for a presentation and I want to make sure it goes really well. What are your best strategies for engaging an audience?"
    
    def _generate_conflict_message(self, dummy: AIDummy) -> str:
        """Generate conflict-related message"""
        agreeableness = dummy.personality.agreeableness
        neuroticism = dummy.personality.neuroticism
        
        if agreeableness <= 4 and neuroticism >= 7:
            return f"I'm really frustrated with my colleague. They keep undermining my work and I'm not sure how to handle it without making things worse."
        elif agreeableness <= 4:
            return f"I have a disagreement with my coworker about a project approach. I want to stand my ground but also maintain a good working relationship."
        else:
            return f"I'm in a difficult situation with a colleague where we have different opinions. I want to resolve it constructively. Any advice?"
    
    def _generate_small_talk_message(self, dummy: AIDummy) -> str:
        """Generate small talk message"""
        extraversion = dummy.personality.extraversion
        anxiety_level = dummy.social_anxiety.anxiety_level
        
        if extraversion <= 4 and anxiety_level >= 5:
            return f"Hi, I'm {dummy.name}. I'm your new neighbor. I'm not great at small talk, but I wanted to introduce myself."
        elif extraversion <= 4:
            return f"Hello! I'm {dummy.name}, your new neighbor. I hope we can get to know each other. How long have you lived here?"
        else:
            return f"Hey there! I'm {dummy.name}, your new neighbor. I love this area! What's your favorite thing about living here?"
    
    def _generate_date_message(self, dummy: AIDummy) -> str:
        """Generate dating-related message"""
        anxiety_level = dummy.social_anxiety.anxiety_level
        extraversion = dummy.personality.extraversion
        
        if anxiety_level >= 7:
            return f"I really like this person I've been talking to, but I'm so nervous about asking them out. What if they say no? What if the date is awkward?"
        elif anxiety_level >= 5:
            return f"I want to ask someone out, but I'm not sure how to do it naturally. I don't want to come across as too forward or too hesitant."
        else:
            return f"I'm interested in asking someone out and I want to make a good impression. What are some good first date ideas?"
    
    def _generate_networking_message(self, dummy: AIDummy) -> str:
        """Generate networking message"""
        anxiety_level = dummy.social_anxiety.anxiety_level
        extraversion = dummy.personality.extraversion
        
        if anxiety_level >= 7 and extraversion <= 4:
            return f"I'm at this networking event and I feel completely out of place. Everyone seems to know each other and I don't know how to start conversations."
        elif anxiety_level >= 5:
            return f"I'm trying to network for my career, but I find these events really intimidating. How do you approach people you don't know?"
        else:
            return f"I'm here to network and make professional connections. What's your approach to making meaningful connections at events like this?"
    
    def _generate_criticism_message(self, dummy: AIDummy) -> str:
        """Generate criticism-related message"""
        neuroticism = dummy.personality.neuroticism
        anxiety_level = dummy.social_anxiety.anxiety_level
        
        if neuroticism >= 7 and anxiety_level >= 6:
            return f"I received some feedback at work today and I can't stop thinking about it. I feel like I'm not good enough and I'm worried about my job."
        elif neuroticism >= 6:
            return f"I got some constructive criticism today and I'm having trouble processing it. I know it's meant to help, but it still stings."
        else:
            return f"I received some feedback that I want to use to improve, but I'm not sure how to implement the suggestions effectively."
    
    def _generate_disagreement_message(self, dummy: AIDummy) -> str:
        """Generate disagreement message"""
        agreeableness = dummy.personality.agreeableness
        extraversion = dummy.personality.extraversion
        
        if agreeableness <= 4 and extraversion >= 7:
            return f"I strongly disagree with my friend's political views, but I don't want to ruin our friendship. How do I express my opinion respectfully?"
        elif agreeableness <= 4:
            return f"I have a different opinion than my colleague on an important decision. I want to advocate for my position without creating conflict."
        else:
            return f"I find myself disagreeing with someone I respect, and I want to have a constructive discussion about our different perspectives."
    
    def _generate_generic_message(self, dummy: AIDummy, scenario: str) -> str:
        """Generate generic message for unspecified scenarios"""
        anxiety_level = dummy.social_anxiety.anxiety_level
        
        if anxiety_level >= 7:
            return f"Hi, I'm {dummy.name}. I'm not really sure how to start this conversation, but I'm trying to work on my social skills."
        elif anxiety_level >= 5:
            return f"Hello! I'm {dummy.name}. I'm working on improving my communication skills, so I thought I'd practice with you."
        else:
            return f"Hi there! I'm {dummy.name}. I'm always looking to learn and grow, so I'd love to hear your thoughts on [topic]."
    
    async def _generate_ai_response_async(self, conversation: Conversation, system_prompt: str, 
                                        dummy: AIDummy) -> str:
        """Generate AI response using DeepSeek R1 API or simulation"""
        if self.client:
            try:
                return await self._call_openai_api_async(conversation, system_prompt, dummy)
            except Exception as e:
                print(f"DeepSeek R1 API call failed: {e}. Falling back to simulation.")
                return self._simulate_ai_response(conversation, dummy)
        else:
            return self._simulate_ai_response(conversation, dummy)
    
    async def _call_openai_api_async(self, conversation: Conversation, system_prompt: str, 
                                   dummy: AIDummy) -> str:
        """Call DeepSeek R1 API to generate response"""
        # Use the custom system prompt or fall back to default
        if system_prompt and len(system_prompt.strip()) > 50:
            simple_prompt = system_prompt
        else:
            simple_prompt = f"""You are a supportive AI assistant helping students improve their social skills.

Your role: Respond directly to the student in a warm, encouraging way. Give practical advice and help build confidence.

Keep responses:
- Conversational and natural
- Under 150 words
- Practical and actionable
- Focused on the student's specific situation

Do NOT analyze the conversation or explain your approach. Just respond naturally as a helpful mentor."""
        
        # Prepare conversation history
        messages = [
            {"role": "system", "content": simple_prompt},
            {"role": "user", "content": f"Student: {dummy.get_character_summary()}"},
            {"role": "user", "content": f"Scenario: {conversation.scenario}"}
        ]
        
        # Add conversation history
        for turn in conversation.turns[-6:]:  # Last 6 turns for context
            role = "assistant" if turn.speaker == "ai" else "user"
            messages.append({"role": role, "content": turn.message})
        
        # Generate response using DeepSeek Chat (non-thinking mode) with aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.deepseek.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "deepseek-chat",
                    "messages": messages,
                    "max_tokens": 200,
                    "temperature": 0.7
                }
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    response_data = result
                else:
                    raise Exception(f"API call failed with status {response.status}")
        
        # Get the response content from DeepSeek Chat
        message = response_data['choices'][0]['message']
        
        # Extract response content - deepseek-chat only has content field
        if 'content' in message and message['content'] and len(message['content'].strip()) > 20:
            ai_final_response = message['content'].strip()
            print(f"✅ Using deepseek-chat: {len(ai_final_response)} chars")
        else:
            print("❌ No usable response, falling back to simulation")
            return self._simulate_ai_response(conversation, dummy)
        
        # Clean up the response - remove any remaining meta-analysis language
        ai_final_response = self._clean_ai_response(ai_final_response)
        
        # No reasoning_content with deepseek-chat, so we'll use a simplified reasoning
        ai_reasoning = f"Response generated using deepseek-chat model for {dummy.name} in {conversation.scenario}"
        
        print(f"🎯 Final AI Response: {len(ai_final_response)} chars")
        
        return {
            "ai_reasoning": ai_reasoning,
            "ai_final_response": ai_final_response,
            "message": ai_final_response  # This is what the dummy will hear
        }
    
    def _clean_ai_response(self, response: str) -> str:
        """Clean up AI response to remove meta-analysis and make it conversational"""
        # Remove common meta-analysis phrases
        meta_phrases = [
            "hmm, this is a social anxiety scenario",
            "the user wants",
            "i should",
            "first, i need to",
            "next, i'll",
            "finally, i'll",
            "the response should",
            "make sure the response",
            "structure it as",
            "avoid sounding scripted",
            "keep the tone",
            "the goal is to",
            "hmm, the user is",
            "the user provided",
            "i notice the user",
            "the user emphasized",
            "the user mentioned",
            "the user reiterated"
        ]
        
        cleaned = response
        for phrase in meta_phrases:
            if phrase.lower() in cleaned.lower():
                # Find where this phrase starts and remove everything before it
                start_idx = cleaned.lower().find(phrase.lower())
                if start_idx > 0:
                    # Look for the next sentence or natural break
                    next_sentence = cleaned[start_idx:].find('.')
                    if next_sentence > 0:
                        cleaned = cleaned[start_idx + next_sentence + 1:].strip()
                    else:
                        cleaned = cleaned[start_idx:].strip()
        
        # Remove any remaining meta-analysis at the beginning
        if cleaned.lower().startswith(('hmm,', 'okay,', 'first,', 'next,', 'finally,')):
            # Find the first period and start from there
            first_period = cleaned.find('.')
            if first_period > 0:
                cleaned = cleaned[first_period + 1:].strip()
        
        # Ensure the response starts with a proper sentence
        if cleaned and not cleaned[0].isupper():
            # Find the first capital letter
            for i, char in enumerate(cleaned):
                if char.isupper():
                    cleaned = cleaned[i:]
                    break
        
        return cleaned.strip()
    
    def _simulate_ai_response(self, conversation: Conversation, dummy: AIDummy) -> str:
        """Simulate AI response when API is not available"""
        # Get the last dummy message
        last_dummy_message = None
        for turn in reversed(conversation.turns):
            if turn.speaker == "dummy":
                last_dummy_message = turn.message
                break
        
        if not last_dummy_message:
            return "Hello! I'm here to help you with your social skills. How can I assist you today?"
        
        # Generate contextual response based on dummy's message and profile
        anxiety_level = dummy.social_anxiety.anxiety_level
        extraversion = dummy.personality.extraversion
        
        # Response templates based on message content and dummy profile
        if "nervous" in last_dummy_message.lower() or "anxious" in last_dummy_message.lower():
            if anxiety_level >= 7:
                return "I can see you're feeling quite anxious, and that's completely normal. Let's take this step by step. What specific aspect of this situation is most challenging for you?"
            else:
                return "It's natural to feel some nervousness in new situations. What would help you feel more comfortable right now?"
        
        elif "help" in last_dummy_message.lower():
            return "I'm here to help! Let me understand your situation better. What specific support do you need?"
        
        elif "practice" in last_dummy_message.lower():
            return "That's a great approach! Practice is key to building confidence. What would you like to practice first?"
        
        elif "confidence" in last_dummy_message.lower():
            if extraversion <= 4:
                return "Building confidence takes time, especially for introverts. Let's identify small wins you can celebrate. What's one social interaction that went well recently?"
            else:
                return "Confidence comes from preparation and experience. What specific skills would you like to strengthen?"
        
        elif "?" in last_dummy_message:
            # Respond to questions
            if "how" in last_dummy_message.lower():
                return "Great question! Let me share some practical strategies. First, let's break this down into smaller, manageable steps."
            elif "what" in last_dummy_message.lower():
                return "That's an important consideration. Let me help you think through this systematically."
            else:
                return "I appreciate you asking that. Let me provide some guidance based on your situation."
        
        else:
            # Generic supportive response
            responses = [
                "I hear what you're saying, and I want to help you work through this.",
                "That sounds challenging, but I believe you have the ability to handle this situation.",
                "Let's work together to find a solution that works for you.",
                "I appreciate you sharing this with me. What would be most helpful for you right now?",
                "This is a great opportunity for growth. Let's explore some strategies together."
            ]
            return random.choice(responses)
    
    def _generate_dummy_response(self, conversation: Conversation, dummy: AIDummy, 
                               scenario: str, round_num: int) -> str:
        """Generate AI-powered dummy response based on character profile and conversation context"""
        # Get the last AI message
        last_ai_message = None
        for turn in reversed(conversation.turns):
            if turn.speaker == "ai":
                last_ai_message = turn.message
                break
        
        if not last_ai_message:
            return "Thank you for your help. I'm not sure what to say next."
        
        # Use AI to generate a response that matches the dummy's character
        if self.client:
            try:
                return self._generate_ai_dummy_response(conversation, dummy, scenario, round_num)
            except Exception as e:
                print(f"AI dummy response generation failed: {e}. Falling back to simulation.")
                return self._simulate_dummy_response(conversation, dummy, scenario, round_num)
        else:
            return self._simulate_dummy_response(conversation, dummy, scenario, round_num)
    
    def _generate_ai_dummy_response(self, conversation: Conversation, dummy: AIDummy, 
                                  scenario: str, round_num: int) -> str:
        """Generate AI-powered response that matches the dummy's character profile"""
        
        # Get the last AI message
        last_ai_message = None
        for turn in reversed(conversation.turns):
            if turn.speaker == "ai":
                last_ai_message = turn.message
                break
        
        if not last_ai_message:
            return "Thank you for your help. I'm not sure what to say next."
        
        # Create a character-specific system prompt for the dummy
        character_prompt = self._create_character_prompt(dummy, scenario, round_num)
        
        # Prepare conversation context
        messages = [
            {"role": "system", "content": character_prompt},
            {"role": "user", "content": f"Your conversation partner just said: '{last_ai_message}'"}
        ]
        
        # Add recent conversation history for context (last 4 turns)
        recent_turns = conversation.turns[-4:] if len(conversation.turns) >= 4 else conversation.turns
        for turn in recent_turns:
            if turn.speaker == "dummy":
                messages.append({"role": "assistant", "content": turn.message})
            else:
                messages.append({"role": "user", "content": turn.message})
        
        # Generate response using DeepSeek Chat (non-thinking mode)
        response = self.client.chat.completions.create(
            model="deepseek-chat",  # Use non-thinking mode for direct character responses
            messages=messages,
            max_tokens=100,  # Shorter responses for dummies
            temperature=0.8   # More creative variation
        )
        
        message = response.choices[0].message
        
        # Extract the response content - deepseek-chat only has content field
        if hasattr(message, 'content') and message.content:
            return message.content.strip()
        else:
            # Fallback to simulation
            return self._simulate_dummy_response(conversation, dummy, scenario, round_num)
    
    def _create_character_prompt(self, dummy: AIDummy, scenario: str, round_num: int) -> str:
        """Create a character prompt for the dummy's AI response generation"""
        
        # Get personality traits
        personality = dummy.personality
        anxiety = dummy.social_anxiety
        
        # Create anxiety description
        if anxiety.anxiety_level >= 7:
            anxiety_desc = "You have SEVERE social anxiety. You're extremely nervous, overthink everything, and often freeze up in social situations."
        elif anxiety.anxiety_level >= 5:
            anxiety_desc = "You have MODERATE social anxiety. You feel nervous and uncertain in social situations, but you're trying to improve."
        else:
            anxiety_desc = "You have LOW social anxiety. You're generally comfortable in social situations, though you still want to improve your skills."
        
        # Create personality description
        personality_desc = f"""You are {dummy.name}, a {dummy.age}-year-old {dummy.student_type} studying {dummy.major} at {dummy.university}. 

Your personality:
- Extraversion: {personality.extraversion}/10 - {'Very outgoing and social' if personality.extraversion >= 7 else 'Moderately social' if personality.extraversion >= 4 else 'Introverted and reserved'}
- Agreeableness: {personality.agreeableness}/10 - {'Very cooperative and trusting' if personality.agreeableness >= 7 else 'Moderately agreeable' if personality.agreeableness >= 4 else 'More competitive and skeptical'}
- Conscientiousness: {personality.conscientiousness}/10 - {'Very organized and careful' if personality.conscientiousness >= 7 else 'Moderately organized' if personality.conscientiousness >= 4 else 'More spontaneous and flexible'}
- Neuroticism: {personality.neuroticism}/10 - {'Very sensitive to stress' if personality.neuroticism >= 7 else 'Moderately sensitive' if personality.neuroticism >= 4 else 'Very emotionally stable'}
- Openness: {personality.openness}/10 - {'Very creative and curious' if personality.openness >= 7 else 'Moderately open' if personality.openness >= 4 else 'More traditional and practical'}

{anxiety_desc}
Your triggers: {', '.join(anxiety.triggers)}
Your communication style: {anxiety.communication_style}

Current scenario: {scenario}

INSTRUCTIONS:
1. Respond as {dummy.name} would naturally speak
2. Show your personality traits and anxiety level
3. Keep responses under 30 words and conversational
4. Respond to what the AI just said
5. Stay in character - be {dummy.name}, not an actor playing {dummy.name}"""
        
        return personality_desc.strip()
    
    def _simulate_dummy_response(self, conversation: Conversation, dummy: AIDummy, 
                               scenario: str, round_num: int) -> str:
        """Fallback simulation when AI generation fails"""
        # Get the last AI message
        last_ai_message = None
        for turn in reversed(conversation.turns):
            if turn.speaker == "ai":
                last_ai_message = turn.message
                break
        
        if not last_ai_message:
            return "Thank you for your help. I'm not sure what to say next."
        
        # Generate response based on dummy's personality and the AI's message
        anxiety_level = dummy.social_anxiety.anxiety_level
        extraversion = dummy.personality.extraversion
        agreeableness = dummy.personality.agreeableness
        
        # More dynamic response generation based on conversation context
        if "?" in last_ai_message:
            # AI asked a question - respond based on personality
            if anxiety_level >= 7:
                responses = [
                    "I'm not sure... I tend to overthink things.",
                    "That's a good question. Let me think about it.",
                    "I want to answer honestly, but I'm worried about saying the wrong thing.",
                    "Can you give me a moment to process that?",
                    "I'm trying to figure out the best way to respond."
                ]
            elif anxiety_level >= 5:
                responses = [
                    "I think I know what you mean, but I want to make sure.",
                    "That's an interesting point. Let me reflect on it.",
                    "I'm still learning, so I might need some clarification.",
                    "I want to give you a thoughtful answer.",
                    "Can you help me understand this better?"
                ]
            else:
                responses = [
                    "I have some thoughts on that. Let me share them.",
                    "That's a great question! Here's what I think.",
                    "I've been thinking about this too. My perspective is...",
                    "I'm excited to discuss this with you.",
                    "I have some ideas that might be helpful."
                ]
        else:
            # AI gave advice/guidance - respond based on personality and anxiety
            if anxiety_level >= 7:
                # High anxiety responses - more varied and realistic
                responses = [
                    "That sounds helpful, but I'm worried I won't be able to do it right.",
                    "I appreciate your advice, but I'm not sure I'm ready for this.",
                    "Can you break this down into even smaller steps? I'm feeling overwhelmed.",
                    "What if people think I'm weird or awkward?",
                    "I'm still feeling really nervous about this. What if I mess up?",
                    "That makes sense in theory, but I'm scared I'll freeze up in the moment.",
                    "I want to try, but my anxiety keeps telling me I'll fail.",
                    "Can you give me some specific phrases I can practice?",
                    "I'm worried that even with practice, I'll still be awkward.",
                    "What if someone asks me a question I can't answer?"
                ]
            elif anxiety_level >= 5:
                # Moderate anxiety responses
                responses = [
                    "I think I can try that, but I'm still a bit nervous.",
                    "That makes sense. Maybe I can start with something small?",
                    "I want to improve, but I'm not sure where to start.",
                    "Can you give me an example of how to do this?",
                    "I'm willing to try, but I might need some encouragement.",
                    "That sounds doable. How long do you think it will take to feel comfortable?",
                    "I like the approach, but I'm worried about the first few attempts.",
                    "Can you suggest a way to practice this safely?",
                    "I'm optimistic but also realistic about my current abilities.",
                    "What should I do if I start feeling overwhelmed while trying this?"
                ]
            else:
                # Low anxiety responses
                responses = [
                    "That's a great idea! I can definitely try that approach.",
                    "I'm excited to put this into practice. What's the next step?",
                    "This makes a lot of sense. I can see how it would help.",
                    "I'm ready to take on this challenge. Any other tips?",
                    "That's exactly what I needed to hear. Thank you!",
                    "I can already see how this will improve my social interactions.",
                    "This approach feels natural to me. I'm confident I can do it.",
                    "I appreciate the practical advice. When should I start?",
                    "I'm looking forward to seeing the results of this strategy.",
                    "This gives me a clear roadmap. I'm ready to begin."
                ]
        
        # Add some personality-based variations
        if extraversion <= 3:
            responses.extend([
                "I prefer to think things through before acting.",
                "I'm more comfortable with one-on-one interactions.",
                "I need time to process before responding."
            ])
        
        if agreeableness >= 7:
            responses.extend([
                "I really appreciate you taking the time to help me.",
                "Your advice feels very supportive and understanding.",
                "I feel heard and validated by your response."
            ])
        
        # Select response and add some natural variation
        base_response = random.choice(responses)
        
        # Add contextual elements based on the scenario
        if "party" in scenario.lower():
            base_response = base_response.replace("this", "parties").replace("situation", "social gatherings")
        elif "presentation" in scenario.lower():
            base_response = base_response.replace("this", "presentations").replace("situation", "public speaking")
        elif "neighbor" in scenario.lower():
            base_response = base_response.replace("this", "casual conversations").replace("situation", "neighbor interactions")
        
        return base_response
    
    def save_conversation(self, conversation: Conversation, filename: str = None):
        """Save conversation to JSON file"""
        if filename is None:
            filename = os.path.join(Config.DATA_DIR, Config.CONVERSATIONS_FILE)
        
        # Create data directory if it doesn't exist
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        # Load existing conversations or create new list
        existing_conversations = []
        if os.path.exists(filename):
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if content:  # Only try to parse if file has content
                        existing_conversations = json.loads(content)
            except (json.JSONDecodeError, ValueError):
                print(f"⚠️ Corrupted conversations file detected, starting fresh")
                existing_conversations = []
        
        # Add new conversation
        conversation_data = conversation.dict()
        existing_conversations.append(conversation_data)
        
        # Save updated file
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(existing_conversations, f, indent=2, default=str, ensure_ascii=False)
        
        print(f"💾 Saved conversation {conversation.id} for dummy {conversation.dummy_id}")
    
    def load_conversations(self, filename: str = None) -> List[Conversation]:
        """Load conversations from JSON file"""
        if filename is None:
            filename = os.path.join(Config.DATA_DIR, Config.CONVERSATIONS_FILE)
        
        if not os.path.exists(filename):
            print(f"File {filename} not found. No conversations available.")
            return []
        
        with open(filename, 'r', encoding='utf-8') as f:
            conversations_data = json.load(f)
        
        conversations = [Conversation(**conv_data) for conv_data in conversations_data]
        print(f"Loaded {len(conversations)} conversations from {filename}")
        return conversations

def main():
    """Test the conversation simulator"""
    print("Testing Conversation Simulator...")
    
    # This would typically be used with actual dummies and system prompts
    # For testing, we'll create sample data
    from character_generator import CharacterGenerator
    
    generator = CharacterGenerator()
    dummy = generator.generate_character()
    
    system_prompt = SystemPrompt(
        name="Basic Social Skills Helper",
        prompt="You are a supportive AI assistant helping students improve their social skills. Be encouraging, provide practical advice, and help them build confidence gradually.",
        version="1.0"
    )
    
    print(f"Generated test dummy: {dummy.name}")
    print(f"Anxiety level: {dummy.social_anxiety.get_anxiety_category()}")
    
    # Create conversation simulator
    simulator = ConversationSimulator()
    
    # Simulate conversation
    conversation = simulator.simulate_conversation(dummy, system_prompt, num_rounds=3)
    
    print(f"\nSimulated conversation with {len(conversation.turns)} turns")
    print(f"Scenario: {conversation.scenario}")
    print(f"Duration: {conversation.duration_seconds:.1f} seconds")
    
    # Print conversation
    print("\nConversation:")
    for turn in conversation.turns:
        speaker = "AI Assistant" if turn.speaker == "ai" else "Student"
        print(f"{speaker}: {turn.message}")
    
    print("\nConversation simulation test complete!")

if __name__ == "__main__":
    main()
