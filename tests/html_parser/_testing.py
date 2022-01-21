import requests
from zineb.html_parser.html_tags import ElementData, Tag
from zineb.html_parser.parsers import Extractor, General
from zineb.html_parser.queryset import QuerySet
from zineb.html_parser.utils import (filter_by_attrs, filter_by_name,
                                     filter_by_name_or_attrs)
from zineb.tests.html_parser import items

# # """
# # <html>
# #     <body>
# #         <a href="http://example.com" id="test">Click</a>
# #         <a href="http://example.com">Click</a>
# #     </body>
# # </html>
# # """

# # html = Tag('html')
# # body = Tag('body')
# # link1 = Tag('a', attrs=[('id', 'test'), ('href', 'http://example.com')])
# # link2 = Tag('a', attrs=[('href', 'http://example.com')])

# # link_data = ElementData('Click')
# # link1._internal_data = [link_data]
# # link2._internal_data = [link_data]

# # html._children = [body, link1, link2]
# # body._children = [link1, link2]

# # collected_tags = [html, body, link1, link_data, link2, link_data]

# # queryset = QuerySet.copy(collected_tags)


# # Test extractor


# # extractor = Extractor()
# # virtual_tree = ['html', 'body', 'a']
# # for item in virtual_tree:
# #     extractor.start_tag(item, [], position=(None, None))
    
# # for item in virtual_tree:
# #     extractor.end_tag(item)

# # html = extractor.container[0]
# # body = extractor.container[1]



# # # e = Extractor()
# # # e.resolve(items.NORMAL_HTML)

# # from lxml.etree import tostring
# # from lxml.html import fromstring

# # h = fromstring(items.NORMAL_HTML)
# # r = tostring(h, encoding='unicode', pretty_print=True)
# # e = Extractor()
# # e.resolve(r)
# # print(e)

# # from zineb.tests.html_parser import items

# # h = General()
# # s = """<div id="1"><span>1</span></div><div id="2"></div>"""
# # h.resolve(s)
# # div = h.manager.find_all('div')
# # print(h.manager)



# # r = requests.get('http://example.com')
# # g = General()
# # g.resolve(r.content)
# # link = g.manager.find('h1')
# # print(link.get_all_next('a'))


# # html = Tag('html')
# # body = Tag('body')
# # span = Tag('span')

# # span_data = ElementData('Something')
# # span._internal_data = [span_data]

# # html._children = [body, span, span_data]
# # body._children = [span, span_data]

# # container = [html, body, span, span_data]

# # queryset = QuerySet.copy(container)
# # print(queryset.contains('a'))




# e = General()
# e.resolve(items.NORMAL_HTML)
# a = e.manager.find('a')
# print(a._internal_data)

