import threading

class TaskSystem:
    def __init__(self, tasks, precedence):
        # Use task name as key for easy access
        self.tasks = {task.name: task for task in tasks}
        # Dictionary of task dependencies
        self.precedence = precedence

    def getDependencies(self, task_name):
        # Retrieve the list of dependencies for a given task
        return self.precedence.get(task_name, [])
    
    def runSeq(self):
        executed = set()

        # We need to sort the tasks by the number of dependencies to ensure that all tasks are executed after their dependencies
        # Does not handle circular dependencies case
        for task_name in sorted(self.precedence, key=lambda t: len(self.getDependencies(t))):
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