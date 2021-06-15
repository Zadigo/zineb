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
import subprocess
import sys
import unittest

from zineb.management import Utility, collect_commands, load_command_class
from zineb.management.base import BaseCommand


class TestCommandCollection(unittest.TestCase):
    def test_has_paths(self):
        commands_paths = list(collect_commands())
        self.assertTrue(len(commands_paths) > 0)

        sample_path = commands_paths[0]
        self.assertTrue(sample_path.endswith('.py'))
        self.assertIn('\\shell.py', sample_path)


class TestLoadCommand(unittest.TestCase):
    def test_can_get_command(self):
        command = load_command_class('start')
        self.assertTrue(isinstance(command, BaseCommand))


class TestUtility(unittest.TestCase):
    def setUp(self):
        self.utility = Utility()

    def test_registry_is_not_empty(self):
        self.assertTrue(len(self.utility.commands_registry.values()) > 0)

    def test_can_call_command(self):
        pass
        # command = self.utility.call_command(['manage.py', 'start'])
        # subprocess.call(['python', 'tests/testproject/manage.py'], stderr=subprocess.STDOUT)


ARGUMENTS = ['python', os.path.join(os.path.dirname(__file__), 'testproject/manage.py')]

COMMANDS = ['create_spider']

class TestCommands(unittest.TestCase):
    def test_create_spider(self):
        ARGUMENTS.extend(['create_spider', 'Google'])
        subprocess.call(ARGUMENTS, stderr=subprocess.STDOUT)


if __name__ == '__main__':
    # unittest.main()

    runner = unittest.TextTestRunner()
    suite = unittest.TestSuite()
    suite.addTest(TestCommands('test_create_spider'))
    runner.run(suite)
