from src.task_system import TaskSystem
from src.task import Task

def test_task_system_initialization():
    task1 = Task(name="T1")
    task2 = Task(name="T2")
    precedence = {"T2": ["T1"]}
    task_system = TaskSystem(tasks=[task1, task2], precedence=precedence)
    
    assert task_system.tasks["T1"] == task1
    assert task_system.tasks["T2"] == task2
    assert task_system.precedence == precedence

def test_task_system_get_dependencies():
    task1 = Task(name="T1")
    task2 = Task(name="T2")
    precedence = {"T2": ["T1"]}
    task_system = TaskSystem(tasks=[task1, task2], precedence=precedence)
    
    assert task_system.getDependencies("T2") == ["T1"]
    assert task_system.getDependencies("T1") == []

def test_task_system_run_seq():
    X = None
    Y = None

    def runT1():
        nonlocal X
        X = 1

    def runT2():
        nonlocal Y
        Y = 2

    task1 = Task(name="T1", writes=["X"], run=lambda: runT1())
    task2 = Task(name="T2", writes=["Y"], run=lambda: runT2())
    precedence = {"T2": ["T1"]}
    task_system = TaskSystem(tasks=[task1, task2], precedence=precedence)
    
    task_system.runSeq()
    
    assert X == 1
    assert Y == 2

def test_task_system_run():
    X = None
    Y = None

    def runT1():
        nonlocal X
        X = 1

    def runT2():
        nonlocal Y
        Y = 2

    task1 = Task(name="T1", writes=["X"], run=lambda: runT1())
    task2 = Task(name="T2", writes=["Y"], run=lambda: runT2())
    precedence = {"T2": ["T1"]}
    task_system = TaskSystem(tasks=[task1, task2], precedence=precedence)
    
    task_system.run()
    
    assert X == 1
    assert Y == 2