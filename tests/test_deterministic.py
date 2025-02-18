import pytest
import random
from src.task import Task
from src.task_system import TaskSystem

# Global shared state to stimulate concurrent access
shared_state = {"X": 0}

def deterministic_task_system():
    # Create a deterministic task system
    def fixed_task():
        return 42  

    tasks = [
        Task("T1", writes=["X"], run=fixed_task),
        Task("T2", writes=["Y"], run=fixed_task),
        Task("T3", reads=["X", "Y"], writes=["Z"], run=fixed_task),
    ]
    
    precedence = {
        "T3": ["T1", "T2"]  
    }

    return TaskSystem(tasks, precedence)

def non_deterministic_task_system():
    # Create a non-deterministic task system
    def random_task():
        shared_state["X"] += random.randint(1, 100)  
        return shared_state["X"]  

    # Both tasks write to X concurrently to create non-determinism
    tasks = [
        Task("T1", writes=["X"], run=random_task),
        Task("T2", writes=["X"], run=random_task),  
    ]
    
    # No precedence constraints to allow for non-determinism
    precedence = {} 

    return TaskSystem(tasks, precedence)

def test_deterministic():
    system = deterministic_task_system()  
    assert system.detTestRnd(nb_trials=5) 

def test_non_deterministic():
    system = non_deterministic_task_system()  
    assert not system.detTestRnd(nb_trials=5)
