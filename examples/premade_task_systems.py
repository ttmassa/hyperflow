import sys
import os

# Add the parent directory to the path to be able to import the classes
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.task import Task
from src.task_system import TaskSystem
import random
import time

def random_task_system():
    def random_result():
        time.sleep(0.01)
        return {"value": random.randint(1, 100)}
    
    # Generate a random number of tasks
    nbr_tasks = random.randint(5, 10)

    tasks = []
    domain_choice = ["X", "Y", "Z"]
    for i in range(nbr_tasks):
        reads = random.choices(domain_choice, k=random.randint(0, 1))
        writes = random.choices(domain_choice, k=random.randint(0, 1))
        tasks.append(Task(name=f"T{i}", reads=reads, writes=writes, run=random_result))

    precedence = {}

    for i in range(nbr_tasks):
        # Randomly select the number of tasks that the current task will depend on
        nbr_dependencies = random.randint(0, i)
        dependencies = random.sample(range(i), nbr_dependencies)
        precedence[f"T{i}"] = [f"T{dep}" for dep in dependencies]

    return TaskSystem(tasks, precedence)

def simple_task_system():
    def simple_result():
        time.sleep(0.01)
        return {"value": random.randint(1, 100)}

    tasks = [
        Task(name="T1", reads=["A", "F"], writes=["B"], run=simple_result),
        Task(name="T2", reads=["F"], writes=["D"], run=simple_result),
        Task(name="T3", reads=["B", "C"], writes=[], run=simple_result),
        Task(name="T4", reads=["B", "D"], writes=["A", "F"], run=simple_result),
        Task(name="T5", reads=["E"], writes=["C", "E"], run=simple_result),
        Task(name="T6", reads=["A"], writes=["B"], run=simple_result)
    ]
    precedence = {
        "T1": [],
        "T2": ["T1"],
        "T3": ["T1"],
        "T4": ["T2", "T3"],
        "T5": ["T3"],
        "T6": ["T4", "T5"]
    }

    return TaskSystem(tasks, precedence)

def fibonacci_task_system():
    def fibonacci(n):
        time.sleep(0.001)
        if n <= 1:
            return n
        else:
            return fibonacci(n-1) + fibonacci(n-2)

    tasks = [Task(name=f"T{i}", run=lambda i=i: fibonacci(i)) for i in range(8)]
    precedence = {f"T{i}": [f"T{i-1}", f"T{i-2}"] for i in range(2, 8)}

    return TaskSystem(tasks, precedence)

def factorial_task_system():
    def factorial(n):
        time.sleep(0.001)
        if n == 0:
            return 1
        else:
            return n * factorial(n-1)

    tasks = [Task(name=f"T{i}", run=lambda i=i: factorial(i)) for i in range(8)]
    precedence = {f"T{i}": [f"T{i-1}"] for i in range(1, 8)}

    return TaskSystem(tasks, precedence)