from zineb.management.base import BaseCommand
import code

from zineb.extractors import base, images, links
from zineb.http.request import HTTPRequest


def start_ipython_shell():
    try:
        from IPython.terminal import embed, ipapp
    except:
        return False
    else:
        configuration = ipapp.load_default_config()

        def shell_wrapper(namespace: dict = {}, banner=''):
            embed.InteractiveShellEmbed.clear_instance()
            shell = embed.InteractiveShellEmbed.instance(
                banner=banner, user_ns=namespace, config=configuration
            )
            shell()
        return shell_wrapper


def start_standard_console():
    def shell_wrapper(namespace: dict = {}, banner=''):
        code.interact(banner=banner, local=namespace)
    return shell_wrapper


SHELLS = [
    ('ipython', start_ipython_shell)
]


class Shell:
    def __init__(self) -> None:
        self.banner = ''
        self.namespace = {}
        self.shell_variables = {}

    def _start_consoles(self):
        for shell in SHELLS:
            _, func = shell
            try:
                if func:
                    # Starts each console passing the options
                    # and banner into the console
                    func()(namespace=self.shell_variables, banner=self.banner)
            except SystemError:
                pass

    def start(self, url):
        request = HTTPRequest(url)
        request._send()
        self.shell_variables.setdefault('request', request)
        self.shell_variables.setdefault('response', request.html_response)
        self.shell_variables.setdefault(
            'html_page', request.html_response.html_page)

        # Extractors
        self.shell_variables.setdefault('base', base)
        self.shell_variables.setdefault('images', images)
        self.shell_variables.setdefault('links', links)
        self._start_consoles()


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            '-f', '--file', type=str, required=False
        )

    def execute(self, *args, **kwargs):
        pass
