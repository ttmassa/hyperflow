from src.task import Task
from src.task_system import TaskSystem

# Global variables
X, Y, Z = 0, 0, 0

def deterministic_task_system():
    # Create a deterministic task system
    def runT1():
        global X
        X += 1
    
    def runT2():
        global Y
        Y += 2
    
    def runT3():
        global Z
        Z = X + Y

    tasks = [
        Task("T1", writes=["X"], run=runT1),
        Task("T2", writes=["Y"], run=runT2),
        Task("T3", reads=["X", "Y"], writes=["Z"], run=runT3),
    ]
    
    precedence = {
        "T3": ["T1", "T2"]  
    }

    return TaskSystem(tasks, precedence)

def test_deterministic():
    system = deterministic_task_system()
    assert system.detTestRnd(nb_trials=5, global_vars=globals())