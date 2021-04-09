#!/usr/bin/env python

import sys
import os
from zineb.management import execute_command_inline

if __name__ == '__main__':
    os.environ.setdefault('ZINEB_SPIDER_PROJECT', 'tests.testproject.settings')
    execute_command_inline(sys.argv)
