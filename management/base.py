import os
from argparse import ArgumentParser, Namespace
from collections import OrderedDict
from importlib import import_module
from typing import Any

from zineb.logger import create_logger
from zineb.settings import settings

logger = create_logger('Command', to_file=True)

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

    def _load_project_settings(self):
        """
        Load the default project settings (Zineb) updating
        if needed some values with the settings of the
        user's project

        Returns
        -------

            OrderedDict: the base settings file updated with
            the user's settings and some additional annotations
        """
        project = os.environ.get('ZINEB_SPIDER_PROJECT')

        try:
            project_name, _ = project.split('.', maxsplit=1)
        except:
            logger.info(f"Command using global settings since user settings was not specified")
            # If we can't return a project setting,
            # just return the general settings
            return settings
        else:
            if project is None:
                return settings

            module = import_module(project)
            module_dict = module.__dict__
            # Update the initial settings with
            # the settings that the user has
            # implemented in his project
            user_settings = OrderedDict()
            for key, value in module_dict.items():
                if settings.has_setting(key):
                    user_settings.update({key: value})
            new_settings = settings(**user_settings)
            new_settings.update(
                {
                    'project_structure': dict(loaded_spiders=[], middlewares=[]),
                    'project_name': project_name
                }
            )
            return new_settings

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
