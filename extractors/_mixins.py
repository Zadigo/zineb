from typing import List


class MultipleRowsMixin:
    def __init__(self, class_or_id_name=None, processors: List = []):
        self._rows = []

        self.class_or_id_name = class_or_id_name
        self.attrs = dict()
        
        if not isinstance(processors, list):
            raise TypeError('Processors should be a list of processors')
        self.processors = processors

    def __iter__(self):
        return iter(self._rows)

    def __repr__(self):
        return f"<{self.__class__.__name__}>"

    def _compose(self):
        return self._rows

    def _run_processors(self, rows):
        processed_rows = []
        for row in rows:
            for processor in self.processors:
                if not callable(processor):
                    raise TypeError(
                        f"Processor should be a callable. Got {processor}")
                row = [processor(value, row=row) for value in row]
            processed_rows.append(row)
        return rows or processed_rows
