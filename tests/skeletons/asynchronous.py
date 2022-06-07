import asyncio
from zineb.http.request import HTTPRequest
from abc import abstractmethod
from collections.abc import AsyncGenerator
import requests
from zineb.http.request import HTTPRequest

# async def sender(url):
#     return requests.get(url)

# async def creator():
#     tasks = []
#     for i in range(10):
#         tasks.append(asyncio.ensure_future(sender('http://example.com')))
#     responses = await asyncio.gather(*tasks)
#     return responses

# if __name__ == '__main__':
#     loop = asyncio.get_event_loop()
#     # print(responses)
#     future = asyncio.ensure_future(creator())
#     loop.run_until_complete(future)
#     responses = future.result()
#     print(responses)



async def request1():
    request = HTTPRequest('https://jsonplaceholder.typicode.com/todos')
    request._send()
    print(1)
    return request


async def request2():
    request = HTTPRequest('https://jsonplaceholder.typicode.com/posts')
    request._send()
    print(2)
    return request

async def request3():
    await asyncio.sleep(2)
    print(3)
    return 'Last'


async def main():
    task1 = asyncio.create_task(request1())
    task2 = asyncio.create_task(request2())
    task3 = asyncio.create_task(request3())

    # response1 = await task1
    # response2 = await task2
    # responses = await asyncio.wait([task1, task2])
    return await asyncio.gather(task1, task2, task3)

result = asyncio.run(main())
print(result)
# # loop = asyncio.get_event_loop()
# # items = loop.run_until_complete(main())
# # loop.close()
# loop = asyncio.get_event_loop()
# future = asyncio.ensure_future(main())
# loop.run_until_complete(future)
# responses = future.result()
# loop.close()
# print(responses)

# class RequestQueue:
#     def __init__(self):
#         self.urls = [
#             HTTPRequest('http://example.com'),
#             HTTPRequest('http://example.com'),
#             HTTPRequest('https://jsonplaceholder.typicode.com/photos'),
#             HTTPRequest('http://example.com'),
#             HTTPRequest('http://example.com'),
#             HTTPRequest('http://example.com'),
#             HTTPRequest('https://jsonplaceholder.typicode.com/todos'),
#             HTTPRequest('http://example.com'),
#             HTTPRequest('http://example.com'),
#             HTTPRequest('http://example.com'),
#             HTTPRequest('http://example.com'),
#             HTTPRequest('https://jsonplaceholder.typicode.com/todos'),
#             HTTPRequest('http://example.com'),
#             HTTPRequest('https://jsonplaceholder.typicode.com/photos')
#         ]
#         self.responses = []

#     def __iter__(self):
#         return self.send1()

#     def send1(self):
#         async def sender(request):
#             request._send()
#             return request

#         async def main():
#             tasks = [asyncio.create_task(sender(item)) for item in self.urls]
#             responses = await asyncio.gather(*tasks)
#             self.responses = responses

#         loop = asyncio.get_event_loop()
#         return loop.run_until_complete(main())

#         # return asyncio.run(main())

#     def send2(self):
#         for item in self.urls:
#             item._send()
#             self.responses.append(item)
#         return self.responses

# import time
# s = time.time()
# q = RequestQueue()
# q.send2()
# print(q.responses)
# e = time.time()
# print(round(e - s, 2))
