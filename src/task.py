class Task:
    def __init__(self, name: str, reads: list[str] = [], writes: list[str] = [], run: callable = None):
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