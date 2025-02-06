class Task:
    def __init__(self, name, reads=None, writes=None, run=None):
        self.name = name
        self.reads = reads
        self.writes = writes
        self.run = run

    # Execute the test
    def execute(self):
        if self.run:
            self.run()
        else:
            # default behavior when run is not provided
            print(f"Running {self.name}")
