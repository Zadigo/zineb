import platform
import subprocess

from zineb.logger import logger
from zineb.management.base import BaseCommand


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('host', type=str)

    def execute(self, namespace):
        param = '-n' if platform.system().lower() == 'windows' else '-c'
        command = ['ping', param, '1', namespace.host]
        if subprocess.call(command) == 0:
            logger.instance.info('Ping was successful.')
        else:
            logger.instance.error('Url is not valid.')
