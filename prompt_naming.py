#!/usr/bin/env python3
"""
Civilized Prompt Naming System with Genealogy Tracking
=====================================================

This module provides a clean naming system for prompts that:
1. Uses short, readable names
2. Tracks genealogy through a graph structure
3. Maintains generation information
4. Avoids extremely long names
"""

import uuid
from typing import Dict, List, Optional, Set
from dataclasses import dataclass
from collections import defaultdict

@dataclass
class PromptNode:
    """A node in the prompt genealogy graph"""
    id: str
    name: str
    generation: int
    prompt_type: str  # 'initial', 'mutation', 'crossover'
    parent_ids: List[str]
    children_ids: List[str]
    performance_score: float = 0.0

class PromptGenealogy:
    """Manages prompt genealogy and naming"""
    
    def __init__(self):
        self.nodes: Dict[str, PromptNode] = {}
        self.generation_counts: Dict[int, int] = defaultdict(int)
        self.name_counter = 0
    
    def create_initial_prompt(self, prompt_text: str) -> PromptNode:
        """Create the initial prompt node"""
        prompt_id = str(uuid.uuid4())
        node = PromptNode(
            id=prompt_id,
            name="Genesis",
            generation=0,
            prompt_type="initial",
            parent_ids=[],
            children_ids=[]
        )
        self.nodes[prompt_id] = node
        self.generation_counts[0] = 1
        return node
    
    def create_mutation_prompt(self, parent_id: str, generation: int) -> PromptNode:
        """Create a mutation prompt node"""
        parent = self.nodes[parent_id]
        prompt_id = str(uuid.uuid4())
        
        # Generate elegant name with simplified parent indication
        gen_count = self.generation_counts[generation]
        # Extract just the base name without the full parent chain
        parent_base = parent.name.split(' from ')[0] if ' from ' in parent.name else parent.name
        # Clean up parent name to remove any existing suffixes
        parent_base = parent_base.replace(" (Elite)", "").replace("(Elite)", "").strip()
        name = f"G{generation}M{gen_count:02d} from {parent_base}"
        
        node = PromptNode(
            id=prompt_id,
            name=name,
            generation=generation,
            prompt_type="mutation",
            parent_ids=[parent_id],
            children_ids=[]
        )
        
        # Update parent-child relationships
        parent.children_ids.append(prompt_id)
        self.nodes[prompt_id] = node
        self.generation_counts[generation] += 1
        
        return node
    
    def create_elite_prompt(self, parent_id: str, generation: int) -> PromptNode:
        """Create an elite prompt node (preserved from previous generation)"""
        parent = self.nodes[parent_id]
        prompt_id = str(uuid.uuid4())
        
        # Generate elegant name for elite with simplified parent indication
        gen_count = self.generation_counts[generation]
        # Extract just the base name without the full parent chain
        parent_base = parent.name.split(' from ')[0] if ' from ' in parent.name else parent.name
        # Clean up parent name to remove any existing suffixes
        parent_base = parent_base.replace(" (Elite)", "").replace("(Elite)", "").strip()
        name = f"G{generation}E{gen_count:02d} from {parent_base}"
        
        node = PromptNode(
            id=prompt_id,
            name=name,
            generation=generation,
            prompt_type="elite",
            parent_ids=[parent_id],
            children_ids=[]
        )
        
        # Update parent-child relationships
        parent.children_ids.append(prompt_id)
        self.nodes[prompt_id] = node
        self.generation_counts[generation] += 1
        
        return node
    
    def create_crossover_prompt(self, parent1_id: str, parent2_id: str, generation: int) -> PromptNode:
        """Create a crossover prompt node"""
        parent1 = self.nodes[parent1_id]
        parent2 = self.nodes[parent2_id]
        prompt_id = str(uuid.uuid4())
        
        # Generate elegant name with simplified parent indication
        gen_count = self.generation_counts[generation]
        # Extract just the base names without the full parent chains
        parent1_base = parent1.name.split(' from ')[0] if ' from ' in parent1.name else parent1.name
        parent2_base = parent2.name.split(' from ')[0] if ' from ' in parent2.name else parent2.name
        # Clean up parent names to remove any existing suffixes
        parent1_base = parent1_base.replace(" (Elite)", "").replace("(Elite)", "").strip()
        parent2_base = parent2_base.replace(" (Elite)", "").replace("(Elite)", "").strip()
        name = f"G{generation}C{gen_count:02d} from {parent1_base} & {parent2_base}"
        
        node = PromptNode(
            id=prompt_id,
            name=name,
            generation=generation,
            prompt_type="crossover",
            parent_ids=[parent1_id, parent2_id],
            children_ids=[]
        )
        
        # Update parent-child relationships
        parent1.children_ids.append(prompt_id)
        parent2.children_ids.append(prompt_id)
        self.nodes[prompt_id] = node
        self.generation_counts[generation] += 1
        
        return node
    
    def get_genealogy_path(self, prompt_id: str) -> List[str]:
        """Get the genealogy path from root to this prompt"""
        path = []
        current_id = prompt_id
        
        while current_id in self.nodes:
            node = self.nodes[current_id]
            path.append(f"{node.name}({node.prompt_type})")
            if not node.parent_ids:
                break
            current_id = node.parent_ids[0]  # Follow first parent for simplicity
        
        return list(reversed(path))
    
    def get_family_tree(self, max_depth: int = 3) -> str:
        """Generate a text representation of the family tree"""
        lines = []
        lines.append("🌳 Prompt Genealogy Tree")
        lines.append("=" * 50)
        
        # Find root nodes (generation 0)
        root_nodes = [node for node in self.nodes.values() if node.generation == 0]
        
        for root in root_nodes:
            self._print_subtree(root, lines, 0, max_depth)
        
        return "\n".join(lines)
    
    def _print_subtree(self, node: PromptNode, lines: List[str], depth: int, max_depth: int):
        """Recursively print subtree"""
        if depth > max_depth:
            return
        
        indent = "  " * depth
        lines.append(f"{indent}├─ {node.name} (G{node.generation}, {node.prompt_type})")
        
        # Sort children by generation, then by name
        children = sorted([self.nodes[child_id] for child_id in node.children_ids], 
                         key=lambda x: (x.generation, x.name))
        
        for child in children:
            self._print_subtree(child, lines, depth + 1, max_depth)
    
    def get_prompt_summary(self, prompt_id: str) -> Dict:
        """Get a summary of a prompt including its genealogy"""
        if prompt_id not in self.nodes:
            return {}
        
        node = self.nodes[prompt_id]
        return {
            "id": prompt_id,
            "name": node.name,
            "generation": node.generation,
            "type": node.prompt_type,
            "parents": [self.nodes[pid].name for pid in node.parent_ids if pid in self.nodes],
            "children_count": len(node.children_ids),
            "genealogy_path": self.get_genealogy_path(prompt_id),
            "performance_score": node.performance_score
        }

# Global genealogy tracker
genealogy_tracker = PromptGenealogy()

def get_civilized_name(prompt_type: str, generation: int, parent_ids: List[str] = None) -> str:
    """Get a civilized name for a prompt"""
    if prompt_type == "initial":
        return "Genesis"
    elif prompt_type == "mutation":
        gen_count = genealogy_tracker.generation_counts[generation]
        return f"G{generation}M{gen_count:02d}"
    elif prompt_type == "crossover":
        gen_count = genealogy_tracker.generation_counts[generation]
        return f"G{generation}C{gen_count:02d}"
    else:
        return f"Unknown_{generation}_{uuid.uuid4().hex[:8]}"
