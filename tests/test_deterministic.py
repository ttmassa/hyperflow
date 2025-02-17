import pytest
from src.task import Task
from src.task_system import TaskSystem

def test_deterministic():
    X = 0
    Y = 0
    Z = None

    def runT1():
        nonlocal X
        X += 1

    def runT2():
        nonlocal Y
        Y += 2

    def runTSomme():
        nonlocal X, Y, Z
        Z = X + Y

    tasks = [
        Task(name="Task1", reads=[], writes=["X"], run=lambda: runT1()),
        Task(name="Task2", reads=[], writes=["Y"], run=lambda: runT2()),
        Task(name="Task3", reads=["X", "Y"], writes=["Z"], run=lambda: runTSomme())
    ]
    precedence = {
        "Task2": ["Task1"],
        "Task3": ["Task2"]
    }
    task_system = TaskSystem(tasks, precedence)

    assert task_system.detTestRnd(runs=5) 