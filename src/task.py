import random

class Task:
    def __init__(self, name, reads=[], writes=[], run=None):
        self.name = name
        self.reads = reads
        self.writes = writes
        self.run = run
        self.output = None

    # Execute the test
    def execute(self):
        if self.run:
            self.output = self.run()
        else:
            # default behavior when run is not provided
            self.output = f"Running {self.name}"
            print(f"Running {self.name}")

    # Set random values for reads and writes
    def set_random_values(self):
        self.reads = random.randint(0, 100)
        self.writes = random.randint(0, 100)