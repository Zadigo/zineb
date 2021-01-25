import re
from collections import deque

from nltk.tokenize import WordPunctTokenizer
from w3lib.url import urljoin
from zineb.extractors.base import Extractor


class LinkExtractor(Extractor):
    """
    Extract all links using a BeautifulSoup object

    This helper class is a useful wrapper for rapidly getting
    the links from a BeautifulSoup element

    Parameters
    ----------

        url_must_contain (str, optional): only get items which url contains x. Defaults to None.
        unique (bool, optional): links must be unique accross document. Defaults to False.
        base_url (str, optional): [description]. Defaults to None.
        only_valid_links (bool, optional): links must be valid (start with http). Defaults to False.
    """
    def __init__(self, url_must_contain=None, unique=False, 
                 base_url=None, only_valid_links=False):
        self.base_url = base_url
        self.unique = unique
        self.validated_links = []
        self.url_must_contain = url_must_contain
        self.only_valid_links = only_valid_links

    def __enter__(self):
        return self.validated_links

    def __exit__(self, exc_type, exc_val, exc_tb):
        return False

    def __len__(self):
        return len(self.validated_links)

    def __iter__(self):
        return iter(self.validated_links)

    def __getitem__(self, index):
        return self.validated_links[index]

    def __str__(self):
        return str(self.validated_links)

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
                if self.url_must_contain is not None:
                    attrs = tag.attrs
                    url = attrs.get('href')
                    if url is not None:
                        if self.url_must_contain in url:
                            yield tag, attrs
                else:
                    yield tag, tag.attrs

    def _recompose_path(self, path):
        if path.startswith('/'):    
            return urljoin(self.base_url, path)
        return path
 
    def _analyze_links(self):
        for link in self.validated_links:
            if link.is_email:
                yield link

    def _analyze_text(self, tokens):
        pattern = r'^(\w+\W?\w+\@\w+\W?\w+\.\w+)$'
        regex = re.compile(pattern)
        for token in tokens:
            is_match = regex.search(token)
            if is_match:
                yield is_match.group(1)

    def resolve_emails(self, soup):
        self.resolve(soup)

        text = soup.text
        tokenizer = WordPunctTokenizer()
        tokens = tokenizer.tokenize(text)

        emails_from_text = list(self._analyze_text(tokens))
        emails_from_links = list(self._analyze_links())
        return emails_from_links + emails_from_text

    def resolve(self, soup):
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
        from zineb.tags import Link
        if soup is None:
            return None
            
        tags = self._link_iterator(soup)
        for tag in tags:
            element, attrs = tag
            href = attrs.get('href', None)
            if href is not None:
                attrs['href'] = self._recompose_path(attrs['href'])
            self.validated_links.append(Link(element, attrs=attrs))

        if self.unique:
            self.validated_links = {
                link for link in self.validated_links
            }

        if self.only_valid_links:
            self.validated_links = list(
                filter(lambda x: x.is_valid, self.validated_links)
            )
