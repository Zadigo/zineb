import copy
import os
import re
from collections import OrderedDict
from functools import cached_property
from itertools import chain
from typing import List, NoReturn, Union

from bs4 import BeautifulSoup
from bs4.element import ResultSet, Tag
from w3lib.html import safe_url_string
from w3lib.url import is_url, urljoin
from zineb.extractors._mixins import MultipleRowsMixin
from zineb.settings import settings
from zineb.utils.characters import deep_clean
from zineb.utils.decoders import decode_email
from zineb.utils.iteration import keep_while
from zineb.utils.paths import is_path


class Extractor:
    """
    Base class for every extractor class
    """
    def __enter__(self):
        raise NotImplementedError('__enter__ should be implemented by the subclasses')
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        return False

    @cached_property
    def cached_items(self):
        """
        Return the original list of extracted
        elements on the page
        """
        raise NotImplementedError(('Subclasses should provide a way'
        ' to return the orginal data'))

    def _check_response(self, response):
        from zineb.http.responses import HTMLResponse
        if isinstance(response, HTMLResponse):
            return response.html_page
        return response

    def resolve(self, soup: BeautifulSoup) -> NoReturn:
        raise NotImplementedError(('Provide functionnalities for quickly '
        'extracting items from the HTML page'))


class TableExtractor(Extractor):
    """
    Quickly extract a table from an HTML page.
    
    By default this class retrieves the first table of the page if no
    additional information is provided on which table to extract.

    Parameters
    ----------

        - class_or_id_name (str, Optionnal): the class name of the table. Defaults to None
        - has_headers (bool, Optionnal): indicates if the table has headers. Defaults to False
        - processors (func, Optionnal): list of functions to process the final result. Defaults to None

    
        Example
        -------

            extractor = TableExtractor()
            extractor.resolve(BeautifulSoup Object)

                [[a, b, c], [d, ...]]

            By indicating if the table has a header, the header values 
            which generally corresponds to the first row will be dropped
            from the final result.

            Finally, you can also pass a set of processors that will modifiy the values
            of each rows according to the logic you would have implemented.

            def drop_empty_values(value):
                if value != '':
                    return value

            extractor = TableExtractor(processors=[drop_empty_values])
            extractor.resolve(BeautifulSoup Object)
    """

    def __init__(self, class_or_id_name=None, header_position: int=None, 
                 base_url: str=None, processors: List=[]):
        self._table = None
        self._raw_rows = []
        self.values = []
        # self.headers = None

        self.class_or_id_name = class_or_id_name
        self.attrs = None
        self.header_position = header_position
        self.base_url = base_url
        self.processors = processors

    def __enter__(self):
        return self.get_values

    def __iter__(self):
        return iter(self.values)

    def __repr__(self):
        return f"{self.__class__.__name__}({self.values})"

    def __call__(self, soup: BeautifulSoup, **kwargs):
        """
        Resolve another table by calling the instance

        Args:
            soup (BeautifulSoup): [description]

        Returns:
            [type]: [description]
        """
        self.__init__(**kwargs)
        self.resolve(soup)
        return self

    def __getitem__(self, index):
        return self.values[index]

    def __len__(self):
        return len(self.values)

    # def __add__(self, table_instance):
    #     if not isinstance(table_instance, TableExtractor):
    #         raise TypeError("The table to add should be an instance of TableExtractor")
    #     return pandas.concat(
    #         [table_instance.get_values, self.get_values],
    #         axis=1
    #     )

    @property
    def first(self) -> Union[Tag, None]:
        return self._raw_rows[0]

    @property
    def get_values(self):
        import pandas
        
        values = self.values.copy()
        if self.header_position is not None:
            values.pop(self.header_position)
        instance = chain(*values)
        return pandas.Series(data=list(instance))

    @classmethod
    def as_instance(cls, soup, **kwargs):
        instance = cls(**kwargs)
        instance.resolve(soup)
        return instance

    @staticmethod
    def _get_rows(element: Tag):
        return element.find_all('tr')

    def _extract_values(self, elements: ResultSet, include_links: bool=False):
        # if self._raw_rows is not None:
        rows = []
        for row in elements:
            new_row = []
            for column in row:
                if column != '\n':
                    try:
                        new_row.append(deep_clean(column.text))
                    except:
                        # TODO: For whatever reasons on the
                        # table header values, colum is directly
                        # the value of the row instead of <tr>
                        # which generates an error.
                        # column = 'A' instead of <tr>A</tr>
                        # if isinstance(column, str):
                        #     new_row.append(column or None)
                        new_row.append(None)

                    # Find the first link in the column
                    # so that it can be included in the
                    # row -- This is useful in certain
                    # cases where the first row of a table
                    # sometimes has a link to go to a next
                    # page and it can be interesting to catch
                    # these kinds of links e.g. go to profile...
                    if include_links:
                        link = column.find('a')
                        if link or link is not None:
                            href = link.attrs.get('href')
                            # This is a problematic section especially when used
                            # in a Pipeline. When the link is not a link e.g. -1,
                            # this creates an error that is very difficult to resolve
                            # because the Pipe does not give the full stracktrace.
                            # Also, only append a link if something is detected.
                            if is_url(str(href)) or is_path(str(href)):
                                if self.base_url:
                                    href = urljoin(self.base_url, href)
                                link = safe_url_string(href)
                                new_row.extend([href])
                            # else:
                            #     # Sometimes, especially on badly coded websites,
                            #     # the url/path in the link comes out in a very
                            #     # odd manner e.g Players.asp?Tourn=WU202013&Team=CHN&No=133592
                            #     # which does not allow us to collect
                            #     # the url. If the user knows about this and has
                            #     # provided a root url, we can use that in an 
                            #     # attempt to reconcile the path with url
                            #     if self.base_url is not None:
                            #         url = urljoin(self.base_url, href)
                            #         if is_url(url):
                            #             link = safe_url_string(url)
                            #             new_row.extend([url])
            rows.append(new_row)
        #     if self.header_position is not None:
        #         self.headers = rows.pop(self.header_position)
        return rows
        # else:
        #     return self._raw_rows

    # def _run_processors(self, rows):
    #     if self.processors:
    #         processed_rows = []
    #         for row in rows:
    #             for processor in self.processors:
    #                 if not callable(processor):
    #                     raise TypeError(f"Processor should be a callable. Got {processor}")
    #                 row = [processor(value, index=index) for index, value in enumerate(row)]
    #             processed_rows.append(row)
    #         return processed_rows
    #     return rows

    def _run_processors(self, rows):
        new_row = []
        processed_rows = []
        if self.processors:
            for row in rows:
                for processor in self.processors:
                    if not callable(processor):
                        raise TypeError(f"Processor should be a callable. Got {processor}.")
                    
                    if not new_row:
                        new_row = processor(row)
                    else:
                        new_row = processor(new_row)

                processed_rows.append(new_row)
                new_row = []
            return processed_rows
        else:
            return rows
                    

    def get_row(self, index) -> Tag:
        try:
            return self._raw_rows[index]
        except IndexError:
            return None

    def resolve(self, soup: BeautifulSoup, include_links=False, 
                limit_to_columns: list=[]):
        # Sometimes by accident the "soup" object
        # could be None, for example when an object
        # was not found on the page.
        if soup is None:
            raise ValueError(("The BeautifulSoup object is None certainly "
            "because the table you were looking for does not exist on the HTML page. "
            "Inspect the page and ensure the object exists."))

        if self.attrs is None:
            # There might be a case where the user
            # does not pass the whole HTML page but just
            # the section that was parsed beforehand (e.g. the table HTML object)
            # directly and doing a find on that soup object
            # return None. In that case, we should just test
            # if the name equals "table" and continue from there
            if soup.name == 'table':
                self._table = soup
            else:
                self._table = soup.find('table')

            if self._table is None:
                # In case the user passes the table itself
                # as oppposed to the whole HTML page, check
                # the elements tag and assign it
                if soup.name == 'table':
                    self._table = soup
                else:
                    return self._raw_rows

        self.attrs = self._table.attrs
        if self.class_or_id_name is not None and self.attrs:
            # table_class = self.attrs.get('class', [])
            table_class = self._table.get_attribute_list('class', [])
            table_class.extend(self._table.get_attribute_list('id', []))
            
            if self.class_or_id_name not in table_class:
                self._table = self._table.find_next('table')
                if self._table is None:
                    return self._raw_rows
                self.resolve(self._table)

        # If no table, just return
        # an empty array instead of
        # raising an error or showing
        # an error
        if self._table is None:
            return self.values

        if not self._table.is_empty_element:
            # Option: 1
            tbody = self._table.find('tbody')
            if tbody is None:
                self._raw_rows = self._get_rows(self._table)
            else:
                if tbody.is_empty_element:
                    self._raw_rows = self._get_rows(self._table)
                else:
                    self._raw_rows = self._get_rows(tbody)

            extracted_values = self._extract_values(
                self._raw_rows, 
                include_links=include_links
            )
            self.values = self._run_processors(extracted_values)

            # Option: 2
            # recomposed_table = []

            # thead = self._table.find('thead')
            # raw_headers = thead.find_all('th')
            # self._raw_rows = self._get_rows(self._table.find('tbody'))

            # theader_values = self._extract_values(raw_headers)
            # tbody_values = self._extract_values(self._raw_rows, include_links=include_links)
            # recomposed_table.extend(theader_values)
            # recomposed_table.extend(tbody_values)
            
            # self.values = self._run_processors(recomposed_table)
            return self.values

    def resolve_to_dataframe(self, soup: BeautifulSoup=None, columns: list=[]):
        import pandas
        
        if soup is not None:
            self.resolve(soup)
            
        if columns:
            return pandas.DataFrame(data=self.values, columns=columns)
        return pandas.DataFrame(data=self.values)


class MultiTablesExtractor(Extractor):
    """
    Extract all the tables on a given page at once
    """

    def __init__(self, with_attrs: list = [], header_position: int = None):
        self.with_attrs = with_attrs
        self.tables_list = OrderedDict()
        self._raw_tables = None

    def __enter__(self):
        return self.tables_list

    def __iter__(self):
        return iter(self.tables_list.values())

    def __repr__(self):
        return f"{self.__class__.__name__}(count={len(self.tables_list.keys())})"

    def __getitem__(self, key):
        return self.tables_list[key]

    @staticmethod
    def _filter_tables(tables, with_attrs):
        def utility(table):
            for attr_value in table.attrs.values():
                if attr_value in with_attrs:
                    return True
                else:
                    return False
        return filter(utility, tables)

    def get_table_as_tag(self, index) -> Tag:
        return self._raw_tables[index]

    def get_table_parsed_values(self, key: int) -> List:
        return self.tables_list[key].values

    def get_table_class(self, key: int) -> TableExtractor:
        return self.tables_list[key]

    def resolve(self, soup: BeautifulSoup, include_links=False, 
                limit_to_columns=[]):
        tables = soup.find_all('table')
        self._raw_tables = tables
        if self.with_attrs:
            tables = self._filter_tables(tables, self.with_attrs)

        extractor = TableExtractor()
        for i, table in enumerate(tables):
            instance = extractor.as_instance(
                table, 
                include_links=include_links, 
                limit_to_columns=limit_to_columns
            )
            self.tables_list.update({i: instance})


class TextExtractor(Extractor):
    """
    Extract all the text from a soup object
    """

    def __init__(self):
        # For performance reasons, load the nltk library
        # during the __init__. This library takes a little
        # time to load
        from nltk.tokenize import WordPunctTokenizer

        self.tokenizer = WordPunctTokenizer()
        self.raw_text = None
        self.tokens = None

    def __iter__(self):
        return iter(self.tokens)

    def __enter__(self):
        return self.tokens

    @property
    def unique_words(self):
        return set(self.tokens)

    @cached_property
    def _stop_words(self):
        stop_words_path = os.path.join(settings.GLOBAL_ZINEB_PATH, 'extractors', 'stop_words')
        with open(stop_words_path, mode='r') as f:
            data = f.readlines()
            words = data.copy()
        new_words = []
        for word in words:
            new_words.append(word.replace('\n', ''))
        return new_words

    def resolve(self, soup: BeautifulSoup):
        text = soup.text
        self.tokens = self.tokenizer.tokenize(text)
        self.raw_text = text

    # def vectorize(self, min_df=1, max_df=1, return_matrix=False):
    #     from nltk import PunktSentenceTokenizer
    #     from sklearn.feature_extraction.text import CountVectorizer

    #     if self.raw_text is not None:
    #         tokenizer = PunktSentenceTokenizer()
    #         sentences = tokenizer.sentences_from_text(self.raw_text)

    #         vectorizer = CountVectorizer(
    #             min_df=min_df, max_df=max_df, stop_words=self._stop_words
    #         )
    #         matrix = vectorizer.fit_transform(sentences)
    #         return matrix if return_matrix else vectorizer.get_feature_names()
    #     return None


class LinkExtractor(Extractor):
    """
    Extract all the links on a given HTML page

    Parameters
    ----------

        - url_must_contain (str, optional): only get items which url contains x. Defaults to None.
        - unique (bool, optional): links must be unique accross document. Defaults to False.
        - base_url (str, optional): [description]. Defaults to None.
        - only_valid_links (bool, optional): links must be valid (start with http). Defaults to False.
    """
    def __init__(self, url_must_contain: str=None, unique: bool=False,
                 base_url: str=None, only_valid_links: bool=False):
        self.base_url = base_url
        self.unique = unique
        self.validated_links = []
        self.url_must_contain = url_must_contain
        self.only_valid_links = only_valid_links

    def __enter__(self):
        return self.validated_links

    def __call__(self, **kwargs):
        return self.__class__(**kwargs)

    def __len__(self):
        return len(self.validated_links)

    def __iter__(self):
        return iter(self.validated_links)

    def __next__(self):
        return next(self.__iter__())

    def __contains__(self, value_to_check):
        links = [str(link) for link in self.validated_links]
        return value_to_check in links

    def __add__(self, a):
        if not isinstance(a, (LinkExtractor, MultiLinkExtractor)):
            raise ValueError(f"Cannot add object of type {type(a)} to an extractor.")
        self.validated_links.extend(a)
        return self.validated_links

    def __getitem__(self, index):
        return self.validated_links[index]

    def __str__(self):
        return str(self.validated_links)

    def _document_links(self, soup):
        """
        Return all the document's links

        Returns        
        -------

            list: list of links
        """
        # from zineb.http.responses import HTMLResponse
        # if isinstance(soup, HTMLResponse):
        #     soup = soup.html_page
        soup = self._check_response(soup)
        return soup.find_all('a')

    def _link_iterator(self, soup):
        """
        Iterate on link BeautifulSoup ResultSet

        Parameters
        ----------

            - soup (type): BeautifulSoup object

        Yields
        ------

            - Generator[tuple[PageElement | Any, Any], None, None]: url and link attributes
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

    def _recompose_path(self, path: str):
        if path.startswith('/'):
            path = path.removeprefix('/')
        # urljoin does not care that the base
        # url is None. It just returns the path
        # as is. That's why we do not care here.
        return urljoin(self.base_url, path)

    def resolve(self, soup: BeautifulSoup):
        """
        Pass either a BeautifulSoup object or an HTMLResponse
        in order to extract all the links of a given page
        """
        from zineb.tags import Link
        if soup is None:
            return None

        tags = self._link_iterator(soup)
        for tag in tags:
            element, attrs = tag
            # href = attrs.get('href', None)
            # if href is not None:
            attrs['href'] = self._recompose_path(attrs['href'])
            self.validated_links.append(Link(element, attrs=attrs))

        if self.unique:
            self.validated_links = list(
                {link for link in self.validated_links}
            )

        if self.only_valid_links:
            # self.validated_links = list(
            #     filter(lambda x: x.is_valid, self.validated_links)
            # )
            self.validated_links = list(
                keep_while(lambda x: x.is_valid, self.validated_links)
            )


class MultiLinkExtractor(LinkExtractor):
    """
    Extract all links using a BeautifulSoup object
    and inluding emails as well

    Parameters
    ----------

        url_must_contain (str, optional): only get items which url contains x. Defaults to None.
        unique (bool, optional): links must be unique accross document. Defaults to False.
        base_url (str, optional): [description]. Defaults to None.
        only_valid_links (bool, optional): links must be valid (start with http). Defaults to False.
    """
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

    def _analyze_tags(self, soup):
        # Certain websites implemnent special tags
        # to prevent spamming. We have to carefully
        # analyze these tags to specifically resolve
        # their values to an email address
        for tag in self._document_links(self):
            attrs = tag.attrs
            if '' in attrs:
                data_encoded_email_value = attrs.get('data-')
                decoded_email = decode_email(data_encoded_email_value)
                self.validated_links.extend([decoded_email])
        return self.validated_links

    def resolve_emails(self, soup: BeautifulSoup):
        from nltk.tokenize import WordPunctTokenizer

        super().resolve(soup)

        text = soup.text
        tokenizer = WordPunctTokenizer()
        tokens = tokenizer.tokenize(text)

        emails_from_text = list(self._analyze_text(tokens))
        emails_from_links = list(self._analyze_links())
        return emails_from_links + emails_from_text


class ImageExtractor(Extractor):
    """
    Extracts all the images from a document

    Parameters
    ----------

        - unique (bool, Optional): if images should be unique. Defaults to False
        - as_type (str, Optional): get images only from a specific extension. Defaults to None
        - url_must_contain: (str, Optional): images with a specific url. Defaults to None
        - match_height: (int, Optional): images of a certain height
        - match_width: (int, Optional): images of a certain width
    """

    def __init__(self, unique: bool=False, as_type: str=None,
                 url_must_contain: str=None, match_height: int=None,
                 match_width: int=None):
        self.images = []
        self._cached_images = []
        self.unique = unique
        self.as_type = as_type
        self.url_must_contain = url_must_contain
        self.match_height = match_height
        self.match_width = match_width
        self.processors = []

    def __len__(self):
        return len(self.images)

    def __getitem__(self, index):
        return self.images[index] if self.images else []

    def __repr__(self):
        return f'{self.__class__.__name__}({self.images})'

    @cached_property
    def cached_items(self):
        return self._cached_images

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

    def resolve(self, soup: BeautifulSoup, processors: list=[]):
        from zineb.tags import ImageTag

        self.processors.extend(processors)

        images = self._image_iterator(soup)
        for i, image in enumerate(images):
            tag, attrs = image
            self._cached_images.append(
                ImageTag(tag, attrs=attrs, index=i, html_page=soup)
            )
        self.images = self.filter_images()
        
        # processor_result = []
        # for processor in processors:
        #     if not processor_result:
        #         processor_result = processor.get_result
        #     else:
                
        return self.images

    def filter_images(self, expression: str=None):
        images = self._cached_images.copy()

        if self.unique:
            images = list(set(images))

        if expression is not None:
            images = list(keep_while(lambda x: expression in x, images))

        if self.as_type is not None:
            images = list(keep_while(lambda x: x.endswith(self.as_type), images))

        if self.url_must_contain is not None:
            images = list(keep_while(lambda x: self.url_must_contain in x, images))

        if (self.match_height is not None 
                or self.match_width is not None):
            filtered_images = {}
            for image in images:
                height, width = (image.attrs.get('height'), image.attrs.get('width'))
                if height is not None:
                    if height == self.match_height:
                        filtered_images.add(image)
                    
                if width is not None:
                    if width == self.match_width:
                        filtered_images.add(image)
            
            images = list(filtered_images)
            
        return images


class ListExtractor(MultipleRowsMixin, Extractor):
    def __init__(self, class_or_id_name=None, processors: List=[]):
        super().__init__(class_or_id_name=class_or_id_name, processors=processors)
        self.class_or_id_name = class_or_id_name

    def resolve(self, soup):
        attrs = {}
        # list_items = []
        if self.class_or_id_name is not None:
            attrs['class'] = self.class_or_id_name

        soup = self._check_response(soup)

        tags = soup.find_all('ul', attrs=attrs)
        for tag in tags:
            items = tag.find_all('li')
            for index, item in enumerate(items):
                link = item.find('a')
                if link is not None:
                    link = link.attrs['href']
                self._rows.append([index, deep_clean(item.text), link])
        return self._run_processors(self._compose())
