from zineb.commands.base import BaseCommand


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            '-f', '--file', type=str, required=False
        )

    def execute(self, *args, **kwargs):
        super().execute(*args, **kwargs)
