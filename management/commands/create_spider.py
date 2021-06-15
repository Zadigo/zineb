import os

from zineb import global_logger
from zineb.exceptions import CommandRequiresProjectError
from zineb.management.base import BaseCommand
from zineb.settings import settings as global_settings


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('name', type=str)
        parser.add_argument('--type', '-t', type=str, default='MySpider')

    def execute(self, namespace):
        # project_path = global_settings.PROJECT_PATH
        _, configured_settings = self.preconfigure_project()
        project_path = configured_settings.PROJECT_PATH
        if project_path is None:
            raise CommandRequiresProjectError(namespace.command)

        path = os.path.join(project_path, namespace.name)
        with open(path, mode='wb+') as f:
            content = f.read()
            base = f"""
            \n
            \n
            class {namespace.name}(Zineb):
                start_urls = []

                def start(self, response, request, **kwargs):
                    pass
            """
            content = content + bytes(base.encode('utf-8'))
            f.write(content)
            global_logger.logger.info((f"{namespace.name} was succesfully created. "
            "Do not forget to register the spider in order to run it"))
