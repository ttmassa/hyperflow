from src.task_system import TaskSystem
from src.task import Task

def test_task_system_initialization():
    # Basic test to check if the TaskSystem is initialized correctly
    task1 = Task(name="T1")
    task2 = Task(name="T2")
    precedence = {"T2": ["T1"]}
    task_system = TaskSystem(tasks=[task1, task2], precedence=precedence)
    
    assert task_system.tasks["T1"] == task1
    assert task_system.tasks["T2"] == task2
    assert task_system.precedence == precedence

def test_task_system_initialization_empty_names():
    task1 = Task(name="T1")
    task2 = Task(name="")
    precedence = {"T2": ["T1"]}

    try:
        # Attempt to initialize TaskSystem with empty task names
        TaskSystem(tasks=[task1, task2], precedence=precedence)
        assert False
    except ValueError as e:
        assert str(e) == "Task name cannot be empty"

def test_task_system_initialization_duplicate_names():
    # Test if the TaskSystem raises an error when duplicate task names are detected
    task1 = Task(name="T1")
    task2 = Task(name="T1")
    
    try:
        # Attempt to initialize TaskSystem with duplicate task names
        TaskSystem(tasks=[task1, task2], precedence={})
        assert False
    except ValueError as e:
        assert str(e) == "Duplicate task names detected"

def test_task_system_check_circular_dependencies():
    # Test if the TaskSystem raises an error when circular dependencies are detected
    task1 = Task(name="T1")
    task2 = Task(name="T2")
    precedence = {"T2": ["T1"], "T1": ["T2"]}
    
    try:
        # Attempt to initialize TaskSystem with circular dependencies
        TaskSystem(tasks=[task1, task2], precedence=precedence)
        assert False
    except Exception as e:
        assert str(e) == "Circular dependency detected: Task 'T1' is part of a cycle."

def test_task_system_check_missing_tasks():
    # Test if the TaskSystem raises an error when missing tasks are detected in the dependencies
    task1 = Task(name="T1")
    task2 = Task(name="T2")
    precedence = {"T2": ["T1"], "T3": ["T1"]}
    
    try:
        # Attempt to initialize TaskSystem with missing dependencies
        TaskSystem(tasks=[task1, task2], precedence=precedence)
        assert False
    except ValueError as e:
        assert str(e) == "Missing task detected: Task 'T3' is listed in dependencies but does not exist."

def test_task_system_check_missing_dependencies():
    # Test if the TaskSystem raises an error when missing dependencies are detected
    task1 = Task(name="T1")
    task2 = Task(name="T2")
    precedence = {"T2": ["T3"]}
    
    try:
        # Attempt to initialize TaskSystem with missing dependencies
        TaskSystem(tasks=[task1, task2], precedence=precedence)
        assert False
    except ValueError as e:
        assert str(e) == "Missing dependency detected: Task 'T2' depends on 'T3' which does not exist."

def test_task_system_get_dependencies():
    # Test the getDependencies method
    task1 = Task(name="T1")
    task2 = Task(name="T2")
    precedence = {"T2": ["T1"]}
    task_system = TaskSystem(tasks=[task1, task2], precedence=precedence)
    
    assert task_system.getDependencies("T2") == ["T1"]
    assert task_system.getDependencies("T1") == []

def test_task_system_run_seq():
    # Test the runSeq method
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
    # Test the run method
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