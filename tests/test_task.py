from src.task import Task

def test_task_initialization():
    task = Task(name="test")
    assert task.name == "test"
    # Not provided reads, writes, run should be None
    assert task.reads == None
    assert task.writes == None
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
    