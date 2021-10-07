# from zineb.models.datastructure import DataContainers

# container = DataContainers.as_container('name', 'age')

# container.update('name', 'Kendall')

# container.update('name', 'Kylie')
# container.update('age', 22)

# container.update('age', 26)

# print(container.values)

from zineb.http.request import XMLRequest
from zineb.management import execute_command_inline
import sys
import os

# os.environ.setdefault('ZINEB_SPIDER_PROJECT', 'tests.testproject.settings')

# execute_command_inline([os.path.abspath(__file__), 'createspider', 'Temptation'])
# execute_command_inline(sys.argv)

# from argparse import ArgumentParser

# parser = ArgumentParser()
# parser.add_argument('command')
# parser.add_argument('project')
# parser.add_argument('--settings')
# namespace = parser.parse_args()
# print(namespace)


request = XMLRequest('https://www.shein.com/sitemap-index.xml')
request._send()
