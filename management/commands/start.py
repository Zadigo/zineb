import os
from collections import OrderedDict
from importlib import import_module

from zineb.app import Zineb
from zineb.management.base import BaseCommand
from zineb.checks.core import checks_registry
from zineb.models.datastructure import Model
from zineb.settings import settings


class Command(BaseCommand):
    def add_arguments(self, parser):
        pass

    def execute(self):
        new_settings = super()._load_project_settings()
        project_name = new_settings.get('project_name')

        # Now, load the spider and the models
        # that were registered for the project
        spiders_module = import_module(f'{project_name}.spiders')
        spiders_module_dict = spiders_module.__dict__

        spiders = new_settings.get('SPIDERS')
        for spider_name in spiders:
            spider_obj = spiders_module_dict.get(spider_name)
            new_settings['project_structure']['loaded_spiders'].append(spider_obj)

        # middlewares = new_settings.get('MIDDLEWARES')

        # Run checks on the new settings that were
        # provided/updated in order to keep things
        # tight and solid
        checks_registry._default_settings = new_settings
        checks_registry.run()

        # Send a signal when mostly everything is started
        # and that the spiders are ready to receive signals
        # or start processing urls

        # Finally execute each spider. Normally they don't
        # return an instance but it would be interesting to
        # actually register their state
        loaded_spiders = new_settings.get('project_structure')['loaded_spiders']
        for spider in loaded_spiders:
            _ = spider()    
