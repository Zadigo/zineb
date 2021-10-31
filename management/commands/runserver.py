from utils.reloader import run_simple, run_with_reloader
from zineb.management.base import ProjectCommand
from zineb.utils.reloader import Server

class Command(ProjectCommand):
    def add_arguments(self, parser):
        parser.add_argument('--reload', type=bool, default=False)

    def execute(self, namespace):
        server = Server()
        if namespace.reload:
            run_with_reloader(server.run, args=(), kwargs={})
        else:
            run_simple(server.run, args=(), kwargs={})
