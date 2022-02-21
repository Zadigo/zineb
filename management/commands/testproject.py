from zineb.checks.core import checks_registry
from zineb.management.base import BaseCommand


class Command(BaseCommand):
    def execute(self, namespace):
        # Check that the user's project
        # is correctly set
        self.preconfigure_project()
        checks_registry.run()
