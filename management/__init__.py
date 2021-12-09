import os
from collections import OrderedDict
from importlib import import_module
from os.path import basename
from typing import Callable

# NOTE: In order for certain commands to work when
# testing ex. startproject myproject, in order for
# the second command to work correctly, its better
# to call a file with the vscode debugger and the
# arguments that we want. Otherwise, for whatever
# reason there is an error on the second command.

def collect_commands():
    """
    This collects all the paths to the commands
    located in the `management/commands` directory
    without loading any of them

    Returns
    -------

        Iterator [Iterator]: the paths of each commands in the directory
    """
    from zineb.settings import settings as global_settings
    commands_path = list(os.walk(os.path.join(global_settings.GLOBAL_ZINEB_PATH, 'management', 'commands')))
    files = commands_path[0][-1]
    complete_paths = map(lambda filename: os.path.join(commands_path[0][0], filename), files)
    return complete_paths


def load_command_class(name: str) -> Callable:
    """
    Loads each commands in the `management/commands` directory
    and then returns the Command class instance of a specific
    command specified the name in the parameter

    Parameters
    ----------

        name (str): the command's name

    Returns
    -------

        Command (type): the Command instance
    """
    paths = collect_commands()
    for path in   paths:
        module_name = basename(path)
        name, _ = module_name.split('.')
        try:
            module = import_module(f'zineb.management.commands.{name}')
        except:
            raise ImportError(f"Could not import module at {path} from the Zineb commands directory.")
        return module.Command()


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
        modules_paths = collect_commands()

        for path in modules_paths:
            module_name = basename(path)
            true_name, _ = module_name.split('.')
            try:
                module_obj = import_module(f'zineb.management.commands.{true_name}')
            except Exception as e:
                raise ImportError((f"Could not import module: {path}"))
            self.commands_registry[true_name] = module_obj.Command()

    def _parse_incoming_commands(self, args: list):
        if len(args) <= 1:
            raise ValueError(('You called manage.py or python -m zineb '
            'without specifying any commands to run.'))
        name = args[0]
        remaining_tokens = args[1:]
        return name, remaining_tokens

    def call_command(self, name: list):
        """
        Call a specific command from the registry

        Parameters
        ----------

            name (Union[list, str]): command name

        Returns
        -------

            Type[BaseCommand]: the command instance to use
        """
        module_or_file, tokens = self._parse_incoming_commands(name)
        command_name = tokens.pop(0)
        command_instance = self.commands_registry.get(command_name, None)
        if command_instance is None:
            raise ValueError(f'Command {command_name} does not exist.')

        parser = command_instance.create_parser()
        namespace = parser.parse_args()
        command_instance.execute(namespace)
        return command_instance


def execute_command_inline(argv):
    """
    Execute a command using `python manage.py`

    Parameters
    ----------

        argv (list): [file, command, ...]
    """
    utility = Utility()
    utility.call_command(argv)
