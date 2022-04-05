from calendar import c
import os
import subprocess

from zineb.management.base import ProjectCommand
from zineb.registry import registry
from importlib import import_module
from zineb.logger import logger

class Command(ProjectCommand):
    def execute(self, namespace):
        project_name, settings = self.preconfigure_project()
        path_to_server = os.path.join(settings.GLOBAL_ZINEB_PATH, 'server', 'app.py')
        
        try:
            # Load the spiders module
            # e.g. project.spiders
            spiders_module = import_module(
                settings._project_meta['spiders_path']
            )
        except Exception as e:
            logger.instance.error(e.args, stack_info=True)
            raise
        except:
            raise ImportError(("The command was executed outside "
            "of a project and thus cannot load the 'spiders' module. "
            f"Got {project_name}."))
        else:
            registry.populate(spiders_module)
            # Update the settings with a REGISTRY
            # that will contain the fully loaded
            # spiders which is the Registry class
            # itself for apps that need to access it
            setattr(settings, 'REGISTRY', registry)
        
        command = ['python', path_to_server]
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        print(result.stdout)
