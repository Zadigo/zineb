import os
import sys

from zineb.management import execute_command_inline

os.environ.setdefault('ZINEB_SPIDER_PROJECT', 'project5.settings')
cmds = sys.argv
cmds.extend(['start'])
execute_command_inline(cmds)
