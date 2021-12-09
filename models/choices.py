from collections.abc import Mapping
from zineb.utils.iteration import keep_while
from zineb.utils.formatting import LazyFormat

class ChoicesMapping(Mapping):
    choices = set()
    labels = set()
    
    def __str__(self):
        return str(self.choices)

    def __getitem__(self, name):
        possibilities = filter(lambda x: name in x, self.choices)
        if not possibilities:
            raise ValueError('')
        return list(possibilities)

    def __setitem__(self, name, value):
        if not name.isupper():
            return False

        if name in self.choices:
            return False

        # On the Choices model, users
        # can mistakenly put a comma
        # after the attribute e.g. "NAME,"
        # and in that case Python directly
        # interpretes that as a tuple
        if isinstance(value, tuple):
            value = list(value)[-1]

        self.choices.add((name, value))
        self.labels.add(name)

    def __iter__(self):
        return [item[0] for item in self.choices]

    def __len__(self):
        return len(self.choices)

    def __contains__(self, value):
        return value in self.labels


class ChoicesMeta(type):
    def __new__(cls, name, bases, attrs):
        new_class = super().__new__
        mapping = ChoicesMapping()
        for key, value in attrs.items():
            if key.isupper() and not key.startswith('__'):
                mapping[key] = value
        attrs['_choices'] = mapping
        return new_class(cls, name, bases, attrs)


class BaseChoices(metaclass=ChoicesMeta):        
    def __str__(self):
        return str(self._choices)

    def __contains__(self, value):
        return value in self._choices

    def __getattr__(self, name):
        return getattr(self._choices, name)

    @property
    def labels(self):
        return self._choices.labels
    
    @property
    def choices(self):
        return self._choices.choices
    
    def convert(self, value: str):
        if not isinstance(value, str):
            pass
        candidates = list(keep_while(lambda x: value in x, self.choices))
        if len(candidates) == 0:
            raise 


class Choices(BaseChoices):
    """Create a list of choices that can be used
    to convert an item fom the internet to a choice
    on the class"""
    