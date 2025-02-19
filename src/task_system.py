import threading
import networkx as nx
import matplotlib.pyplot as plt
from src.task import Task
import numpy as np
import random
import time

class TaskSystem:
    def __init__(self, tasks, precedence):
        # Use task name as key for easy access
        self.tasks = {task.name: task for task in tasks}
        # Dictionary of task dependencies
        self.precedence = precedence

        # Check for duplicate task names
        # Dictionary overwrites duplicates keys so we just need to compare its length with the number of tasks
        if len(self.tasks) != len(tasks):
            raise ValueError("Duplicate task names detected")

        # Check for empty task names
        self.checkEmptyTaskNames()

        # Check for circular dependencies
        self.checkCircularDependencies()

        # Check for missing dependencies
        self.checkMissingDependencies()

    # The Task constructor already ensures that a name is provided but why not check it again 
    def checkEmptyTaskNames(self):
        for task_name in self.tasks.keys():
            if not task_name:
                raise ValueError("Task name cannot be empty")
            
    def checkCircularDependencies(self):
        visited = set()
        rec_stack = set()

        # Depth-first search to detect circular dependencies
        def dfs(task_name):
            # Task is already in the current path being explored so circular dependency
            if task_name in rec_stack:
                raise Exception(f"Circular dependency detected: Task '{task_name}' is part of a cycle.")
            
            if task_name in visited:
                return
            
            visited.add(task_name)
            rec_stack.add(task_name)

            for dep in self.getDependencies(task_name):
                dfs(dep)
            # Remove the task from the current path
            rec_stack.remove(task_name)

        # Outer loop
        for task_name in self.tasks.keys():
            if task_name not in visited:
                dfs(task_name)
            
    def checkMissingDependencies(self):
        # Loop through all tasks and check if they depend on tasks that do not exist
        for task_name, deps in self.precedence.items():
            # Task does not exist so useless 
            if task_name not in self.tasks:
                raise ValueError(f"Missing task detected: Task '{task_name}' is listed in dependencies but does not exist.")
            for dep in deps:
                if dep not in self.tasks:
                    raise ValueError(f"Missing dependency detected: Task '{task_name}' depends on '{dep}' which does not exist.")
                
    def getDependencies(self, task_name):
        # Retrieve the list of dependencies for a given task
        return self.precedence.get(task_name, [])
    
    def runSeq(self):
        # Run tasks sequentially
        executed = set()

        """
            Because we want to allow tasks to be in any order in the self.tasks list, I need 
            to visit all dependencies using a dfs before executing the task. This way, it 
            ensures that all dependencies are executed before the task itself.
        """

        # DFS function to visit all dependencies before executing the task
        def visit(task_name):
            if task_name in executed:
                return
            
            for dep in self.getDependencies(task_name):
                visit(dep)
            
            self.tasks[task_name].execute()
            executed.add(task_name)

        for task_name in self.tasks.keys():
            visit(task_name)

    def run(self):
        # Run tasks in parallel
        threads = []
        executed = set()
        events = {task_name: threading.Event() for task_name in self.tasks.keys()}
        ressource_locks = {ressource: threading.Lock() for task in self.tasks.values() for ressource in task.reads + task.writes}

        def runTask(task):
            for dep in self.getDependencies(task.name):
                # Wait for the dependency(ies) to finish
                events[dep].wait()  

            # Sort resources alphabetically to enforce a fixed lock order
            resources = sorted(set(task.reads + task.writes))

            # Acquire locks in the fixed order
            acquired = []
            try:
                for ressource in resources:
                    ressource_locks[ressource].acquire()
                    acquired.append(ressource)

                task.execute()

            finally:
                # Release locks in the same order
                for ressource in acquired:
                    ressource_locks[ressource].release()

            executed.add(task.name)
            events[task.name].set()

        # Start a thread for each task with the runTask function as target
        for task in self.tasks.values():
            thread = threading.Thread(target=runTask, args=(task,))
            threads.append(thread)
            thread.start()

        # Wait for all threads to finish
        for thread in threads:
            thread.join()

    def detTestRnd(self, nb_trials=100):
        system_deterministic = True

        for trial in range(nb_trials):
            # Random seed for each trial
            seed = random.randint(0, 10**6)
            results = []

            for _ in range(2):
                # Set the random seed for this run
                random.seed(seed)

                # Randomize the initial state of the tasks
                for task in self.tasks.values():
                    task.randomize_result()

                # Run the current task system
                self.run()

                # Collect the state of each task and store it
                state = {name: task.get_result() for name, task in self.tasks.items()}
                results.append(state)

            # Check if all results are the same
            if not all(result == results[0] for result in results):
                print(f"Non-deterministic behavior detected in trial {trial + 1}.")
                print(f"Results: {results}")
                system_deterministic = False

        if system_deterministic:
            print("System is deterministic.")

        return system_deterministic
        
    """
        After some (long) research for drawing graphs with levels, I found that Graphviz is 
        one of the most popular tools for this purpose. However, using Graphviz requires 
        the pygraphviz package, which is not readily available on Windows without 
        installing Graphviz separately. To avoid relying on external dependencies, I 
        decided to manually implement the level logic using the networkx and matplotlib libraries.
    """
    def draw(self):
        # Create directed graph
        G = nx.DiGraph()

        # Add nodes 
        for task_name in self.tasks.keys():
            G.add_node(task_name)

        # Add edges 
        for task_name, deps in self.precedence.items():
            for dep in deps:
                G.add_edge(dep, task_name)

        # Calculate task levels
        levels = {}
        for task_name in nx.topological_sort(G):
            level = max([levels.get(dep, 0) for dep in G.predecessors(task_name)], default=-1) + 1
            levels[task_name] = level

        # Group tasks by level
        level_dict = {}
        for task, level in levels.items():
            if level not in level_dict:
                level_dict[level] = []
            level_dict[level].append(task)

        # Calculate positions for each task
        pos = {}
        for level, tasks in level_dict.items():
            x_positions = np.linspace(-len(tasks) / 2, len(tasks) / 2, len(tasks))  # Spread evenly
            for i, task in enumerate(tasks):
                pos[task] = (x_positions[i], -level)  # Y is inverted for top-down layout

        # Calculate node sizes based on name length
        node_sizes = [2000 + 100 * len(task_name) for task_name in G.nodes()]

        # Draw the graph
        plt.figure(figsize=(8, 6))
        nx.draw(
            G, pos, with_labels=True, 
            node_color="skyblue", edgecolors="black",
            node_size=node_sizes, font_size=12, font_weight="bold",
            edge_color="gray", width=2, 
            arrows=True, arrowsize=20
        )

        plt.title("Task System Graph", fontsize=14, fontweight="bold")
        plt.show()
    
    def parCost(self, runs=5):
        seq_times = []
        par_times = []

        for _ in range(runs):
            # Sequential 
            start = time.time()
            self.runSeq()
            seq_times.append(time.time() - start)

            # Parallel
            start = time.time()
            self.run()
            par_times.append(time.time() - start)

        # Calculate average times
        avg_seq_time = sum(seq_times) / runs
        avg_par_time = sum(par_times) / runs

        print(f"Average Sequential Execution Time: {avg_seq_time:.5f} sec")
        print(f"Average Parallel Execution Time: {avg_par_time:.5f} sec")
        print(f"Speedup Factor: {avg_seq_time / avg_par_time:.2f}x")