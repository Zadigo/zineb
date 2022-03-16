import os
from argparse import ArgumentParser, Namespace
from collections import OrderedDict
from typing import Any


class RequiresProjectError(Exception):
    def __init__(self):
        super().__init__('Project scope is required for this command.')


class BaseCommand:
    """
    Represents a base Zineb command. Each command
    class to subclass this in order to be registered
    """

    help = ''
    command_registry = OrderedDict()
    requires_system_checks = False

    def create_parser(self, **kwargs):
        parser = ArgumentParser(
            description=self.help or None,
            **kwargs
        )
        # These are the base arguments that are implemented
        # to the base parser and then passed in the add_arguments
        # of the subclasses for additional arguments to be added
        parser.add_argument('command', help='Command to use', type=str)

        # Adds other optional arguments to the parser
        # by the Command subclasses
        self.add_arguments(parser)
        return parser

    def preconfigure_project(self, **extra_settings):
        """
        A method to use in order to configure the settings
        files and other main variables when a project 
        command is called
        """
        project = os.environ.get('ZINEB_SPIDER_PROJECT')
        if project is None:
            raise RequiresProjectError()

        project_name, _ = project.rsplit('.', maxsplit=1)
        # In order to load the correct settings
        # as per what the user has entered, we
        # have to reinstantiate the class which
        # will force an update --; the problem is
        # the settings file is loaded before the command
        # (since it is placed in the __init__) and in that
        # situation, only the global settings are loaded.
        # By forcing a reinstantiation, the command has
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

        project_path = getattr(settings, 'PROJECT_PATH')
        zineb_path = getattr(settings, 'GLOBAL_ZINEB_PATH')

        setattr(
            settings, 'LOG_FILE', 
            os.path.join(project_path or zineb_path, 'zineb.log'),
        )

        # If the user did not explicitly set the path
        # to a MEDIA_FOLDER, we will be doing it
        # autmatically here
        media_folder = getattr(settings, 'MEDIA_FOLDER')
        if media_folder is None and project_path is not None:
            setattr(settings, 'MEDIA_FOLDER', os.path.join(project_path, 'media'))
        
        return project_name, settings

    def add_arguments(self, parser: ArgumentParser):
        """
        Adds additional arguments in addition with
        the ones that were already implemented above. Each
        subclass can implement additional arguments
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


class ProjectCommand(BaseCommand):
    requires_system_checks = True
