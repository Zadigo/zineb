from lxml import etree

# find('div')
# //body/div[1]
# find_all('div')
# //body/div
# find('div', attrs={'class': 'a'})
# //body/div[@class="a"]
# find(F(div__eq='Google', 'class'))
# //body/div[contains(@class, "a")]
# find_all(...).exists()
# find(div__class__contains='google')
# find(div__class__eq='google')
# find(div__class='google').last(div__position=1)
# find_all(Case(When(div__eq=1), When(div__lt=1)))
# find_all(Q(a__class='a') | Q(a__class='b'))
# find_all(Q(a__class='a') & Q(a__class='b'))
# find_all(~Q(a__class='a'))
# tables()
# //*[text()]
# get_all_text()
# get(div__class__eq='a')
# X('body', 'div', 'div@id=google', 'div@position=3', 'div@first', 'a', 'href')

class XPathCompiler:
    child = '/'
    descendent = '//'
    any = '*'
    body = '/body'
    nth_of_type = '[{index}]'
    last_of_type = '[last()]'
    fist_child = ''
    attribute = '[@{attr}={value}]'
    starts_with = '[starts-with(@{attr}, "{value}")]'
    ends_with = '[ends-with(@{attr}, "{value}")]'
    contains = '[contains(@{attr}, "{value}")]'
    following_sibling = 'following-sibling::{param}'
    text_match = '[text()="{value}"]'
    text_match_substring = '[contains(text(),"{value}")]'
    arithmetic = '[@{attr} {operator} {value}]'
    or_logic = 'or'
    union = '|'
    position = '[position()={index}]'
    attribute = '@'
    ancestor = 'ancestor'

    def __init__(self, query, model=None):
        self.html_object = None
        self.query = query
        self.model = model
        self.xpath = None
        self.parser = etree.HTMLParser()
    
    def setup_xpath(self):
        self.xpath = ''

    def pre_xpath_setup(self):
        self.setup_xpath()
        self.html_object = etree.fromstring(self.query.html_content, self.parser)
        return '', None, None

    def as_xpath(self):
        return ''

    def execute_xpath(self):
        result = self.query.get_compiler().execute_xpath(self.xpath)
        return result
