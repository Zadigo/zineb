"""
Call this class in order to test the generic project
in tests/testproject. This is done in order to quickly
test the overall processes and functionnalities
"""

import os
import subprocess

if __name__ == '__main__':
    arguments = ['python', os.path.join(os.path.dirname(__file__), 'testproject/manage.py'), 'start']
    subprocess.call(arguments, stderr=subprocess.STDOUT)
