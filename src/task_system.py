import threading

class TaskSystem:
    def __init__(self, tasks, precedence):
        # Use task name as key for easy access
        self.tasks = {task.name: task for task in tasks}
        # Dictionary of task dependencies
        self.precedence = precedence

        # Check if all names are unique
        # Dictionary overwrites duplicates keys so we just need to compare its length with the number of tasks
        if len(self.tasks) != len(tasks):
            raise ValueError("Duplicate task names detected")
        
        # Check for circular dependencies
        self.checkCircularDependencies()

    def checkCircularDependencies(self):
        visited = set()
        rec_stack = set()

        # Depth-first search to detect circular dependencies
        def dfs(task_name):
            # Task is already in the current path being explored so circular dependency
            if task_name in rec_stack:
                raise Exception(f"Task {task_name} has a circular dependency")
            
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

    def getDependencies(self, task_name):
        # Retrieve the list of dependencies for a given task
        return self.precedence.get(task_name, [])
    
    def runSeq(self):
        # Run tasks sequentially
        # Does not handle circular dependencies cases yet
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