import os
import subprocess

import zineb
from zineb.management.base import ProjectCommand
from zineb.settings import settings


class Command(ProjectCommand):
    def execute(self, namespace):
        zineb.setup()
        path_to_server = os.path.join(settings.GLOBAL_ZINEB_PATH, 'server', 'app.py')
        
        command = ['python', path_to_server]
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        print(result)
