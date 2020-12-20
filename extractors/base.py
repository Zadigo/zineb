from functools import cached_property
from zineb.utils.html import deep_clean


class Extractor:
    def __enter__(self):
        raise NotImplementedError('Should be implemented by the subclasses')
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        return NotImplementedError('Should be implemented by the subclasses')

    def resolve(self, soup):
        raise NotImplementedError(('Provide functionnalities for quickly '
        'extracting items from the HTML page'))


class RowExtractor(Extractor):
    """
    Quickly extract a table from an HTML page. By default,
    this class retrieves the first table of the page

    Parameters
    ----------

        class_name (str): the class name of the table
    """

    def __init__(self, class_name=None, has_headers=False):
        self.table = None
        self.rows = None
        self.headers = None

        self.class_name = class_name
        self.attrs = None
        self.has_headers = has_headers

    def __iter__(self):
        return iter(self.rows)

    @cached_property
    def _compose(self):
        if self.rows is not None:
            rows = []
            for row in self.rows:
                new_row = []
                for column in row:
                    if column != '\n':
                        new_row.append(deep_clean(column.text))
                rows.append(new_row)
            if self.has_headers:
                self.headers = rows.pop(0)
            return rows
        else:
            return self.rows

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

    def resolve(self, soup):
        if self.attrs is None:
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
            return self._compose
