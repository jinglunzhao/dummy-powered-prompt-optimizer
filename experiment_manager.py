#!/usr/bin/env python3
"""
Experiment Result Management System
==================================

This module provides proper management of experiment results:
1. Timestamped file naming
2. Version control
3. Experiment metadata
4. Result archiving
5. Easy retrieval and comparison
"""

import json
import os
import shutil
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path
import uuid

class ExperimentManager:
    """Manages experiment results with proper versioning and archiving"""
    
    def __init__(self, base_dir: str = "data/experiments"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(exist_ok=True)
        
        # Create subdirectories
        self.results_dir = self.base_dir / "results"
        self.archives_dir = self.base_dir / "archives"
        self.metadata_dir = self.base_dir / "metadata"
        
        for dir_path in [self.results_dir, self.archives_dir, self.metadata_dir]:
            dir_path.mkdir(exist_ok=True)
    
    def create_experiment(self, 
                         experiment_name: str,
                         config: Dict[str, Any],
                         description: str = "") -> str:
        """Create a new experiment with unique ID"""
        
        experiment_id = str(uuid.uuid4())[:8]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        experiment_info = {
            "experiment_id": experiment_id,
            "name": experiment_name,
            "timestamp": timestamp,
            "description": description,
            "config": config,
            "status": "running",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        # Save metadata
        metadata_file = self.metadata_dir / f"{experiment_id}_{timestamp}.json"
        with open(metadata_file, 'w') as f:
            json.dump(experiment_info, f, indent=2)
        
        print(f"🧪 Created experiment: {experiment_name}")
        print(f"   📁 ID: {experiment_id}")
        print(f"   📅 Timestamp: {timestamp}")
        print(f"   📄 Metadata: {metadata_file}")
        
        return experiment_id
    
    def save_experiment_result(self, 
                              experiment_id: str,
                              result_data: Dict[str, Any],
                              status: str = "completed") -> str:
        """Save experiment results with proper naming"""
        
        # Find the experiment metadata
        metadata_file = self._find_metadata_file(experiment_id)
        if not metadata_file:
            raise ValueError(f"Experiment {experiment_id} not found")
        
        # Load metadata
        with open(metadata_file, 'r') as f:
            metadata = json.load(f)
        
        # Update status and timestamp
        metadata["status"] = status
        metadata["updated_at"] = datetime.now().isoformat()
        metadata["result_file"] = f"result_{experiment_id}_{metadata['timestamp']}.json"
        
        # Save updated metadata
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        # Save result data
        result_file = self.results_dir / metadata["result_file"]
        with open(result_file, 'w') as f:
            json.dump(result_data, f, indent=2)
        
        print(f"💾 Saved experiment result: {result_file}")
        print(f"   📊 Status: {status}")
        print(f"   📁 Size: {result_file.stat().st_size / 1024 / 1024:.1f} MB")
        
        return str(result_file)
    
    def archive_experiment(self, experiment_id: str) -> str:
        """Archive an experiment to the archives directory"""
        
        metadata_file = self._find_metadata_file(experiment_id)
        if not metadata_file:
            raise ValueError(f"Experiment {experiment_id} not found")
        
        # Load metadata
        with open(metadata_file, 'r') as f:
            metadata = json.load(f)
        
        # Create archive directory
        archive_dir = self.archives_dir / f"{experiment_id}_{metadata['timestamp']}"
        archive_dir.mkdir(exist_ok=True)
        
        # Copy files
        shutil.copy2(metadata_file, archive_dir / "metadata.json")
        
        if "result_file" in metadata:
            result_file = self.results_dir / metadata["result_file"]
            if result_file.exists():
                shutil.copy2(result_file, archive_dir / "result.json")
        
        # Update metadata
        metadata["archived_at"] = datetime.now().isoformat()
        metadata["archive_path"] = str(archive_dir)
        
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"📦 Archived experiment: {archive_dir}")
        return str(archive_dir)
    
    def list_experiments(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all experiments, optionally filtered by status"""
        
        experiments = []
        
        for metadata_file in self.metadata_dir.glob("*.json"):
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
            
            if status is None or metadata.get("status") == status:
                experiments.append(metadata)
        
        # Sort by creation time (newest first)
        experiments.sort(key=lambda x: x["created_at"], reverse=True)
        
        return experiments
    
    def get_experiment_result(self, experiment_id: str) -> Optional[Dict[str, Any]]:
        """Get experiment result data"""
        
        metadata_file = self._find_metadata_file(experiment_id)
        if not metadata_file:
            return None
        
        with open(metadata_file, 'r') as f:
            metadata = json.load(f)
        
        if "result_file" not in metadata:
            return None
        
        result_file = self.results_dir / metadata["result_file"]
        if not result_file.exists():
            return None
        
        with open(result_file, 'r') as f:
            return json.load(f)
    
    def compare_experiments(self, experiment_ids: List[str]) -> Dict[str, Any]:
        """Compare multiple experiments"""
        
        comparison = {
            "experiments": [],
            "summary": {},
            "best_performance": None,
            "best_experiment": None
        }
        
        best_score = 0
        
        for exp_id in experiment_ids:
            result = self.get_experiment_result(exp_id)
            if not result:
                continue
            
            # Extract key metrics
            metrics = {
                "experiment_id": exp_id,
                "dummies": result.get("test_config", {}).get("dummies_count", 0),
                "rounds": result.get("test_config", {}).get("conversation_rounds", 0),
                "generations": result.get("test_config", {}).get("generations", 0),
                "duration_minutes": result.get("test_config", {}).get("duration_seconds", 0) / 60,
                "pareto_solutions": len(result.get("optimization", {}).get("pareto_frontier", [])),
                "best_improvement": 0
            }
            
            # Get best improvement
            pareto = result.get("optimization", {}).get("pareto_frontier", [])
            if pareto:
                metrics["best_improvement"] = pareto[0].get("performance_metrics", {}).get("avg_improvement", 0)
            
            comparison["experiments"].append(metrics)
            
            # Track best performance
            if metrics["best_improvement"] > best_score:
                best_score = metrics["best_improvement"]
                comparison["best_performance"] = metrics["best_improvement"]
                comparison["best_experiment"] = exp_id
        
        # Generate summary
        comparison["summary"] = {
            "total_experiments": len(comparison["experiments"]),
            "best_improvement": best_score,
            "avg_improvement": sum(exp["best_improvement"] for exp in comparison["experiments"]) / len(comparison["experiments"]) if comparison["experiments"] else 0,
            "total_duration_hours": sum(exp["duration_minutes"] for exp in comparison["experiments"]) / 60
        }
        
        return comparison
    
    def _find_metadata_file(self, experiment_id: str) -> Optional[Path]:
        """Find metadata file for experiment ID"""
        
        for metadata_file in self.metadata_dir.glob("*.json"):
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
            
            if metadata.get("experiment_id") == experiment_id:
                return metadata_file
        
        return None
    
    def cleanup_old_results(self, days_old: int = 30):
        """Clean up old result files (keep metadata)"""
        
        cutoff_date = datetime.now().timestamp() - (days_old * 24 * 60 * 60)
        cleaned_count = 0
        
        for result_file in self.results_dir.glob("*.json"):
            if result_file.stat().st_mtime < cutoff_date:
                result_file.unlink()
                cleaned_count += 1
        
        print(f"🧹 Cleaned up {cleaned_count} old result files (>{days_old} days old)")

# Global experiment manager
experiment_manager = ExperimentManager()

def create_experiment(experiment_name: str, config: Dict[str, Any], description: str = "") -> str:
    """Create a new experiment"""
    return experiment_manager.create_experiment(experiment_name, config, description)

def save_experiment_result(experiment_id: str, result_data: Dict[str, Any], status: str = "completed") -> str:
    """Save experiment results"""
    return experiment_manager.save_experiment_result(experiment_id, result_data, status)

def list_experiments(status: Optional[str] = None) -> List[Dict[str, Any]]:
    """List experiments"""
    return experiment_manager.list_experiments(status)

def compare_experiments(experiment_ids: List[str]) -> Dict[str, Any]:
    """Compare experiments"""
    return experiment_manager.compare_experiments(experiment_ids)
