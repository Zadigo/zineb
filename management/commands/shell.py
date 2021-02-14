import code

from zineb.extractors import base, links, images
from zineb.http.request import HTTPRequest
from zineb.management.base import BaseCommand
from zineb.settings import settings


def start_ipython_shell():
    try:
        from IPython.terminal import embed, ipapp
    except:
        return False
    else:
        configuration = ipapp.load_default_config()

        def shell_wrapper(namespace: dict={}, banner=''):
            embed.InteractiveShellEmbed.clear_instance()
            shell = embed.InteractiveShellEmbed.instance(
                banner=banner, user_ns=namespace, config=configuration
            )
            shell()
        return shell_wrapper


def start_standard_console():
    def shell_wrapper(namespace: dict={}, banner=''):
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
                    # and banner
                    func()(namespace=self.shell_variables, banner=self.banner)
            except SystemError:
                pass

    def start(self, url):
        request = HTTPRequest(url)
        request.project_settings = settings
        request._send()

        self.shell_variables.setdefault('request', request)
        self.shell_variables.setdefault('response', request.html_response)
        self.shell_variables.setdefault(
            'html_page', request.html_response.html_page
        )

        # Pass the extractors in the shell
        self.shell_variables.setdefault('base', base)
        self.shell_variables.setdefault('images', images)
        self.shell_variables.setdefault('links', links)
        self._start_consoles()


class Command(BaseCommand):
    def add_arguments(self, parser):
        pass

    def execute(self, *args, **kwargs):
        pass
