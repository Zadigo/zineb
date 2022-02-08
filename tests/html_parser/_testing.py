from bs4 import BeautifulSoup
from importlib_metadata import re
from zineb.html_parser.parsers import HTMLPageParser
import time
# from bs4 import BeautifulSoup

s = time.time()

f = open('tests/html_parser/test2.html', encoding='utf-8')
soup = HTMLPageParser(f)
body = soup.manager.find_all('div')
print(body)
# with open('tests/html_parser/test1.html', encoding='utf-8') as f:
#     soup = HTMLPageParser(f)
#     body = soup.manager.find('body')
#     # print(soup.manager.regex(re.compile(r'^img')))

#     # b = BeautifulSoup(f, 'html.parser')
#     # body = b.find('body')
#     # body.find_all('img')
f.close()
e = time.time() - s

print(round(e, 3))
