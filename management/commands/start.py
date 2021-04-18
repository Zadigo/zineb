import os
from importlib import import_module

from zineb import global_logger
from zineb.checks.core import checks_registry
from zineb.management.base import BaseCommand
from zineb.registry import registry


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--name', '-n', required=False, type=str)

    def execute(self, namespace):
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
        settings(_project_meta=attrs)
        
        checks_registry.run()

        try:
            # Load the spiders module 
            # e.g. project.spiders
            spiders_module = import_module(
                settings._project_meta['spiders_path']
            )
        except Exception as e:
            global_logger.error(e.args, stack_info=True)
            raise
        except:
            raise ImportError((f"The command was executed outside "
            f"of a project and thus cannot load the 'spiders' module. "
            f"Got {project_name}."))
        else:
            registry.populate(spiders_module)

        if namespace.name is not None:
            spider_config = registry.get_spider(namespace.name)
            spider_config.run()
        else:
            registry.run_all_spiders()
