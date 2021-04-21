import re
from functools import lru_cache
from mimetypes import guess_extension, guess_type
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup
from bs4.element import Tag
from w3lib.url import canonicalize_url, is_url, safe_url_string


class BaseTags:
    def __init__(self, html_page):
        self.html_page = None
        if isinstance(html_page, str):
            # There might be some cases where an HTML string
            # is passed while not being a BeautifulSoup instance
            # at the same time. We can account for this here.
            self.html_page = BeautifulSoup(html_page, 'html.parser')
        elif isinstance(html_page, BeautifulSoup):
            self.html_page = html_page


class HTMLTag(BaseTags):
    tag_name = None

    def __init__(self, tag: Tag, html_page: BeautifulSoup=None, **kwargs):
        super().__init__(html_page)
        self.tag = tag
        self.attrs = kwargs.get('attrs', tag.attrs)

        try:
            self.tag_name = self.tag.name.strip()
        except:
            raise TypeError(
                'HTML tag should be a BeautifulSoup instance'
            )

    def __repr__(self):
        return f"{self.__class__.__name__}(tag={self.tag_name})"


class Link(HTMLTag):
    """
    Represents a link HTML tag

    Parameters
    ----------

        tag (src): a BeautifulSoup image object
    """
    def __init__(self, tag: Tag, **kwargs):
        self.tag = tag
        self.text = tag.text
        self.attrs = kwargs.get('attrs', tag.attrs)
        href = self.attrs.get('href', None)
        
        self.href = href
        self.is_email = False
        if href is not None:
            base_url = kwargs.get('base_url', None)
            if base_url is not None:
                href = urljoin(base_url, href)

            if 'mailto:' in href:
                self.is_email = True
                is_match = re.search(r'^mailto:(.*)$', href)
                if is_match:
                    href = is_match.group(1)
                else:
                    href = href

            href = safe_url_string(canonicalize_url(href))

            try:
                self.is_valid = is_url(href)
            except AttributeError:
                self.is_valid = False
            else:
                self.href = href

                if self.is_email:
                    self.is_valid = True
        else:
            self.is_valid = False
        super().__init__(tag, **kwargs)

    def __eq__(self, link):
        return self.href == link

    def __add__(self, path):
        return urljoin(self.href, path)

    def __contains__(self, value_to_test):
        logic_to_test = []

        if self.href is not None:
            logic_to_test.extend([value_to_test in self.href])

        # if self.attrs:
        #     element_class = self.attrs.get('class')
        #     element_id = self.attrs.get('id')
        #     if element_class is not None:
        #         logic_to_test.extend([value_to_test in element_class])

        #     if element_id is not None:
        #         logic_to_test.extend([value_to_test in element_id])

        if logic_to_test:
            return any(logic_to_test)
            
        return False

    def __str__(self):
        return str(self.href)

    def __hash__(self):
        return hash(self.href)

    def __repr__(self):
        if self.is_email:
            return f"{self.__class__.__name__}(email={self.href})"
        return f"{self.__class__.__name__}(url={self.href}, valid={self.is_valid})"

    @property
    def decompose(self):
        return urlparse(self.href)

    @property
    def domain(self):
        return self.decompose[1]


class ImageTag(HTMLTag):
    """
    Represents an image HTML tag

    Parameters
    ----------

        tag (src): a BeautifulSoup image object
        index (int):
    """
    def __init__(self, tag: Tag, index=None, **kwargs):
        super().__init__(tag, **kwargs)
        self.index = index
        self.src = self.attrs.get('src', None)
        self.is_valid = is_url(self.src)
        self.image_type = guess_type(self.src)
        self.extension = guess_extension(self.image_type[0])

    def __repr__(self):
        return f"{self.__class__.__name__}(src={self.src})"

    def __str__(self):
        return str(self.src)

    def __hash__(self):
        return hash((self.src, self.image_type))

    def __contains__(self, value_to_test):
        # Checks that a value is present in of
        # either the image url, class or id
        truth_values = [
            value_to_test in self.src
        ]
        class_attr = self.attrs.get('class')
        if class_attr:
            truth_values.append(value_to_test in class_attr)
        id_attr = self.attrs.get('id')
        if id_attr:
            truth_values.append(value_to_test in id_attr)
        return any(truth_values)

    def __eq__(self, src):
        return src == self.src

    @property
    def href(self):
        return self.src


class TableTag(HTMLTag):
    def __init__(self, tag: Tag, html_page: BeautifulSoup, index: int=None, **kwargs):
        self.tag = tag
        self.html_page = html_page
        self.index = index
        self.attrs = kwargs.get('attrs', tag.attrs)
        super().__init__(tag, html_page=html_page, **kwargs)

    def __repr__(self):
        return f"{self.__class__.__name__}(values={self.__len__()})"

    def __str__(self):
        return self.tag

    def __iter__(self):
        return iter(self.rows)

    def __len__(self):
        return len(self.rows)

    def __contains__(self, a):
        result = False
        for item in self.data:
            if a in item:
                result =True
                break
        return result

    @property
    def rows(self):
        return self.tag.find_all('tr')

    @property
    def columns(self):
        return self.rows.find_all('td')

    @property
    def header(self):
        return self.rows[:1]

    @lru_cache(maxsize=2)
    def data(self):
        from zineb.extractors.base import TableExtractor
        extractor = TableExtractor()
        return extractor, extractor.resolve(self.tag)
