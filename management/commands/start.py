from importlib import import_module

from zineb import global_logger
from zineb.checks.core import checks_registry
from zineb.management.base import ProjectCommand
from zineb.registry import registry


class Command(ProjectCommand):
    def add_arguments(self, parser):
        parser.add_argument('--name', help='A name of a specific spider to start', type=str)
        parser.add_argument('--settings', help='A settings module to use e.g. myproject.settings', action='store_true')

    def execute(self, namespace):
        project_name, settings = self.preconfigure_project()
        checks_registry.run()

        # The first call of the logger does not
        # use the user settings. To correct that
        # we need to re-instantiate it.
        global_logger(name='Zineb', to_file=True)

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
            raise ImportError(("The command was executed outside "
            "of a project and thus cannot load the 'spiders' module. "
            f"Got {project_name}."))
        else:
            registry.populate(spiders_module)

        if namespace.name is not None:
            spider_config = registry.get_spider(namespace.name)
            spider_config.run()
        else:
            registry.run_all_spiders()
