import requests
import asyncio
import time
from collections.abc import AsyncGenerator

s = time.time()
u = []

urls = [
    'https://data.opendatasoft.com/api/records/1.0/search/?dataset=rail-traffic-information%40sbb&q=',
    'http://example.com',
    'https://jsonplaceholder.typicode.com/posts',
    'https://jsonplaceholder.typicode.com/posts/1/comments',
    'https://data.opendatasoft.com/api/records/1.0/search/?dataset=met_affichage-reglementaire%40scnbdx&q='
]


class X(AsyncGenerator):
    async def __asend__(self):
        return

    def __aiter__(self):
        return self

    async def __athrow__(self):
        return

    def __anext__(self):
        return next(urls)


async def a(url):
    print('Completed', url)
    response = requests.get(url)
    return response


async def main():
    m = [a(url) for url in urls]
    tasks = [asyncio.create_task(x) for x in m]
    return await asyncio.gather(*tasks)


async def main2():
    w, x = await asyncio.as_completed(X)
    for d in x:
        print(await d)
    print(w, x)


w = asyncio.run(main2())

e = (round(time.time() - s, 3))

print(e)
