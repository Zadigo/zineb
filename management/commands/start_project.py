import os
import stat
import shutil

from zineb.management.base import BaseCommand


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('-p', '--project', type=str, help='Project name')
    
    def execute(self, **kwargs):
        template_dir = ''
        project_name = kwargs.get('project')
        if project_name is None:
            raise ValueError('Project should be a valid name')
        current_dir = os.path.abspath(os.curdir)
        new_project_path = os.path.join(current_dir, project_name)
        if os.path.exists(new_project_path):
            raise OSError('The project exists already')

        os.mkdir(new_project_path)
        os.chmod(new_project_path, stat.S_IRWXU)

        os.chdir(new_project_path)
        os.mkdir('middlewares')
        os.mkdir('models')
        open('__init__.py', 'w').close()
        with open('D:/coding/personnal/zineb/templates/project/models/base_tpl', mode='r', encoding='utf-8') as f:
            with open(f"{new_project_path}/models/base.py", mode='w') as n:
                n.write(f.read())
        with open('D:/coding/personnal/zineb/templates/project/spider_tpl', mode='r', encoding='utf-8') as f:
            with open(f"{new_project_path}/spider.py", mode='w') as n:
                n.write(f.read())
        with open('D:/coding/personnal/zineb/templates/project/settings_tpl', mode='r', encoding='utf-8') as f:
            with open(f"{new_project_path}/settings.py", mode='w') as n:
                n.write(f.read())
        with open('D:/coding/personnal/zineb/templates/project/manage_tpl', mode='r', encoding='utf-8') as f:
            data = f.read()
            data = data.replace('project.settings', f'{project_name}.settings')
            with open(f"{new_project_path}/manage.py", mode='w') as n:
                n.write(data)
