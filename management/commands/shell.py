import code

from zineb.extractors import base as base_extractors
from zineb.http.request import HTTPRequest
from zineb.logger import global_logger
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
                    # that will be available within the shell
                    # and the banner
                    func()(namespace=self.shell_variables, banner=self.banner)
            except SystemError:
                pass

    def start(self, url, use_settings=None):
        from zineb.settings import settings as global_settings

        request = HTTPRequest(url)
        # request.project_settings = use_settings or global_settings
        request._send()

        # When the request fails, the html_response
        # is None which raises an Attribute error.
        # This creates a more user friendly error
        # to better understand what's going on
        if request.html_response is not None:
            self.shell_variables.setdefault('request', request)
            self.shell_variables.setdefault('response', request.html_response)

            self.shell_variables.setdefault('html_page', request.html_response.html_page)

            # Pass the extractors in the shell
            self.shell_variables.setdefault('extractors', base_extractors)
            self.shell_variables.setdefault('images', base_extractors.ImageExtractor)
            self.shell_variables.setdefault('links', base_extractors.LinkExtractor)
            self.shell_variables.setdefault('multilinks', base_extractors.MultiLinkExtractor)
            self.shell_variables.setdefault('table', base_extractors.TableExtractor)

            # Pass the project setttings
            self.shell_variables.setdefault('settings', global_settings)
            self._start_consoles()
        else:
            global_logger.logger.error("Shells failed to start because the response "
            "did not return a valid success code. Try pinging the url for validity.")

    def start_file_shell(self, filepath, use_settings=None):
        import os

        from bs4 import BeautifulSoup
        from zineb.settings import settings as global_settings

        with open(os.path.join(global_settings.PROJECT_PATH, filepath), mode='r') as f:
            soup = BeautifulSoup(f, 'html.parser')

        self.shell_variables.setdefault('soup', soup)
        self.shell_variables.setdefault('settings', global_settings)

        self._start_consoles()


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--url', type=str, help='Opens a shell with a given url request')
        parser.add_argument('--file', type=str, help='Opens a shell with the given file')

    def execute(self, namespace):
        configured_settings = self.preconfigure_project()

        shell = Shell()

        # Allows the user to create a shell
        # for a specific file to work on
        # within a project --; one of file
        # or url should be provided and if
        # none a provided, raise an error
        filepath = namespace.file
        if filepath:
            shell.start_file_shell(filepath, use_settings=configured_settings)
        else:
            url = namespace.url
            if url is None:
                raise ValueError(("Did you provide a url when calling shell? "
                "ex. python manage.py shell --url http://"))
            shell.start(url=url, use_settings=configured_settings)
