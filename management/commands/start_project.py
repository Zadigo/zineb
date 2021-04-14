import os

from zineb.management.base import BaseCommand
from zineb.settings import settings as global_settings


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('-p', '--project', type=str, help='Project name')

    @staticmethod
    def _clean_file_name(name_or_path:str):
        if name_or_path.endswith('tpl'):
            name_or_path = name_or_path.removesuffix('_tpl')
        return f'{os.path.basename(name_or_path)}.py'

    def _create_new_file(self, source, destination, project_path=None):
        with open(source, mode='rb') as f:
            base_name = self._clean_file_name(source)
            file_to_create = os.path.join(destination, base_name)
            content = f.read().decode('utf-8')
            with open(file_to_create, mode='wb') as d:
                d.write(content.encode('utf-8'))
    
    def execute(self, namespace):
        project_name = namespace.project
        if project_name is None:
            raise ValueError('Project does not have a name')

        # Construct a full path the project's
        # root directory
        current_dir = os.path.abspath(os.curdir)
        full_project_path_dir = os.path.join(current_dir, project_name)

        zineb_templates_dir_path = os.path.join(global_settings.PROJECT_PATH, 'templates/project')
        zineb_template_items = list(os.walk(zineb_templates_dir_path))
        root_path, folders, root_files = zineb_template_items.pop(0)

        # Create the base folders:
        # media, middlewares, models
        for folder in folders:
            os.makedirs(os.path.join(full_project_path_dir, folder))

        for file in root_files:
            self._create_new_file(
                os.path.join(root_path, file),
                full_project_path_dir
            )

        # Now once the main root elements were
        # created, create the sub elements
        for items in zineb_template_items:
            full_path, folder, files = items
            for file in files:
                self._create_new_file(
                    os.path.join(full_path, file),
                    os.path.join(full_project_path_dir, os.path.basename(full_path)),
                    project_path=full_project_path_dir,
                )
