from bs4 import BeautifulSoup

HTML = """<html><div></div><div></div></html>"""

soup = BeautifulSoup(HTML, 'html.parser')
soup.find_all('div')
