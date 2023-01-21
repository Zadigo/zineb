"""
The commands process works in the following manner:

    1. The `collect_commands` is called in order to get all the
       paths to the command files within the commands directory
    
    2. Once the commands are loaded, it is possible then to load
       a command class using the `load_command_class` method

To execute a command from the `manage.py` file, the `execute_command_inline`
is called using the element name that was appended ex. `python manage.py start`.

This is passed to the `Utility` class whose role is to execute the command but also
register them into it's own internal registry.

Once the command class is retrieved, the `create_parser` method is called from the `BaseCommand`
class which will implement all the main commands to run for that specific command.
create an `ArgumentParser` for that specific command

This in turn calls the `add_arguments` including therefore all other
additional commands that can be used with that very specific command.
"""

import os
import pathlib
import subprocess
import sys
import unittest

from zineb.management import Utility, collect_commands, load_command_class
from zineb.management.base import BaseCommand
from zineb.settings import settings


class TestCommandCollection(unittest.TestCase):
    def test_has_paths(self):
        commands_paths = list(collect_commands())
        self.assertTrue(len(commands_paths) > 0)

        sample_path = commands_paths[0]
        self.assertTrue(sample_path.endswith('.py'))
        self.assertIn('\\createspider.py', sample_path)


class TestLoadCommands(unittest.TestCase):
    def test_can_load_command(self):
        command = load_command_class('start')
        self.assertTrue(isinstance(command, BaseCommand))


class TestUtility(unittest.TestCase):
    def setUp(self):
        self.utility = Utility()

    def test_registry_is_not_empty(self):
        self.assertGreater(len(self.utility.commands_registry), 0)

    def test_command_calling_in_project(self):
        os.environ.setdefault('ZINEB_SPIDER_PROJECT',
                              'zineb.tests.testproject')

        settings()

        ARGUMENTS = ['python', pathlib.Path(
            settings.PROJECT_PATH).joinpath('manage.py')]
        ARGUMENTS.extend(['ping', '-n', '1', '167.114.222.149'])
        subprocess.call(ARGUMENTS, stderr=subprocess.STDOUT)


if __name__ == '__main__':
    unittest.main()
