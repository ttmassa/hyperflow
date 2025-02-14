import threading
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np

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

        # We need to sort the tasks by the number of dependencies to ensure that all tasks are executed after their dependencies
        # We also need to include the tasks that have no dependencies cause the sorting logic will not take them into account otherwise
        all_tasks = set(self.tasks.keys())
        sorted_tasks = sorted(all_tasks, key=lambda t: len(self.getDependencies(t)))

        for task_name in sorted_tasks:
            # Check if all dependencies of the current task have been executed
            for dep in self.getDependencies(task_name):
                if dep not in executed:
                    raise Exception(f"Task {task_name} depends on {dep} which is not executed yet")
            self.tasks[task_name].execute()
            executed.add(task_name)

    def run(self):
        # Run tasks in parallel
        threads = []
        executed = set()

        def runTask(task):
            for dep in self.getDependencies(task.name):
                if dep not in executed:
                    raise Exception(f"Task {task.name} depends on {dep} which is not executed yet")
                
            task.execute()
            executed.add(task.name)

        # Start a thread for each task with the runTask function as target
        for task in self.tasks.values():
            thread = threading.Thread(target=runTask, args=(task,))
            threads.append(thread)
            thread.start()

        # Wait for all threads to finish
        for thread in threads:
            thread.join()

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
        node_sizes = [3000 + 100 * len(task_name) for task_name in G.nodes()]

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