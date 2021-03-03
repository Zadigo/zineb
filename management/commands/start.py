import os
from collections import OrderedDict
from importlib import import_module

from zineb.app import Zineb
from zineb.checks.core import checks_registry
from zineb.management.base import BaseCommand
from zineb.models.datastructure import Model
from zineb.settings import settings
from zineb.utils.general import create_logger

logger = create_logger('Start', to_file=False)


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--name', '-n', required=False, type=str)

    def execute(self, namespace=None):
        new_settings = super()._load_project_settings()
        project_name = new_settings.get('project_name')

        try:
            # Load the spiders module e.g. project.spiders
            spiders_module = import_module(f'{project_name}.spiders')
        except:
            raise ImportError((f"The command was executed outside "
            f"of a project and thus cannot load the 'spiders' module. "
            f"Got {project_name}."))
        else:
            spiders_module_dict = spiders_module.__dict__

        missing_spiders = []

        spiders = new_settings.get('SPIDERS')
        for spider_name in spiders:
            spider_obj = spiders_module_dict.get(spider_name)

            if spider_obj is not None:
                new_settings['project_structure']['loaded_spiders'].append((spider_name, spider_obj))                    
            else:
                missing_spiders.extend([spider_name])            

        # middlewares = new_settings.get('MIDDLEWARES')

        # Run checks on the new settings that were
        # provided/updated in order to keep things
        # tight and solid
        checks_registry._default_settings = new_settings
        checks_registry.run()

        if missing_spiders:
            for missing_spider in missing_spiders:
                logger.info(f"'{missing_spider}' spider was not found in project")

        # Send a signal when mostly everything is started
        # and that the spiders are ready to receive signals
        # or start processing urls

        loaded_spiders = new_settings.get('project_structure')['loaded_spiders']
        if namespace.name is not None:
            spider = list(filter(lambda x: namespace.name in x, loaded_spiders))
            if not loaded_spiders:
                logger.info(f"'{namespace.name}' spider was not found in project")
            else:
                _ = spider[0][-1]()
        else:
            # Finally execute each spider. Normally they don't
            # return an instance but it would be interesting to
            # actually register their state
            for spider in loaded_spiders:
                _ = spider[1]()    
