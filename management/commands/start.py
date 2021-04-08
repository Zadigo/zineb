import os
from importlib import import_module

from zineb.checks.core import checks_registry
from zineb.logger import create_logger
from zineb.management.base import BaseCommand
from zineb.registry import registry

logger = create_logger('Start', to_file=False)


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--name', '-n', required=False, type=str)

    def execute(self, namespace=None):
        checks_registry.run()
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
        # reloaded_settings = settings(LOADED_SPIDERS=[])
        project = os.environ.get('ZINEB_SPIDER_PROJECT')
        project_name, _ = project.split('.', maxsplit=1)
        
        try:
            # Load the spiders module e.g. project.spiders
            spiders_module = import_module(f'{project_name}.spiders')
        except Exception as e:
            logger.error(e.args, stack_info=True)
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
