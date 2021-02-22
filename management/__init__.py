import os
from collections import OrderedDict
from functools import lru_cache
from importlib import import_module
from os.path import basename

from zineb.settings import settings


def collect_commands():
    """
    This collects all the commands in the management/commands
    directory  without loading any of them

    Returns
    -------

        [Iterator]: the paths of each commands in the directory
    """
    commands_path = list(os.walk(os.path.join(settings.PROJECT_PATH, 'management', 'commands')))
    files = commands_path[0][-1]
    complete_paths = map(lambda filename: os.path.join(commands_path[0][0], filename), files)
    return complete_paths


def load_command_class(name):
    """
    Loads each commands in the management/commands directory
    and then returns the Command class instance of a specific
    command

    Parameters
    ----------

        name (str): the command's name

    Returns
    -------

        obj: the Command instance
    """
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
    """
    This is the main class that encapsulates the logic
    for creating and using the command parser

    Raises
    ------

        Exception: [description]

    Returns
    -------

        [type]: [description]
    """
    commands_registry = OrderedDict()

    def __init__(self):
        modules = collect_commands()

        for module in modules:
            module_name = basename(module)
            true_name, ext = module_name.split('.')
            module_obj = import_module(f'zineb.management.commands.{true_name}')
            self.commands_registry[true_name] = module_obj.Command()

    def call_command(self, name):
        """
        Call a specific command from the registry

        Args:
            name (str): command's name

        Raises:
            Exception: [description]

        Returns:
            obj: Command instance
        """
        # ['manage.py', 'commmand=start']
        _, items = name
        _, cmd_value = items.split('=')
        # Once all the commands were collected,
        # look for the actual command
        command_instance = self.commands_registry.get(cmd_value, None)
        if command_instance is None:
            raise Exception('Command does not exist')

        # command_instance = command_instance.Command()
        parser = command_instance.create_parser()
        namespace = parser.parse_args()

        command_called = namespace.command
        _, command_value = command_called.split('=')
        if command_value == 'shell':
            command_instance.execute(url=namespace.url)
        else:
            command_instance.execute()

        # if command_called == 'startproject':
        #     pass
        # elif command_called == 'start':
        #     pass

        return command_instance


def execute_command_inline(arg):
    """
    Execute a command using `python manage.py`

    Parameters
    ----------

        arg (list): a list where [command name, value]
    """
    utility = Utility()
    utility.call_command(arg)
