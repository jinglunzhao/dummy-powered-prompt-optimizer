"""
Personality Evolution Storage System

Handles saving and loading personality evolution data for web interface visualization.
Stores evolution data per dummy in JSON files with full timeline tracking.
"""

import json
import os
from typing import Dict, List, Optional, Any
from datetime import datetime
from models import PersonalityEvolution, EvolutionStage, AIDummy

class PersonalityEvolutionStorage:
    """Storage service for personality evolution data"""
    
    def __init__(self, data_dir: str = "data/personality_evolution"):
        self.data_dir = data_dir
        os.makedirs(self.data_dir, exist_ok=True)
        print(f"✅ Personality Evolution Storage initialized: {self.data_dir}")
    
    def save_personality_evolution(self, dummy: AIDummy) -> bool:
        """Save personality evolution data for a dummy"""
        if not dummy.personality_evolution:
            return False
        
        try:
            # Convert to dictionary for JSON serialization
            evolution_data = {
                "dummy_id": dummy.personality_evolution.dummy_id,
                "dummy_name": dummy.personality_evolution.dummy_name,
                "current_experiment_id": dummy.personality_evolution.current_experiment_id,
                "current_prompt_id": dummy.personality_evolution.current_prompt_id,
                "created_at": dummy.personality_evolution.created_at.isoformat(),
                "last_updated": dummy.personality_evolution.last_updated.isoformat(),
                
                # Conversation profile data
                "conversation_profile": {
                    # Original traits (static)
                    "original_fears": dummy.personality_evolution.conversation_profile.original_fears,
                    "original_challenges": dummy.personality_evolution.conversation_profile.original_challenges,
                    "original_behaviors": dummy.personality_evolution.conversation_profile.original_behaviors,
                    "original_anxiety_triggers": dummy.personality_evolution.conversation_profile.original_anxiety_triggers,
                    "original_social_anxiety_level": dummy.personality_evolution.conversation_profile.original_social_anxiety_level,
                    "original_big_five": dummy.personality_evolution.conversation_profile.original_big_five.model_dump(),
                    
                    # Current traits (dynamic)
                    "current_fears": dummy.personality_evolution.conversation_profile.current_fears,
                    "current_challenges": dummy.personality_evolution.conversation_profile.current_challenges,
                    "current_behaviors": dummy.personality_evolution.conversation_profile.current_behaviors,
                    "current_anxiety_triggers": dummy.personality_evolution.conversation_profile.current_anxiety_triggers,
                    "current_social_anxiety_level": dummy.personality_evolution.conversation_profile.current_social_anxiety_level,
                    "current_big_five": dummy.personality_evolution.conversation_profile.current_big_five.model_dump(),
                    
                    # Evolution stages
                    "evolution_stages": [
                        {
                            "stage_number": stage.stage_number,
                            "prompt_id": stage.prompt_id,
                            "prompt_name": stage.prompt_name,
                            "generation": stage.generation,
                            "conversation_id": stage.conversation_id,
                            "conversation_summary": stage.conversation_summary,
                            "fears_materialized": stage.fears_materialized,
                            "challenges_materialized": stage.challenges_materialized,
                            "behaviors_detailed": stage.behaviors_detailed,
                            "triggers_specified": stage.triggers_specified,
                            "anxiety_change": stage.anxiety_change,
                            "new_anxiety_level": stage.new_anxiety_level,
                            "pre_assessment_score": stage.pre_assessment_score,
                            "post_assessment_score": stage.post_assessment_score,
                            "improvement_score": stage.improvement_score,
                            "timestamp": stage.timestamp.isoformat()
                        }
                        for stage in dummy.personality_evolution.conversation_profile.evolution_stages
                    ],
                    "current_stage": dummy.personality_evolution.conversation_profile.current_stage
                }
            }
            
            # Save to file
            file_path = os.path.join(self.data_dir, f"{dummy.id}.json")
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(evolution_data, f, indent=2, ensure_ascii=False)
            
            print(f"💾 Saved personality evolution for {dummy.name}: {len(dummy.personality_evolution.conversation_profile.evolution_stages)} stages")
            return True
            
        except Exception as e:
            print(f"⚠️  Failed to save personality evolution for {dummy.name}: {e}")
            return False
    
    def load_personality_evolution(self, dummy_id: str) -> Optional[PersonalityEvolution]:
        """Load personality evolution data for a dummy"""
        try:
            file_path = os.path.join(self.data_dir, f"{dummy_id}.json")
            if not os.path.exists(file_path):
                return None
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Reconstruct evolution stages
            evolution_stages = []
            for stage_data in data["conversation_profile"]["evolution_stages"]:
                stage = EvolutionStage(
                    stage_number=stage_data["stage_number"],
                    prompt_id=stage_data["prompt_id"],
                    prompt_name=stage_data["prompt_name"],
                    generation=stage_data["generation"],
                    conversation_id=stage_data["conversation_id"],
                    conversation_summary=stage_data["conversation_summary"],
                    fears_materialized=stage_data["fears_materialized"],
                    challenges_materialized=stage_data["challenges_materialized"],
                    behaviors_detailed=stage_data["behaviors_detailed"],
                    triggers_specified=stage_data["triggers_specified"],
                    anxiety_change=stage_data["anxiety_change"],
                    new_anxiety_level=stage_data["new_anxiety_level"],
                    pre_assessment_score=stage_data["pre_assessment_score"],
                    post_assessment_score=stage_data["post_assessment_score"],
                    improvement_score=stage_data["improvement_score"],
                    timestamp=datetime.fromisoformat(stage_data["timestamp"])
                )
                evolution_stages.append(stage)
            
            # Reconstruct conversation profile
            from models import ConversationBasedProfile, PersonalityProfile
            
            conversation_profile = ConversationBasedProfile(
                original_fears=data["conversation_profile"]["original_fears"],
                original_challenges=data["conversation_profile"]["original_challenges"],
                original_behaviors=data["conversation_profile"]["original_behaviors"],
                original_anxiety_triggers=data["conversation_profile"]["original_anxiety_triggers"],
                original_social_anxiety_level=data["conversation_profile"]["original_social_anxiety_level"],
                original_big_five=PersonalityProfile(**data["conversation_profile"]["original_big_five"]),
                
                current_fears=data["conversation_profile"]["current_fears"],
                current_challenges=data["conversation_profile"]["current_challenges"],
                current_behaviors=data["conversation_profile"]["current_behaviors"],
                current_anxiety_triggers=data["conversation_profile"]["current_anxiety_triggers"],
                current_social_anxiety_level=data["conversation_profile"]["current_social_anxiety_level"],
                current_big_five=PersonalityProfile(**data["conversation_profile"]["current_big_five"]),
                
                evolution_stages=evolution_stages,
                current_stage=data["conversation_profile"]["current_stage"]
            )
            
            # Reconstruct personality evolution
            personality_evolution = PersonalityEvolution(
                dummy_id=data["dummy_id"],
                dummy_name=data["dummy_name"],
                conversation_profile=conversation_profile,
                current_experiment_id=data["current_experiment_id"],
                current_prompt_id=data["current_prompt_id"],
                created_at=datetime.fromisoformat(data["created_at"]),
                last_updated=datetime.fromisoformat(data["last_updated"])
            )
            
            print(f"📂 Loaded personality evolution for {data['dummy_name']}: {len(evolution_stages)} stages")
            return personality_evolution
            
        except Exception as e:
            print(f"⚠️  Failed to load personality evolution for {dummy_id}: {e}")
            return None
    
    def get_all_evolution_data(self) -> Dict[str, Dict[str, Any]]:
        """Get all personality evolution data for web interface"""
        evolution_data = {}
        
        try:
            for filename in os.listdir(self.data_dir):
                if filename.endswith('.json'):
                    dummy_id = filename[:-5]  # Remove .json extension
                    evolution = self.load_personality_evolution(dummy_id)
                    if evolution:
                        evolution_data[dummy_id] = {
                            "dummy_name": evolution.dummy_name,
                            "timeline": evolution.get_evolution_timeline(),
                            "current_stage": evolution.conversation_profile.current_stage,
                            "total_stages": len(evolution.conversation_profile.evolution_stages),
                            "last_updated": evolution.last_updated.isoformat(),
                            "current_experiment": evolution.current_experiment_id,
                            "current_prompt": evolution.current_prompt_id
                        }
            
            print(f"📊 Loaded evolution data for {len(evolution_data)} dummies")
            return evolution_data
            
        except Exception as e:
            print(f"⚠️  Failed to load all evolution data: {e}")
            return {}
    
    def get_dummy_evolution_timeline(self, dummy_id: str) -> List[Dict[str, Any]]:
        """Get evolution timeline for a specific dummy"""
        evolution = self.load_personality_evolution(dummy_id)
        if evolution:
            return evolution.get_evolution_timeline()
        return []
    
    def delete_evolution_data(self, dummy_id: str) -> bool:
        """Delete evolution data for a dummy"""
        try:
            file_path = os.path.join(self.data_dir, f"{dummy_id}.json")
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"🗑️  Deleted evolution data for dummy {dummy_id}")
                return True
            return False
        except Exception as e:
            print(f"⚠️  Failed to delete evolution data for {dummy_id}: {e}")
            return False

# Global storage instance
personality_evolution_storage = PersonalityEvolutionStorage()

def main():
    """Test the personality evolution storage system"""
    print("Testing Personality Evolution Storage...")
    
    # Test loading all evolution data
    all_data = personality_evolution_storage.get_all_evolution_data()
    print(f"Found evolution data for {len(all_data)} dummies")
    
    for dummy_id, data in all_data.items():
        print(f"  {data['dummy_name']}: {data['total_stages']} evolution stages")

if __name__ == "__main__":
    main()
