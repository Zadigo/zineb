from collections import OrderedDict, deque
from functools import cached_property

from w3lib.html import strip_html5_whitespace
from w3lib.url import is_url, urljoin
from zineb.extractors.base import Extractor


class LinkExtractor:
    def __init__(self, url_must_contain=None, unique=False, base_url=None):
        self.base_url = base_url
        self.unique = unique
        self.validated_links = []

    def __len__(self):
        return len(self.validated_links)

    def __iter__(self):
        return iter(self.validated_links)

    def _document_links(self, soup):
        """
        Return all the document's links

        Parameters
        ----------

            soup (type): BeautifulSoup object

        Returns
        -------

            list: list of links
        """
        from zineb.http.responses import HTMLResponse
        if isinstance(soup, HTMLResponse):
            soup = soup.html_page
        return soup.find_all('a')

    def _link_iterator(self, soup):
        """
        Iterate on link BeautifulSoup ResultSet

        Parameters
        ----------

            soup (type): BeautifulSoup object

        Yields
        ------

            tuple: link (href) and link attributes
        """
        for tag in self._document_links(soup):
            element_name = tag.name
            if tag and element_name == 'a' and isinstance(element_name, str):
                yield tag, tag.attrs

    def _recompose_path(self, path):
        return urljoin(self.base_url, path)

    def finalize(self, soup):
        """
        Return all the lists from a given
        document

        Parameters
        ----------

            soup (type): BeautifulSoup object

        Returns
        -------

            list: complete list of links
        """
        from zineb.html.tags import Link
        if soup is None:
            return []
            
        tags = self._link_iterator(soup)
        for tag in tags:
            element, attrs = tag
            href = attrs.get('href', None)
            if href is not None:
                attrs['href'] = self._recompose_path(attrs['href'])
            self.validated_links.append(Link(element, attrs=attrs))
        return self.validated_links
