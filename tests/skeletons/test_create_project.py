"""
Simple global skeleton used for testing that the creation process
when starting a new project is correctly done
"""

import os
import re

from zineb.settings import settings


def _clean_file_name(name_or_path: str):
    if name_or_path.endswith('tpl'):
        name_or_path = name_or_path.removesuffix('_tpl')
    return f'{os.path.basename(name_or_path)}.py'


def _create_new_file(source, destination, **kwargs):
    # with open(source, mode='rb') as f:
    #     base_name = _clean_file_name(source)
    #     file_to_create = os.path.join(destination, base_name)
    #     content = f.read().decode('utf-8')
    #     if base_name == 'manage.py':
    #         project_name = kwargs.get('project_name', None)
    #         content = re.sub(r'(project)', project_name, content)

    #     with open(file_to_create, mode='wb') as d:
    #         d.write(content.encode('utf-8'))
    print('File created', source, destination)

def execute():
    project_name = 'test_project'
    if project_name is None:
        raise ValueError('Project does not have a name.')

    # Construct a full path the project's
    # root directory
    current_dir = os.path.abspath(os.curdir)
    full_project_path_dir = os.path.join(current_dir, project_name)

    zineb_templates_dir_path = os.path.join(settings.GLOBAL_ZINEB_PATH, 'templates/project')
    zineb_template_items = list(os.walk(zineb_templates_dir_path))
    root_path, folders, root_files = zineb_template_items.pop(0)

    for folder in folders:
        # Create the base folders:
        # media, middlewares
        # os.makedirs(os.path.join(full_project_path_dir, folder))
        pass

    for file in root_files:
        _create_new_file(os.path.join(root_path, file), full_project_path_dir, project_name=project_name)

    # Now once the main root elements were
    # created, create the sub elements
    for items in zineb_template_items:
        full_path, folder, files = items
        for file in files:
            _create_new_file(
                os.path.join(full_path, file),
                os.path.join(full_project_path_dir, os.path.basename(full_path)),
                project_path=full_project_path_dir,
            )

if __name__ == '__main__':
    execute()
