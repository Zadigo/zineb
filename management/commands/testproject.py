import zineb
from zineb.checks.core import checks_registry
from zineb.management.base import BaseCommand


class Command(BaseCommand):
    def execute(self, namespace):
        zineb.setup()
        checks_registry.check_settings_base_integrity()
