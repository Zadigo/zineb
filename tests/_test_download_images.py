from zineb.app import Zineb
from zineb.extractors.base import ImageExtractor
from zineb.http.pipelines import ResponsesPipeline
from zineb.utils.general import download_image, replace_urls_suffix


def fix_url(url:str):
    url = url.removeprefix('_thumbnail-150x240.jpg')
    return url + '.jpg'


class HawtCeleb(Zineb):
    start_urls = [
        'https://www.hawtcelebs.com/kimberley-garner-in-a-colorful-bikini-at-a-beach-in-miami-01-07-2021/'
    ]

    def start(self, response, **kwargs):
        request = kwargs.get('request')

        extractor = ImageExtractor(unique=True)
        extractor.resolve(response)
        images = extractor.filter_images('attachment-thumbnail')
        
        url_images = replace_urls_suffix(images, '_thumbnail.jpg', '.jpg')
        responses = request.follow_all(url_images[:2])
        ResponsesPipeline(responses, [download_image], parameters={'download_to': 'tests/media'})

spider = HawtCeleb()
