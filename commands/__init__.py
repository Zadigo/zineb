import sys


class Manager:
    def __init__(self, argv):
        self.argv = argv or sys.argv
        self.program = self.argv[0]

    def execute(self, *args, **kwargs):
        subcommand = sys.argv[1]
        print(subcommand)


def execute_command(argv=None):
    command_manager = Manager(argv)
    command_manager.execute()
