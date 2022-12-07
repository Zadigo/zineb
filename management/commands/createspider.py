import os

import zineb
from zineb.exceptions import RequiresProjectError
from zineb.logger import logger
from zineb.management.base import BaseCommand
from zineb.settings import settings


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('name', type=str, help='Name of your spider')
        parser.add_argument('--type', type=str, help='The type of spider to create', default='http', choices=['http', 'file'])

    def execute(self, namespace):
        zineb.setup()
        spider_type = 'Zineb'
        if namespace.type == 'file':
            spider_type = 'FileCrawler'

        path = os.path.join(settings.PROJECT_PATH, 'spiders.py')
        # TODO: Test file creation especially
        # the indentation which is not good
        with open(path, mode='rb+') as f:
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
