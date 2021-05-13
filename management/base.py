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

    def preconfigure_project(self, **extra_settings):
        """
        A method to use in order to configure the settings
        files and other main variables in the settings
        files when a command is called.
        """
        project = os.environ.get('ZINEB_SPIDER_PROJECT')
        project_name, _ = project.rsplit('.', maxsplit=1)
        # Rettriger the settings files in order to counteract
        # the first initial __init__ of the class with sets
        # values such as PROJECT_PATH to None because the
        # environ ZINEB_PROJECT_SPIDER is not set (for
        # whatever reasons)
        # HACK: In order to load the correct settings
        # as per what the user has entered, we
        # have to reinstantiate the class which
        # will force an update --; the problem is
        # the settings file is loaded before the command
        # (since it is placed in the __init__) and in that
        # situation, only the global settings are loaded.
        # By forcing and reinstantiation, the command has
        # the time to place the project's settings in the
        # Windows environment and therefore load the settings
        # file of the project
        from zineb.settings import settings
        attrs = {
            'project_name': project_name, 
            'python_path': project,
            'spiders_path': f'{project_name}.spiders'
        }
        settings(_project_meta=attrs, **extra_settings)

        # Update the settings with a REGISTRY
        # that will contain the fully loaded 
        # spiders which is the Registry class 
        # itself
        setattr(settings, 'REGISTRY', None)

        # If the user did not explicitly set the path
        # to a MEDIA_FOLDER, we will be doing it
        # autmatically here
        media_folder = getattr(settings, 'MEDIA_FOLDER')
        if media_folder is None:
            project_path = os.path.join(getattr(settings, 'PROJECT_PATH'))
            setattr(settings, 'MEDIA_FOLDER', os.path.join(project_path, 'media'))
        return project_name, settings

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
