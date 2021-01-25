#!/usr/bin/env python

import os
import stat
import shutil

from zineb.management.base import BaseCommand
from zineb.settings import settings


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('-p', '--project', type=str, help='Project name')
    
    def execute(self):
        project_name = 'my_project'

        # current_dir = os.path.abspath(os.curdir)
        # new_project_path = os.path.join(current_dir, project_name)
        # if os.path.exists(new_project_path):
        #     raise IOError('The project exists already')

        # os.mkdir(new_project_path)
        # os.chmod(new_project_path, stat.S_IRWXU)

        # os.chdir(new_project_path)
        # os.mkdir('settings')
        # open('__init__.py', 'w').close()

        # shutil.copy(new_project_path, os.path.join(new_project_path, 'settings/zineb.conf'))        
        # shutil.copy(settings.SETTINGS_FILE, os.path.join(new_project_path, 'settings/settings.py'))


        # with open('app.py', mode='w') as f:
        #     elements_to_write = f"""
        #     from zineb.app import Zineb

        #     from {project_name}.models import MyModel

        #     class {project_name.title()}(Zineb):
        #         start_urls = []
        #     """
        #     f.write(elements_to_write)

        # with open('models.py', mode='w') as f:
        #     elements_to_write = f"""
        #     from zineb.models import fields
        #     from zineb.models.datastructure import Model

        #     class MyModel(Model):
        #         pass
        #     """
        #     f.write(elements_to_write)
