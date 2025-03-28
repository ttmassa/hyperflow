import sys
import os

# Add the parent directory to the path to be able to import the classes
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.task import Task
from src.task_system import TaskSystem
import random
import time
import numpy as np

A, B, C, D, E, F = 0, 0, 0, 0, 0, 0

def simple_task_system():
    def simple_result():
        # Mimic some computation time
        time.sleep(0.1)
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

    return TaskSystem(tasks, precedence), globals()

def fibonacci_task_system():
    def fibonacci(n):
        # Mimic some computation time
        time.sleep(0.01)
        if n <= 1:
            return n
        else:
            return fibonacci(n-1) + fibonacci(n-2)

    tasks = [Task(name=f"T{i}", run=lambda i=i: fibonacci(i)) for i in range(8)]
    precedence = {f"T{i}": [f"T{i-1}", f"T{i-2}"] for i in range(2, 8)}

    return TaskSystem(tasks, precedence), globals()

def matrix_multiplication_task_system():
    def multiply_matrices(A, B):
        # Mimic some computation time
        time.sleep(0.5)
        return np.dot(A, B)

    A = np.random.rand(2, 2)
    B = np.random.rand(2, 2)
    C = np.random.rand(2, 2)

    tasks = [
        Task(name="T1", writes=["A"], run=lambda: A),
        Task(name="T2", writes=["B"], run=lambda: B),
        Task(name="T3", reads=["A", "B"], writes=["C"], run=lambda: multiply_matrices(A, B)),
        Task(name="T4", reads=["C"], writes=["D"], run=lambda: multiply_matrices(C, A))
    ]
    precedence = {
        "T1": [],
        "T2": [],
        "T3": ["T1", "T2"],
        "T4": ["T3"]
    }

    return TaskSystem(tasks, precedence), globals()