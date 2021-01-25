from management import Utility, load_command_class
from zineb.management import collect_commands

# print(list(collect_commands()))

u = Utility()
u.call_command('start')
