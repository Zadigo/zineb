import os
from argparse import ArgumentParser
from collections import OrderedDict
from importlib import import_module

from zineb.settings import settings


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
        # project_structure = dict(loaded_spiders=[], middlewares=[])
        project = os.environ.get('ZINEB_SPIDER_PROJECT')
        project_name, _ = project.split('.', maxsplit=1)
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

    def add_arguments(self):
        """
        This adds additional arguments in addition with
        the ones that were already implemented above. Each
        subclass can implement additional arguments

        Parameters
        ----------

            parser ([type]): [description]
        """
        pass

    def execute(self):
        """
        Represents the main logic behind an argument passed
        using the command line. Each Command should override
        this definition to implement their custom logic so that
        when this is called, the logic is run
        """
        pass
