from src.task import Task

def test_task_initialization():
    task = Task(name="test")
    assert task.name == "test"
    assert task.reads == []
    assert task.writes == []
    # Not provided run should be None
    assert task.run == None

def test_task_initialization_with_params():
    task = Task(name="test", reads=["read1", "read2"], writes=["write1", "write2"])
    assert task.name == "test"
    assert task.reads == ["read1", "read2"]
    assert task.writes == ["write1", "write2"]
    assert task.run == None

# Test that the task execute method works
def test_task_execute(capfd):
    task = Task(name="test", run=lambda: print("Task run"))
    task.execute()
    # Capture the output with the capfd fixture from pytest
    out, err = capfd.readouterr()
    assert out == "Task run\n"

def test_task_use():
    # Use the example from the project description
    X = None
    Y = None
    Z = None

    def runT1():
        # Use nonlocal instead of global because X, Y and Z are not defined in the global scope 
        nonlocal X
        X = 1

    def runT2():
        nonlocal Y
        Y = 2

    def runTSomme():
        nonlocal X, Y, Z
        Z = X + Y

    t1 = Task(name="T1", writes=["X"], run=lambda: runT1())
    t2 = Task(name="T2", writes=["Y"], run=lambda: runT2())
    tSomme = Task(name="TSomme", reads=["X", "Y"], writes=["Z"], run=lambda: runTSomme())

    t1.execute()
    t2.execute()
    tSomme.execute()

    assert X == 1
    assert Y == 2
    assert Z == 3