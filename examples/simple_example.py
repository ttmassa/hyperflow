import sys
import os
import time

# Add the parent directory to the path to be able to import the classes
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.task import Task
from src.task_system import TaskSystem


# Simple example of the execution time difference between a sequential and parallel task system
# To avoid the overhead of creating threads, we need to add a sleep in the run function of the tasks 
X = 0
Y = 0
Z = None

def runT1():
    global X
    time.sleep(0.5)
    X += 1

def runT2():
    global Y
    time.sleep(0.5)
    Y += 2

def runTSomme():
    global X, Y, Z
    time.sleep(0.5)
    Z = X + Y

t1 = Task(name="T1", writes=["X"], run=lambda: runT1())
t2 = Task(name="T2", writes=["X"], run=lambda: runT1())
t3 = Task(name="T3", writes=["Y"], run=lambda: runT2())
t4 = Task(name="T4", writes=["Y"], run=lambda: runT2())
tSomme = Task(name="TSomme", reads=["X", "Y"], writes=["Z"], run=lambda: runTSomme())
tFinal = Task(name="TFinal", reads=["Z"], run=lambda: None)

task_system = TaskSystem([t1, t2, t3, t4, tSomme, tFinal], {"T2": ["T1"], "T4": ["T3"], "TSomme": ["T2", "T4"], "TFinal": ["TSomme"]})

print("Comparing execution times...")
task_system.parCost(runs=1)