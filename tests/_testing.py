import json
import threading

from bs4 import BeautifulSoup
from zineb.extractors.links import LinkExtractor
from zineb.http.request import JsonRequest

def get():
    with open('tests/html/matchstat.html') as f:
        soup = BeautifulSoup(f, 'html.parser')

        extractor = LinkExtractor(url_must_contain='match-stats/w/')
        extractor.resolve(soup)

        with extractor as links:
            values = []
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0'
            }
            settings = {
                'proxies': [
                    ('http', '91.202.240.208'),
                    ('https', '81.211.103.66'),
                    ('https', '200.73.129.108')
                ]
            }
            for i, link in enumerate(links):
                request = JsonRequest(link, headers=headers, settings=settings)
                request._send()
                if request._http_response.ok:
                    yield request.json_response.raw_data
            #     values.append(match)
            
            # with open('bouchard.json', 'w') as b:
            #     json.dump(values, b, indent=4)


with open('bouchard1.json', 'w') as f:
    json.dump(list(get()), f)
