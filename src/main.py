import argparse
import sys
import os
import textwrap

# Add the parent directory to the path to be able to import the classes
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from examples.graph_example import generate_graph
from examples.premade_task_systems import simple_task_system, fibonacci_task_system, matrix_multiplication_task_system

class CustomArgumentParser(argparse.ArgumentParser):
    def print_welcome(self):
        welcome_message = textwrap.dedent("""
        Welcome to HyperFlow! 
        HyperFlow is a Python library created to help you manage, visualize and test your task systems. The goal is to maximise the parallelism of your tasks and improve the performance of your system.
        
        To get started, you can type 'main.py --test' to select a premade task system and test it.
    
        Type 'python main.py --help' to see the available options.
        For more information, visit the documentation at https://github.com/ttmassa/hyperflow
        """)
        print(welcome_message)

    def print_help(self):
        help_message = textwrap.dedent("""
        HyperFlow 1.0
        Usage:
            python main.py [options]

        Options:
            -v, --version    Display your current Hyperflow version
            --graph          Generate and display a graph example
            -t, --test       Test a premade task system
            -h, --help       Display this help message

        Example:
            main.py --v
            main.py --graph

        For more information, visit the documentation at https://github.com/ttmassa/hyperflow
        """)
        print(help_message)

    def test_message(self):
        test_message = textwrap.dedent("""
        To get started, you can select one of these premade task systems:
        1. Simple task system
        2. Fibonacci task system
        3. Matrix multiplication task system
        """)
        print(test_message)

        try: 
            choice = input("Select a task system: ")
            task_system = None
            if choice == '1':
                print("Simple task system selected")
                task_system = simple_task_system()
            elif choice == '2':
                print("Fibonacci task system selected")
                task_system = fibonacci_task_system()
            elif choice == '3':
                print("Matrix multiplication task system")
                task_system = matrix_multiplication_task_system()
            else:
                print("Invalid choice. Please select the number of the task system you want to test.")
        except KeyboardInterrupt:
            sys.exit()

        options_message = textwrap.dedent("""
        Here's the list of available options:
        1. Display the graph : 'graph'
        2. Test if the task system is deterministic : 'det'
        3. Compare sequential and parallel execution times : 'time'
        4. Create the matrix : 'matrix'
        5. Run the task system sequentially : 'seq'
        6. Run the task system in parallel : 'run'
        7. Test another premade task system : 'new'
                                          
        Type 'exit' to exit the program.
        """)
        print(options_message)

        try:
            while True:
                option = input("Select an option: ")
                if option == 'graph':
                    for task in task_system.tasks.values():
                        print(task.name, task.reads, task.writes)
                    print("Precedence: ", task_system.precedence)
                    print("Drawing dependency graph...")
                    task_system.draw()
                elif option == 'det':
                    task_system.detTestRnd()
                elif option == 'time':
                    print("Comparing execution times...")
                    task_system.parCost()
                elif option == 'matrix':
                    task_system.createMatrix()
                elif option == 'seq':
                    print("Running the task system sequentially...")
                    task_system.runSeq()
                elif option == 'run':
                    print("Running the task system...")
                    task_system.run()
                elif option == 'new':
                    self.test_message()
                elif option == 'exit':
                    break
                else:
                    print("Invalid option. Please select one of the available options.")
        except KeyboardInterrupt:
            sys.exit()

def main():
    parser = CustomArgumentParser(add_help=False)
    parser.add_argument('-v', '--version', action='version', version='Hyperflow 1.0')
    parser.add_argument('--graph', action='store_true', help='Generate and display a graph')
    parser.add_argument('-t', '--test', action='store_true', help='Test a premade task system')
    parser.add_argument('-h', '--help', action='store_true', help='Display this help message')

    args = parser.parse_args()

    if args.help:
        parser.print_help()
    elif args.graph:
        generate_graph()
    elif args.test:
        parser.test_message()
    else:
        parser.print_welcome()

if __name__ == '__main__':
    main()