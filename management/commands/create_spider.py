from zineb.management.base import BaseCommand
from zineb.settings import settings as global_settings


class Command(BaseCommand):
    def create_parser(self, parser):
        parser.add_argument('name', type='str', required=True)
        parser.add_argument('--type', '-t', type='str', default='spider')

    def execute(self, namespace):
        project_path = global_settings.PROJECT_PATH
        with open(project_path, mode='wb', encoding='utf-8') as f:
            base = f"""
            \n
            \n
            class {namespace.name}(Zineb):
                start_urls = []

                def start(self, response, request, **kwargs):
                    pass
            """
            f.write(base)
