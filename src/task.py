import random

class Task:
    def __init__(self, name, reads=[], writes=[], run=None):
        self.name = name
        self.reads = reads
        self.writes = writes
        self.run = run

    # Execute the test
    def execute(self):
        if self.run:
            self.run()
        else:
            print(f"Running {self.name}")

    def get_result(self):
        return self.run()