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
            # default behavior when run is not provided
            print(f"Running {self.name}")
