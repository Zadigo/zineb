import time
from attr import attr

from bs4 import BeautifulSoup
from bs4.element import PageElement
from zineb.html_parser.parsers import HTMLPageParser

s = time.time()

with open('tests/html_parser/test3.html', encoding='utf-8') as f:
    # soup = HTMLPageParser(f)
    # result = soup.manager.find_all('div', attrs={'id': 'gallery-columns-5'})
    
    soup = BeautifulSoup(f, 'html.parser')
    result = soup.find_all('div', attrs={'id': 'gallery-columns-5'})
    
    print(len(result))
    
f = round((time.time() - s), 2)
print('Executed in', f, 'seconds')
