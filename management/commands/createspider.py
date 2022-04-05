import os

from zineb import initialize
from zineb.exceptions import RequiresProjectError
from zineb.logger import logger
from zineb.management.base import BaseCommand


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('name', type=str, help='Name of your spider')
        parser.add_argument('--type', type=str, help='The type of spider to create', default='http', choices=['http', 'file'])

    def execute(self, namespace):
        _, settings = self.preconfigure_project()
        project_path = settings.PROJECT_PATH
        
        if project_path is None:
            raise RequiresProjectError()

        spider_type = 'Zineb'
        if namespace.type == 'file':
            spider_type = 'FileCrawler'

        path = os.path.join(project_path, 'spiders.py')
        with open(path, mode='rb+') as f:
            content = f.read()
            base = f"""\n
            \n
            class {namespace.name}({spider_type}):
                start_urls = []

                def start(self, response, request, **kwargs):
                    pass
            """
            f.write(bytes(base.encode('utf-8')))
            logger.instance.info((f"{namespace.name} was succesfully created. "
            "Do not forget to register the spider in order to run it."))
