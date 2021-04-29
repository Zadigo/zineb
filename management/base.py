import os
from argparse import ArgumentParser, Namespace
from collections import OrderedDict
from typing import Any



class BaseCommand:
    """
    Represents a base Zineb command. Each command
    class to subclass this in order to be registered
    """

    help = ''
    command_registry = OrderedDict()

    def create_parser(self, **kwargs):
        parser = ArgumentParser(
            description=self.help,
            **kwargs
        )
        # These are the base arguments that are implemented
        # to the base parser and then passed in the add_arguments
        # of the subclasses for additional arguments to be added
        parser.add_argument('command', help='Command name to use', type=str)

        # Add other optional arguments are specified in the
        # add_arguments definition of the Command class
        self.add_arguments(parser)
        return parser

    def add_arguments(self, parser: ArgumentParser):
        """
        This adds additional arguments in addition with
        the ones that were already implemented above. Each
        subclass can implement additional arguments

        Args:
            parser (ArgumentParser): the ArgumentParser instance
        """
        pass

    def execute(self, namespace: Namespace=None) -> Any:
        """
        Represents the main logic behind an argument passed
        using the command line. Each Command should override
        this definition to implement their custom logic so that
        when this is called, the logic is run
        """
        pass
