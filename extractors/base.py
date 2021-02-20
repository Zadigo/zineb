import os
import re
from functools import cached_property

import pandas
from nltk.tokenize import PunktSentenceTokenizer, WordPunctTokenizer
from sklearn.feature_extraction.text import CountVectorizer
from w3lib.html import safe_url_string
from w3lib.url import is_url
from zineb.settings import settings
from zineb.utils._html import deep_clean, is_path


class Extractor:
    """
    Base class for every extractor class
    """
    def __enter__(self):
        raise NotImplementedError('Should be implemented by the subclasses')
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        return False

    def resolve(self, soup):
        raise NotImplementedError(('Provide functionnalities for quickly '
        'extracting items from the HTML page'))


class TableRows(Extractor):
    """
    Quickly extract a table from an HTML page.
    
    By default this class retrieves the first table of the page

    Parameters
    ----------

        class_name (str, Optionnal): the class name of the table. Defaults to None
        has_headrs (bool, Optionnal): indicates if the table has headers. Defaults to False
        processors (func, Optionnal): list of functions to process the final result. Defaults to None

    
        Example
        -------

            extractor = RowExtractor()
            extractor.resolve(BeautifulSoup Object)

                -> [[a, b, c], [d, ...]]

            By indicating if the table has a header, the heder values will be dropped
            from the final result

            Finally, you can also pass a set of processors that will modifiy the values
            of each rows according to the logic of said processor:

            def drop_empty_values(value):
                if value != '':
                    return value

            extractor = RowExtractor(processors=[drop_empty_values])
            extractor.resolve(BeautifulSoup Object)
    """

    def __init__(self, class_name=None, has_headers=False, processors:list=None):
        self.table = None
        self.rows = None
        self.headers = None

        self.class_name = class_name
        self.attrs = None
        self.has_headers = has_headers
        self.processors = processors

    def __iter__(self):
        return iter(self.rows)

    def __repr__(self):
        return f"<{self.__class__.__name__}>"

    def __add__(self, b):
        return 

    # @cached_property
    def _compose(self, include_links=False):
        if self.rows is not None:
            rows = []
            for row in self.rows:
                new_row = []
                for column in row:
                    if column != '\n':
                        new_row.append(deep_clean(column.text))

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
                                    link = safe_url_string(href)
                                    new_row.extend([href])
                rows.append(new_row)
            if self.has_headers:
                self.headers = rows.pop(0)
            return rows
        else:
            return self.rows

    def _run_processors(self, rows):
        if self.processors:
            processed_rows = []
            for row in rows:
                for processor in self.processors:
                    if not callable(processor):
                        raise TypeError('Processor should be a callable')
                    row = [processor(value, row=row) for value in row]
                processed_rows.append(row)
            return processed_rows
        return rows

    @property
    def first(self):
        return self.rows[0]

    def _get_rows(self, element):
        return element.find_all('tr')

    def get_row(self, index):
        try:
            return self.rows[index]
        except IndexError:
            return None

    def resolve(self, soup, include_links=False, limit_to_columns :list=[]):
        if self.attrs is None:
            # There might be a case where the user
            # does not pass the whole HTML page but just
            # the section that was parsed beforehand (e.g. the table HTML object)
            # directly and doing a find on that soup object
            # return None. In that case, we should just test
            # if the name equals "table" and continue from there
            if soup.name == 'table':
                self.table = soup
            else:
                self.table = soup.find('table')

            if self.table is None:
                # In case the user passes the table itself
                # as oppposed to the whole HTML page, check
                # the elements tag and assign it
                if soup.name == 'table':
                    self.table = soup
                else:
                    return self.rows

        self.attrs = self.table.attrs
        if self.class_name is not None and self.attrs:
            table_class = self.attrs.get('class', [])
            if self.class_name not in table_class:
                self.table = self.table.find_next('table')
                if self.table is None:
                    return self.rows
                self.resolve(self.table)

        if not self.table.is_empty_element:
            tbody = self.table.find('tbody')
            if tbody is None:
                self.rows = self._get_rows(self.table)
            else:
                if tbody.is_empty_element:
                    self.rows = self._get_rows(self.table)
                else:
                    self.rows = self._get_rows(tbody)
            
            return self._run_processors(self._compose(include_links=include_links))

    def resolve_to_dataframe(self, columns: dict={}):
        df = pandas.DataFrame(data=self._compose())
        if columns:
            return df.rename(columns=columns)
        return df


class Text(Extractor):
    """
    Extract all the text from a soup object
    """
    tokenizer = WordPunctTokenizer()

    def __init__(self):
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
        stop_words_path = os.path.join(settings.PROJECT_PATH, 'extractors', 'stop_words')
        with open(stop_words_path, mode='r') as f:
            data = f.readlines()
            words = data.copy()
        new_words = []
        for word in words:
            new_words.append(word.replace('\n', ''))
        return new_words

    def resolve(self, soup):
        text = soup.text
        self.tokens = self.tokenizer.tokenize(text)
        self.raw_text = text

    def vectorize(self, min_df=1, max_df=1, return_matrix=False):
        if self.raw_text is not None:
            tokenizer = PunktSentenceTokenizer()
            sentences = tokenizer.sentences_from_text(self.raw_text)

            vectorizer = CountVectorizer(
                min_df=min_df, max_df=max_df, stop_words=self._stop_words
            )
            matrix = vectorizer.fit_transform(sentences)
            return matrix if return_matrix else vectorizer.get_feature_names()
        return None
