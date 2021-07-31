from zineb.middlewares.wireframe import WireFrame
from zineb.http.request import HTTPRequest

request = HTTPRequest('http://example.com')
request._send()
wireframe = WireFrame(request.html_response)





# cache = {'a': [], 'b': []}

# def add_value(name, value):
#     cache[name].append(value)
#     lengths = [[key, len(values)] for key, values in cache.items()]
#     for i in range(0, len(lengths)):
#         x = i + 1
#         if x >= len(lengths):
#             break
#         if lengths[x][1] < lengths[i][1]:
#             cache[lengths[x][0]].append(None)
#         if lengths[x][1] == lengths[i][1]:
#             cache[lengths[i][0]].insert(x, value)

# add_value('a', 1)
# add_value('a', 2)
# add_value('b', 3)
# print(cache)
