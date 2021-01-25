from zineb.management.base import BaseCommand

class Command(BaseCommand):
    def add_arguments(self, parser):
        pass

    def execute(self):
        print('Doing start')
