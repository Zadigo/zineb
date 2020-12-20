import argparse
import os
import shutil

from zineb.settings import Settings

settings = Settings()

class Manager:
    def __init__(self, project_name):
        current_dir = os.path.abspath(os.curdir)
        new_project_path = os.path.join(current_dir, project_name)
        if os.path.exists(new_project_path):
            raise FileExistsError('The project is already there')
        os.mkdir(new_project_path)
        os.chdir(new_project_path)
        os.mkdir('settings')
        open('__init__.py', 'w').close()

        settings_file = settings.get('SETTINGS_FILE')
        shutil.copy2(settings_file, os.path.join(new_project_path, 'settings'))

        with open('app.py', mode='w') as f:
            elements_to_write = f"""
            from zineb.app import Zineb

            from {project_name}.models import MyModel

            class {project_name.title()}(Zineb):
                start_urls = []
            """
            f.write(elements_to_write)

        with open('models.py', mode='w') as f:
            elements_to_write = f"""
            from zineb.models import fields
            from zineb.models.datastructure import Model
            
            class MyModel(Model):
                pass
            """
            f.write(elements_to_write)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Web spider')
    parser.add_argument('-p', '--project-name', type=str, help='Project name', required=True)
    parsed_args = parser.parse_args()

    manager = Manager(parsed_args.project_name)
