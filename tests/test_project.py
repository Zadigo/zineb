import subprocess
import os

if __name__ == '__main__':
    arguments = ['python', os.path.join(os.path.dirname(__file__), 'testproject/manage.py'), 'start']
    subprocess.call(arguments, stderr=subprocess.STDOUT)
