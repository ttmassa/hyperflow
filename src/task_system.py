import threading
import time
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
from src.task import Task

class TaskSystem:
    def __init__(self, tasks: list[Task], precedence: dict[str, list[str]] = {}):
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

        # Check if the task system is deterministic using the Bernstein condition
        self.checkDetBernstein()

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

    """
        The Bernstein condition states that a task system is deterministic if and only if
        every pair of tasks is non-conflicting. Two tasks are non-conflicting if they meet
        one of the following conditions:
        - T1 -> T2 or T2 -> T1 
        - T1.reads ∩ T2.writes = ∅ and T1.writes ∩ T2.reads = ∅ and T1.writes ∩ T2.writes = ∅
    """
    def checkDetBernstein(self):
        # Check if the task system is deterministic using the Bernstein condition
        for task1 in self.tasks.values():
            for task2 in self.tasks.values():
                if task1 == task2:
                    continue

                # Check for conflicts
                if self.areTasksConflicting(task1, task2):
                    raise Exception("Non-deterministic behavior detected: Tasks '{0}' and '{1}' are conflicting.".format(task1.name, task2.name))
                
    def createTransitiveClosureMatrix(self):
        task_names = list(self.tasks.keys())
        n = len(task_names)

        # Initialize the transitive closure matrix
        transitive_closure = np.zeros((n, n), dtype=int)
        for i, task_name in enumerate(task_names):
            for dep in self.getDependencies(task_name):
                j = task_names.index(dep)
                transitive_closure[j, i] = 1

        # Compute the transitive closure using the Floyd-Warshall algorithm
        for k in range(n):
            for i in range(n):
                for j in range(n):
                    transitive_closure[i, j] = transitive_closure[i, j] or (transitive_closure[i, k] and transitive_closure[k, j])

        return transitive_closure
                
    def createMatrix(self):
        # Create max parallelism matrix
        task_names = list(self.tasks.keys())
        n = len(task_names)
        transitive_closure = self.createTransitiveClosureMatrix()

        # Create the max parallelism matrix by removing useless edges 
        max_parallelism_matrix = transitive_closure.copy()
        for i in range(n):
            for j in range(n):
                if i == j or transitive_closure[i, j] == 0:
                    continue

                task1 = self.tasks[task_names[i]]
                task2 = self.tasks[task_names[j]]
                # If two tasks are non-conflicting, they can run in parallel
                if set(task1.reads).intersection(task2.writes) or set(task1.writes).intersection(task2.reads) or set(task1.writes).intersection(task2.writes):
                    max_parallelism_matrix[i, j] = 1
                else:
                    max_parallelism_matrix[i, j] = 0

        return max_parallelism_matrix
    
    def areTasksConflicting(self, task1, task2):
        task_names = list(self.tasks.keys())
        transitive_closure = self.createTransitiveClosureMatrix()

        # Check if there's a path between the two tasks
        if transitive_closure[task_names.index(task1.name), task_names.index(task2.name)] == 1 or transitive_closure[task_names.index(task2.name), task_names.index(task1.name)] == 1:
            return False
            
        # Bernstein condition
        if set(task1.reads).intersection(task2.writes) or set(task1.writes).intersection(task2.reads) or set(task1.writes).intersection(task2.writes):
            return True
        
        return False
    
    def getDependencies(self, task_name):
        # Retrieve the list of dependencies for a given task
        return self.precedence.get(task_name, [])
    
    def runSeq(self):
        # Run tasks sequentially
        start_time = time.time()
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

        elapsed_time = time.time() - start_time
        return executed, elapsed_time

    def run(self):
        # Run tasks with maximum parallelism using the matrix
        start_time = time.time()
        task_names = list(self.tasks.keys())
        n = len(task_names)
        matrix = self.createMatrix()

        events = {task_name: threading.Event() for task_name in task_names}
        resource_locks = {resource: threading.Lock() for task in self.tasks.values() for resource in task.reads + task.writes}

        def runTask(task):
            for dep in self.getDependencies(task.name):
                events[dep].wait()  # Wait for dependencies to complete

            resources = sorted(set(task.reads + task.writes))
            acquired = []
            try:
                for resource in resources:
                    resource_locks[resource].acquire()
                    acquired.append(resource)

                task.execute()
            finally:
                for resource in acquired:
                    resource_locks[resource].release()

            events[task.name].set()

        # Determine task execution order based on max parallelism matrix
        executed = set()
        while len(executed) < n:
            # Find tasks with no dependencies remaining
            runnable_tasks = []
            for i in range(n):
                task_name = task_names[i]
                if task_name in executed:
                    continue
                if all(matrix[j, i] == 0 or task_names[j] in executed for j in range(n)):
                    runnable_tasks.append(self.tasks[task_name])

            # Execute all runnable tasks in parallel
            threads = []
            for task in runnable_tasks:
                t = threading.Thread(target=runTask, args=(task,))
                t.start()
                threads.append(t)
                executed.add(task.name)

            for t in threads:
                t.join()
        
        elapsed_time = time.time() - start_time
        return elapsed_time
    
    def detTestRnd(self, nb_trials=5, global_vars=None):
        is_deterministic = True
        start_time = time.time()

        if global_vars is None:
            global_vars = globals()

        # Get all the variables used by the system
        shared_variables = {var for task in self.tasks.values() for var in task.reads + task.writes}

        for _ in range(nb_trials):
            results = []

            # Randomize the variables
            for task in self.tasks.values():
                for var in task.reads + task.writes:
                    global_vars[var] = np.random.randint(0, 100)

            # Store the values of the variables before the execution
            initial_values = {var: global_vars[var] for var in shared_variables}

            for i in range(2):
                self.run()
                
                # Store the values of the variables after the execution
                result = {var: global_vars[var] for var in shared_variables}
                results.append(result)
                
                # Reset the variables to their random values given at the beggining of this trial
                for var, value in initial_values.items():
                    global_vars[var] = value

            if results[0] != results[1]:
                is_deterministic = False
                print("Task system is not deterministic: ", results[0], results[1])
                break
        
        if is_deterministic:
            print("Task system is deterministic!")

        elapsed_time = time.time() - start_time
        return is_deterministic, elapsed_time

        
    """
        After some (long) research for drawing graphs with levels, I found that Graphviz is 
        one of the most popular tools for this purpose. However, using Graphviz requires 
        the pygraphviz package, which is not readily available on Windows without 
        installing Graphviz separately. To avoid relying on external dependencies, I 
        decided to manually implement the level logic using the networkx and matplotlib libraries.
    """
    def draw(self):
        # Get max parallelism matrix
        matrix = self.createMatrix()
        task_names = list(self.tasks.keys())
        n = len(task_names)

        # Create directed graph
        G = nx.DiGraph()

        # Add nodes
        for task_name in task_names:
            G.add_node(task_name)

        # Add edges based on max parallelism matrix
        for i in range(n):
            for j in range(n):
                if matrix[i, j] == 1:  
                    G.add_edge(task_names[i], task_names[j])

        # Remove useless edges
        G = nx.transitive_reduction(G)

        # Compute task levels for visualization
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

        plt.title("Max Parallelism Graph", fontsize=14, fontweight="bold")
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