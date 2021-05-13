from zineb.management.base import BaseCommand
from zineb.checks.base import checks_registry

class Command(BaseCommand):
    def execute(self, namespace):
        self.preconfigure_project()
        checks_registry.run()
