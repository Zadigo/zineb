import time

from bs4 import BeautifulSoup
from bs4.element import PageElement
from zineb.html_parser.parsers import General

s = time.time()

with open('tests/html_parser/test3.html', encoding='utf-8') as f:
    # soup = General(f)
    # result = soup.manager.find_all('section')
    
    soup = BeautifulSoup(f, 'html.parser')
    result = soup.find_all('section')
    
    print(len(result))
    
f = round((time.time() - s), 2)
print('Executed in', f, 'seconds')
