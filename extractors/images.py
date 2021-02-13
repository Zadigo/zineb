from zineb.extractors.base import Extractor
from bs4.element import Tag

class ImageExtractor(Extractor):
    """
    Extracts all the images from a document

    Parameters
    ----------

        unique (bool, Optional): if images should be unique. Defaults to False
        as_type (str, Optional): get images only from a specific extension. Defaults to None
        url_must_contain: (str, Optional): images with a specific url. Defaults to None
        match_height: (int, Optional): images of a certain height
        match_width: (int, Optional): images of a certain width
    """
    def __init__(self, unique=False, as_type=None,
                 url_must_contain=None, match_height=None, 
                 match_width=None):
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
        from zineb.tags import ImageTag
        images = self._image_iterator(soup)
        for i, image in enumerate(images):
            tag, attrs = image
            self.images.append(
                ImageTag(tag, attrs=attrs, index=i, html_page=soup)
            )
        return self.images

    def filter_images(self, expression=None):
        expression = expression or self.url_must_contain
        
        images = self.images.copy()

        if self.unique:
            images = list(set(images))

        if expression is not None:
            images = list(filter(lambda x: expression in x, images))

        if self.as_type is not None:
            images = list(filter(lambda x: x.endswith(self.as_type), images))

        if self.url_must_contain is not None:
            images = list(filter(lambda x: self.url_must_contain in x, images))

        if self.match_height is not None:
            filtered_images = []
            for image in images:
                height = image.attrs.get('height', None)
                if height is not None:
                    if height == self.match_height:
                        filtered_images.append(image)
            images = filtered_images

        if self.match_width is not None:
            filtered_images = []
            for image in images:
                height = image.attrs.get('width', None)
                if height is not None:
                    if height == self.match_width:
                        filtered_images.append(image)
            images = filtered_images
        return images
