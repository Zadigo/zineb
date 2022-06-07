import zineb
from zineb.logger import logger
from zineb.checks.core import checks_registry
from zineb.management.base import BaseCommand


class Command(BaseCommand):
    def execute(self, namespace):
        zineb.setup()
        checks_registry.run()
        logger.instance.info('Test completed!')
