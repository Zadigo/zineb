from zineb.extractors.base import Extractor
from bs4.element import Tag

class ImageExtractor(Extractor):
    def __init__(self, unique=False, as_type=None,
                 url_must_contain=None, match_height=None, match_width=None):
        self.images = []
        self.unique = unique
        self.as_type = as_type
        self.url_must_contain = url_must_contain
        self.match_height = match_height
        self.match_width = match_width

    def __len__(self):
        return len(self.images)

    def __getitem__(self, index):
        return self.images[index] if self.images else []

    def _document_images(self, soup):
        from zineb.http.responses import HTMLResponse
        if isinstance(soup, HTMLResponse):
            soup = soup.html_page
        elif isinstance(soup, Tag):
            soup = soup
        return soup.find_all('img')

    def _image_iterator(self, soup):
        for image in self._document_images(soup):
            yield image, image.attrs

    def resolve(self, soup):
        from zineb.dom.tags import ImageTag
        images = self._image_iterator(soup)
        for i, image in enumerate(images):
            tag, attrs = image
            self.images.append(
                ImageTag(tag, attrs=attrs, src=attrs.get('src', None), index=i)
            )
        return self.images

    def filter_images(self, expression=None):
        filtered_images = []
        images = self.images.copy()

        if expression is not None:
            filtered_images = filter(
                lambda x: expression in x, images
            )

        if self.unique:
            images = set(self.images)

        if self.as_type is not None:
            filtered_images = filter(
                lambda x: x.endswith(self.as_type), images
            )

        if self.url_must_contain is not None:
            filtered_images = filter(
                lambda x: self.url_must_contain in x, images
            )

        if self.match_height is not None:
            filtered_images = []
            for image in images:
                height = image.attrs.get('height', None)
                if height is not None:
                    if height == self.match_height:
                        filtered_images.append(image)

        if self.match_width is not None:
            filtered_images = []
            for image in images:
                height = image.attrs.get('width', None)
                if height is not None:
                    if height == self.match_width:
                        filtered_images.append(image)

        return list(filtered_images)
