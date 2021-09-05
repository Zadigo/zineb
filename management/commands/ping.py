import platform
import subprocess

from zineb import global_logger
from zineb.management.base import BaseCommand


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('host', type=str)

    def execute(self, namespace):
        param = '-n' if platform.system().lower() == 'windows' else '-c'
        command = ['ping', param, '1', namespace.host]
        if subprocess.call(command) == 0:
            global_logger.logger.info('Ping was successful.')
        else:
            global_logger.logger.error('Url is not valid.')
