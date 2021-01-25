from argparse import ArgumentParser
from collections import OrderedDict


class BaseCommand:
    help = ''
    command_registry = OrderedDict()

    def create_parser(self, **kwargs):
        parser = ArgumentParser(
            description=self.help,
            **kwargs
        )
        parser.add_argument('command', help='Command name to use', type=str)
        self.add_arguments(parser)
        return parser

    def add_arguments(self, parser):
        pass

    def execute(self):
        pass
