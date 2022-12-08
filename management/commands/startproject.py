import os
import re

from zineb.management.base import BaseCommand
from zineb.settings import settings


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('project', help='Name of the project', type=str)

    @staticmethod
    def _clean_file_name(name_or_path):
        if name_or_path.endswith('tpl'):
            name_or_path = name_or_path.removesuffix('_tpl')
        return f'{os.path.basename(name_or_path)}.py'

    def _create_new_file(self, source, destination, **kwargs):
        """Helper for creating a new file"""
        with open(source, mode='rb') as f:
            base_name = self._clean_file_name(source)
            
            file_to_create = os.path.join(destination, base_name)
            content = f.read().decode('utf-8')
            
            if base_name == 'manage.py':
                project_name = kwargs.get('project_name', None)
                content = re.sub(r'(project_name_placeholder)', project_name, content)

            with open(file_to_create, mode='wb') as d:
                d.write(content.encode('utf-8'))
    
    def execute(self, namespace):
        project_name = namespace.project
        if project_name is None:
            raise ValueError('Project does not have a name')

        # Construct a full path to the 
        # project's root directory
        current_dir = os.path.abspath(os.curdir)
        full_project_path_dir = os.path.join(current_dir, project_name)
        
        # FIXME: This blocks the creation of new project
        # directory. What's the necessity?
        # if not os.path.exists(full_project_path_dir):
        #     raise FileExistsError('Project directory does not exist')

        zineb_templates_dir_path = os.path.join(settings.GLOBAL_ZINEB_PATH, 'templates/project')
        zineb_template_items = list(os.walk(zineb_templates_dir_path))
        root_path, folders, root_files = zineb_template_items.pop(0)

        # Create the base folders:
        # media, middlewares, models
        for folder in folders:
            os.makedirs(os.path.join(full_project_path_dir, folder))

        for file in root_files:
            self._create_new_file(
                os.path.join(root_path, file),
                full_project_path_dir,
                project_name=project_name
            )

        # Now once the main root elements were
        # created, create the sub elements
        for items in zineb_template_items:
            full_path, folder, files = items
            for file in files:
                self._create_new_file(
                    os.path.join(full_path, file),
                    os.path.join(full_project_path_dir, os.path.basename(full_path))
                )
