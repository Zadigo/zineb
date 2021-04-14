import code

from zineb.extractors import base as base_extractors
from zineb.http.request import HTTPRequest
from zineb.management.base import BaseCommand


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

    def start(self, url, use_settings=None):
        from zineb.settings import settings as global_settings
        # Force reload to take into account
        # the user's settings. See related issue.
        global_settings()

        request = HTTPRequest(url)
        request.project_settings = use_settings or global_settings
        request._send()

        self.shell_variables.setdefault('request', request)
        self.shell_variables.setdefault('response', request.html_response)
        self.shell_variables.setdefault('html_page', request.html_response.html_page)

        # Pass the extractors in the shell
        self.shell_variables.setdefault('base', base_extractors)
        self.shell_variables.setdefault('images', base_extractors.ImageExtractor)
        self.shell_variables.setdefault('links', base_extractors.LinkExtractor)
        self.shell_variables.setdefault('multilinks', base_extractors.MultiLinkExtractor)
        self.shell_variables.setdefault('table', base_extractors.TableExtractor)

        # Pass the project setttings
        self.shell_variables.setdefault('settings', global_settings)
        self._start_consoles()


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--url', type=str, help='Url to use for testing')

    def execute(self, namespace):
        shell = Shell()
        url = namespace.url
        if url is None:
            raise ValueError(("Did you provide a url when calling shell? "
            "ex. python manage.py shell --url http://"))
        shell.start(url=url)
