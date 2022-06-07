import zineb
from utils.reloader import run_with_reloader
from zineb.management.base import ProjectCommand
from zineb.utils.reloader import run_simple, run_with_reloader
from zineb.utils.servers import get_default_server


class Command(ProjectCommand):
    def add_arguments(self, parser):
        parser.add_argument('--reload', type=bool, default=False, help='Should the reloader detect file changes')
        
    def execute(self, namespace):
        zineb.setup()

        server = get_default_server()

        if namespace.reload:
            run_with_reloader(server.run, args=(), kwargs={})
        else:
            run_simple(server.run, args=(), kwargs={})
