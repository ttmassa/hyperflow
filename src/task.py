import random

class Task:
    def __init__(self, name, reads=[], writes=[], run=None):
        self.name = name
        self.reads = reads
        self.writes = writes
        self.run = run
        self.result = None

    # Execute the test
    def execute(self):
        if self.run:
            self.result = self.run()
        else:
            self.result = self.name

    def get_result(self):
        return self.result
    
    def randomize_result(self):
        self.result = random.randint(1, 100)