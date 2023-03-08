# find('div')
# //body/div[1]
# find_all('div')
# //body/div
# find('div', attrs={'class': 'a'})
# //body/div[@class="a"]
# find(F('div', 'contains', 'class=a))
# //body/div[contains(@class, "a")]

class Query:
    compiler = 'XPathCompiler'

    def __init__(self):
        self.html_content = '<html><body></body></html>'

    def __str__(self):
        return ''

    def clone(self):
        pass

    def get_compiler(self, using=None):
        pass

    def get_initial_alias(self):
        return ['//']
