import sys
import os

# Add the parent directory to the path to be able to import the classes
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.task import Task
from src.task_system import TaskSystem


# Simple example of how a task system can be represented as a graph
X = 0
Y = 0
Z = None

def runT1():
    global X
    X += 1

def runT2():
    global Y
    Y += 2

def runTSomme():
    global X, Y, Z
    Z = X + Y

t1 = Task(name="T1", writes=["X"], run=lambda: runT1())
t2 = Task(name="T2", writes=["X"], run=lambda: runT1())
t3 = Task(name="T3", writes=["Y"], run=lambda: runT2())
t4 = Task(name="T4", writes=["Y"], run=lambda: runT2())
tSomme = Task(name="TSomme", reads=["X", "Y"], writes=["Z"], run=lambda: runTSomme())
tFinal = Task(name="TFinal", reads=["Z"], run=lambda: print(f"Final result: Z = {Z}"))

task_system = TaskSystem([t1, t2, t3, t4, tSomme, tFinal], {"T2": ["T1"], "T4": ["T3"], "TSomme": ["T2", "T4"], "TFinal": ["TSomme"]})

def generate_graph():
    print("Executing Task System...")
    task_system.run()
    print("Drawing Dependency Graph...")
    task_system.draw()
    print("Draw function executed successfully.")

if __name__ == "__main__":
    generate_graph()