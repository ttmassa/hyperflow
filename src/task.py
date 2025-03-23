class Task:
    def __init__(self, name, reads=[], writes=[], run=None):
        self.name = name
        self.reads = reads
        self.writes = writes
        self.run = run
        self.variables = {}
        self.result = None

    # Execute the test
    def execute(self):
        if self.run:
            self.result = self.run()
        else:
            self.result = self.name

    def set_initial_values(self, variables):
        self.variables = {var: variables[var] for var in self.reads + self.writes if var in variables}

    def get_final_value(self, var):
        return self.variables.get(var, None)
    
    def get_result(self):
        return self.result