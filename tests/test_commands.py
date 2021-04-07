import sys
import unittest

from management import Utility, load_command_class
from zineb.management import collect_commands, execute_command_inline
from zineb.management.base import BaseCommand

# utility = Utility()


# class TestExecuteInline(unittest.TestCase):
#     def test_execution(self):
#         # execute_command_inline(sys.argv)
#         pass


# class TestBaseCommand(unittest.TestCase):
#     def test_new_project_command(self):
#         command = utility.call_command(sys.argv)
#         # self.assertIsInstance(command, BaseCommand)
#         # command = execute_command_inline('')


if __name__ == '__main__':
    # unittest.main()
    u = Utility()
    u.call_command(sys.argv)
