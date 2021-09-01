import subprocess
import os

ARGUMENTS = ['python', os.path.join(os.path.dirname(__file__), 'testproject/manage.py')]
ARGUMENTS.extend(['shell', '--url', 'http://www.fivb.org/EN/volleyball/competitions/U20/2013/Teams.asp'])

subprocess.call(ARGUMENTS, stderr=subprocess.STDOUT)
