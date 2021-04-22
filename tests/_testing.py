from zineb.extractors.base import TableExtractor
from zineb.tests import file_opener

def delete_blank(value, **kwargs):
    if value == '':
        return None
    return value


soup = file_opener('tests/html/tables3.html')

extractor = TableExtractor(class_or_id_name='third-table')
extractor.resolve(soup, include_links=True)
print(extractor.values)
