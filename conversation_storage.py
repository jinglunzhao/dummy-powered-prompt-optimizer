#!/usr/bin/env python3
"""
Conversation Storage System
Manages conversation data in separate JSON files organized by dummy ID
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
import uuid

class ConversationStorage:
    """Manages conversation storage in separate files by dummy ID"""
    
    def __init__(self, base_dir: str = "data/conversations"):
        self.base_dir = base_dir
        os.makedirs(base_dir, exist_ok=True)
    
    def _get_dummy_file_path(self, dummy_id: str) -> str:
        """Get the file path for a dummy's conversations"""
        return os.path.join(self.base_dir, f"dummy_{dummy_id}.json")
    
    def _generate_conversation_id(self, dummy_id: str, prompt_id: str) -> str:
        """Generate a unique conversation ID"""
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        return f"conv_{timestamp}_{dummy_id[:8]}_{prompt_id[:8]}"
    
    def save_conversation(self, 
                         dummy_id: str, 
                         dummy_name: str,
                         prompt_id: str,
                         prompt_name: str,
                         generation: int,
                         conversation: List[Dict[str, Any]],
                         pre_assessment: Dict[str, Any],
                         post_assessment: Dict[str, Any],
                         improvement: float,
                         reflection_insights: List[str],
                         reflection: str = None) -> str:
        """Save a conversation to the dummy's file"""
        
        # Generate conversation ID
        conversation_id = self._generate_conversation_id(dummy_id, prompt_id)
        
        # Create conversation record
        conversation_record = {
            "conversation_id": conversation_id,
            "timestamp": datetime.now().isoformat(),
            "prompt_id": prompt_id,
            "prompt_name": prompt_name,
            "generation": generation,
            "conversation_rounds": len(conversation),
            "conversation": conversation,
            "pre_assessment": pre_assessment,
            "post_assessment": post_assessment,
            "improvement": improvement,
            "reflection_insights": reflection_insights,
            "reflection": reflection  # Add individual conversation reflection
        }
        
        # Load existing dummy data or create new
        dummy_file = self._get_dummy_file_path(dummy_id)
        if os.path.exists(dummy_file):
            try:
                with open(dummy_file, 'r', encoding='utf-8') as f:
                    dummy_data = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                dummy_data = {
                    "dummy_id": dummy_id,
                    "dummy_name": dummy_name,
                    "conversations": []
                }
        else:
            dummy_data = {
                "dummy_id": dummy_id,
                "dummy_name": dummy_name,
                "conversations": []
            }
        
        # Add new conversation
        dummy_data["conversations"].append(conversation_record)
        
        # Save updated data with proper JSON serialization
        with open(dummy_file, 'w', encoding='utf-8') as f:
            json.dump(dummy_data, f, indent=2, ensure_ascii=False, default=str)
        
        return conversation_id
    
    def get_dummy_conversations(self, dummy_id: str) -> Optional[Dict[str, Any]]:
        """Get all conversations for a specific dummy"""
        dummy_file = self._get_dummy_file_path(dummy_id)
        if not os.path.exists(dummy_file):
            return None
        
        try:
            with open(dummy_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return None
    
    def get_conversation_by_id(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """Find a specific conversation by ID across all dummy files"""
        for filename in os.listdir(self.base_dir):
            if filename.startswith("dummy_") and filename.endswith(".json"):
                dummy_file = os.path.join(self.base_dir, filename)
                try:
                    with open(dummy_file, 'r', encoding='utf-8') as f:
                        content = f.read().strip()
                        if not content:
                            print(f"⚠️  Empty file: {filename}")
                            continue
                        dummy_data = json.loads(content)
                    
                    for conversation in dummy_data.get("conversations", []):
                        if conversation.get("conversation_id") == conversation_id:
                            return conversation
                except (json.JSONDecodeError, FileNotFoundError):
                    continue
        
        return None
    
    def get_conversations_by_prompt(self, prompt_id: str) -> List[Dict[str, Any]]:
        """Get all conversations for a specific prompt across all dummies"""
        conversations = []
        
        for filename in os.listdir(self.base_dir):
            if filename.startswith("dummy_") and filename.endswith(".json"):
                dummy_file = os.path.join(self.base_dir, filename)
                try:
                    with open(dummy_file, 'r', encoding='utf-8') as f:
                        content = f.read().strip()
                        if not content:
                            print(f"⚠️  Empty file: {filename}")
                            continue
                        dummy_data = json.loads(content)
                    
                    for conversation in dummy_data.get("conversations", []):
                        if conversation.get("prompt_id") == prompt_id:
                            # Add dummy info to conversation
                            conversation_with_dummy = conversation.copy()
                            conversation_with_dummy["dummy_id"] = dummy_data["dummy_id"]
                            conversation_with_dummy["dummy_name"] = dummy_data["dummy_name"]
                            conversations.append(conversation_with_dummy)
                except (json.JSONDecodeError, FileNotFoundError):
                    continue
        
        return conversations
    
    def get_all_conversations(self) -> List[Dict[str, Any]]:
        """Get all conversations from all dummy files"""
        all_conversations = []
        
        for filename in os.listdir(self.base_dir):
            if filename.startswith("dummy_") and filename.endswith(".json"):
                dummy_file = os.path.join(self.base_dir, filename)
                try:
                    with open(dummy_file, 'r', encoding='utf-8') as f:
                        content = f.read().strip()
                        if not content:
                            print(f"⚠️  Empty file: {filename}")
                            continue
                        dummy_data = json.loads(content)
                    
                    for conversation in dummy_data.get("conversations", []):
                        # Add dummy info to conversation
                        conversation_with_dummy = conversation.copy()
                        conversation_with_dummy["dummy_id"] = dummy_data["dummy_id"]
                        conversation_with_dummy["dummy_name"] = dummy_data["dummy_name"]
                        all_conversations.append(conversation_with_dummy)
                except (json.JSONDecodeError, FileNotFoundError):
                    continue
        
        return all_conversations
    
    def get_conversation_stats(self) -> Dict[str, Any]:
        """Get statistics about stored conversations"""
        stats = {
            "total_dummies": 0,
            "total_conversations": 0,
            "total_turns": 0,
            "dummies_with_conversations": []
        }
        
        for filename in os.listdir(self.base_dir):
            if filename.startswith("dummy_") and filename.endswith(".json"):
                dummy_file = os.path.join(self.base_dir, filename)
                try:
                    with open(dummy_file, 'r', encoding='utf-8') as f:
                        content = f.read().strip()
                        if not content:
                            print(f"⚠️  Empty file: {filename}")
                            continue
                        dummy_data = json.loads(content)
                    
                    stats["total_dummies"] += 1
                    conversations = dummy_data.get("conversations", [])
                    stats["total_conversations"] += len(conversations)
                    
                    if conversations:
                        stats["dummies_with_conversations"].append({
                            "dummy_id": dummy_data["dummy_id"],
                            "dummy_name": dummy_data["dummy_name"],
                            "conversation_count": len(conversations)
                        })
                    
                    # Count total turns
                    for conversation in conversations:
                        stats["total_turns"] += len(conversation.get("conversation", []))
                        
                except (json.JSONDecodeError, FileNotFoundError):
                    continue
        
        return stats

# Global instance for easy access
conversation_storage = ConversationStorage()
