from bs4 import BeautifulSoup
from zineb.models.datastructure import Model
from zineb.models.fields import UrlField

with open('tests/html/simpggle.html') as f:
    soup = BeautifulSoup(f, 'html.parser')

class Player(Model):
    name = UrlField()

player = Player(html_document=soup)
player.add_expression('name', 'a#jenner__href')
print(player)

