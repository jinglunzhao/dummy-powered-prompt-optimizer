#!/usr/bin/env python3
"""
Advanced Parallel Processing for GEPA System
===========================================

This module implements full parallel processing for:
1. All prompts in each generation (not just individual prompt testing)
2. Crossover and mutation operations
3. Assessment and conversation simulation
4. Result collection and analysis
"""

import asyncio
import aiohttp
import time
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
import logging

logger = logging.getLogger(__name__)

@dataclass
class ParallelTask:
    """Represents a task to be executed in parallel"""
    task_id: str
    task_type: str  # 'crossover', 'mutation', 'assessment', 'conversation'
    prompt_id: str
    data: Dict[str, Any]
    priority: int = 0  # Higher number = higher priority

class ParallelProcessor:
    """Advanced parallel processor for GEPA operations"""
    
    def __init__(self, max_concurrent_tasks: int = 10):
        self.max_concurrent_tasks = max_concurrent_tasks
        self.semaphore = asyncio.Semaphore(max_concurrent_tasks)
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        """Async context manager entry"""
        connector = aiohttp.TCPConnector(limit=100, limit_per_host=30)
        timeout = aiohttp.ClientTimeout(total=60)
        self.session = aiohttp.ClientSession(connector=connector, timeout=timeout)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def process_generation_parallel(self, 
                                        population: List[Any], 
                                        dummies: List[Any],
                                        generation: int,
                                        crossover_rate: float = 0.6,
                                        mutation_rate: float = 0.3) -> List[Any]:
        """Process an entire generation in parallel"""
        
        print(f"🚀 Starting parallel processing for generation {generation}")
        print(f"   📊 Population: {len(population)} prompts")
        print(f"   👥 Dummies: {len(dummies)}")
        
        # Create all tasks for this generation
        tasks = []
        
        # 1. Assessment tasks (test all prompts with all dummies)
        for prompt in population:
            for dummy in dummies:
                task = ParallelTask(
                    task_id=f"assess_{prompt.id}_{dummy.id}",
                    task_type="assessment",
                    prompt_id=prompt.id,
                    data={"prompt": prompt, "dummy": dummy}
                )
                tasks.append(task)
        
        # 2. Evolution tasks (crossover and mutation)
        evolution_tasks = await self._create_evolution_tasks(
            population, generation, crossover_rate, mutation_rate
        )
        tasks.extend(evolution_tasks)
        
        print(f"   🎯 Total tasks: {len(tasks)}")
        print(f"   ⚡ Concurrent limit: {self.max_concurrent_tasks}")
        
        # Execute all tasks in parallel
        results = await self._execute_tasks_parallel(tasks)
        
        # Process results
        new_population = await self._process_results(results, population, generation)
        
        print(f"   ✅ Generation {generation} completed: {len(new_population)} prompts")
        return new_population
    
    async def _create_evolution_tasks(self, 
                                    population: List[Any], 
                                    generation: int,
                                    crossover_rate: float,
                                    mutation_rate: float) -> List[ParallelTask]:
        """Create evolution tasks (crossover and mutation)"""
        tasks = []
        
        # Calculate how many new prompts we need
        target_size = min(2 ** generation, 20)  # Exponential growth, capped at 20
        current_size = len(population)
        needed = max(0, target_size - current_size)
        
        if needed == 0:
            return tasks
        
        # Create crossover tasks
        crossover_count = int(needed * crossover_rate)
        for i in range(crossover_count):
            if len(population) >= 2:
                # Select two different parents
                parent1, parent2 = self._select_parents(population)
                task = ParallelTask(
                    task_id=f"crossover_{i}_{generation}",
                    task_type="crossover",
                    prompt_id="new",
                    data={"parent1": parent1, "parent2": parent2, "generation": generation}
                )
                tasks.append(task)
        
        # Create mutation tasks
        mutation_count = needed - crossover_count
        for i in range(mutation_count):
            if population:
                parent = self._select_parent_for_mutation(population)
                task = ParallelTask(
                    task_id=f"mutation_{i}_{generation}",
                    task_type="mutation",
                    prompt_id="new",
                    data={"parent": parent, "generation": generation}
                )
                tasks.append(task)
        
        return tasks
    
    def _select_parents(self, population: List[Any]) -> Tuple[Any, Any]:
        """Select two different parents for crossover"""
        import random
        if len(population) < 2:
            return population[0], population[0]
        
        parent1, parent2 = random.sample(population, 2)
        return parent1, parent2
    
    def _select_parent_for_mutation(self, population: List[Any]) -> Any:
        """Select a parent for mutation"""
        import random
        return random.choice(population)
    
    async def _execute_tasks_parallel(self, tasks: List[ParallelTask]) -> List[Dict[str, Any]]:
        """Execute all tasks in parallel with controlled concurrency"""
        
        # Group tasks by type for better organization
        task_groups = {
            "assessment": [t for t in tasks if t.task_type == "assessment"],
            "crossover": [t for t in tasks if t.task_type == "crossover"],
            "mutation": [t for t in tasks if t.task_type == "mutation"]
        }
        
        all_results = []
        
        # Process each group with appropriate concurrency
        for task_type, group_tasks in task_groups.items():
            if not group_tasks:
                continue
                
            print(f"   🔄 Processing {len(group_tasks)} {task_type} tasks...")
            
            # Create coroutines for this group
            coroutines = [self._execute_single_task(task) for task in group_tasks]
            
            # Execute with controlled concurrency
            group_results = await asyncio.gather(*coroutines, return_exceptions=True)
            
            # Filter out exceptions and collect results
            for i, result in enumerate(group_results):
                if isinstance(result, Exception):
                    logger.error(f"Task {group_tasks[i].task_id} failed: {result}")
                else:
                    all_results.append(result)
        
        return all_results
    
    async def _execute_single_task(self, task: ParallelTask) -> Dict[str, Any]:
        """Execute a single task with semaphore control"""
        async with self.semaphore:
            try:
                if task.task_type == "assessment":
                    return await self._execute_assessment_task(task)
                elif task.task_type == "crossover":
                    return await self._execute_crossover_task(task)
                elif task.task_type == "mutation":
                    return await self._execute_mutation_task(task)
                else:
                    raise ValueError(f"Unknown task type: {task.task_type}")
            except Exception as e:
                logger.error(f"Task {task.task_id} failed: {e}")
                return {"task_id": task.task_id, "error": str(e), "success": False}
    
    async def _execute_assessment_task(self, task: ParallelTask) -> Dict[str, Any]:
        """Execute an assessment task"""
        # This would call your existing assessment logic
        # For now, return a placeholder
        return {
            "task_id": task.task_id,
            "task_type": "assessment",
            "prompt_id": task.prompt_id,
            "success": True,
            "result": "assessment_placeholder"
        }
    
    async def _execute_crossover_task(self, task: ParallelTask) -> Dict[str, Any]:
        """Execute a crossover task"""
        # This would call your existing crossover logic
        # For now, return a placeholder
        return {
            "task_id": task.task_id,
            "task_type": "crossover",
            "prompt_id": task.prompt_id,
            "success": True,
            "result": "crossover_placeholder"
        }
    
    async def _execute_mutation_task(self, task: ParallelTask) -> Dict[str, Any]:
        """Execute a mutation task"""
        # This would call your existing mutation logic
        # For now, return a placeholder
        return {
            "task_id": task.task_id,
            "task_type": "mutation",
            "prompt_id": task.prompt_id,
            "success": True,
            "result": "mutation_placeholder"
        }
    
    async def _process_results(self, 
                             results: List[Dict[str, Any]], 
                             population: List[Any], 
                             generation: int) -> List[Any]:
        """Process the results and create new population"""
        # This would process the results and create new prompts
        # For now, return the original population
        return population

# Usage example
async def run_parallel_generation(population, dummies, generation):
    """Example of how to use the parallel processor"""
    async with ParallelProcessor(max_concurrent_tasks=10) as processor:
        new_population = await processor.process_generation_parallel(
            population=population,
            dummies=dummies,
            generation=generation,
            crossover_rate=0.6,
            mutation_rate=0.3
        )
        return new_population
