import zineb
from zineb.checks.core import checks_registry
from zineb.exceptions import ImproperlyConfiguredError
from zineb.management.base import ProjectCommand
from zineb.registry import registry


class Command(ProjectCommand):
    def add_arguments(self, parser):
        parser.add_argument('--name', help='A name of a specific spider to start', type=str)
        parser.add_argument('--settings', help='A settings module to use e.g. myproject.settings', action='store_true')

    def execute(self, namespace):        
        zineb.setup()
        
        # TODO: Move the checks registry to the
        # setup where we an run all the checks
        # for the given project ?
        checks_registry.run()
        
        if not registry.spiders_ready:
            raise ImproperlyConfiguredError('The spiders for the current project were not properly configured')
        
        if namespace.name is not None:
            config = registry.get_spider(namespace.name)
            config.run()
        else:
            registry.run_all_spiders()
