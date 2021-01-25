import os
from collections import OrderedDict
from functools import lru_cache
from importlib import import_module
from os.path import basename

from zineb.settings import settings


def collect_commands():
    commands_path = list(os.walk(os.path.join(settings.PROJECT_PATH, 'management', 'commands')))
    files = commands_path[0][-1]
    complete_paths = map(lambda filename: os.path.join(commands_path[0][0], filename), files)
    return complete_paths


def load_command_class(name):
    modules = collect_commands()
    for module in modules:
        module_name = basename(module)
        name, _ = module_name.split('.')
        module = import_module(f'zineb.management.commands.{name}')
        return module.Command()


@lru_cache(maxsize=1)
def available_commands():
    pass


class Utility:
    commands_registry = OrderedDict()

    def __init__(self):
        modules = collect_commands()

        for module in modules:
            module_name = basename(module)
            true_name, ext = module_name.split('.')
            module_obj = import_module(f'zineb.management.commands.{true_name}')
            self.commands_registry[true_name] = module_obj.Command()

    def call_command(self, name):
        # Once all the commands were collected,
        # look for the actual command
        command_instance = self.commands_registry.get(name, None)
        if command_instance is None:
            raise Exception('Command does not exist')

        # command_instance = command_instance.Command()
        parser = command_instance.create_parser()
        namespace = parser.parse_args()
        # print(defaults)
        command_called = namespace.command
        if command_called == 'startproject':
            pass
        elif command_called == 'start':
            pass
        command_instance.execute()
        return command_instance


def execute_command_inline():
    utility = Utility()
