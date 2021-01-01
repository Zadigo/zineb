from argparse import ArgumentParser

class BaseCommand:
    help = ''

    def create_parser(self, **kwargs):
        parser = ArgumentParser(
            description=self.help,
            **kwargs
        )
        parser.add_argument(
            '-u', '--url', type=str, required=True
        )
        return parser

    def execute(self, *args, **kwargs):
        pass
