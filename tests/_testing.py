# from zineb.app import Options


# options = Options(domains=['http://example.com'])
# print(options.check_url_domain('example.com'))

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
