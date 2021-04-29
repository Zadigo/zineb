from zineb.models.datastructure import Model
from zineb.models.fields import CharField
from bs4 import BeautifulSoup

class TestModel(Model):
    name = CharField()

with open('tests/html/test_links.html') as f:
    soup = BeautifulSoup(f, 'html.parser')
    model = TestModel(html_document=soup)
    model.add_using_expression('name', 'a', attrs={'class': 'title'})
    print(model.save(commit=False))
