from collections.abc import Mapping


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

    def __iter__(cls):
        return (item for item in cls)

class BaseChoices(metaclass=ChoicesMeta):        
    def __str__(self):
        return str(self._choices)

    def __contains__(self, value):
        return value in self._choices

    def __getattr__(self, name):
        return getattr(self._choices, name)

    # @property
    # def labels(self):
    #     return self._choices.labels
    
    # @property
    # def choices(self):
    #     return self._choices.choices


class Choices(BaseChoices):
    def __str__(self):
        return str(self._choices.choices)





class MyChoices(Choices):
    NAME = 'Name'
    SURNAME = 'Surname'
    AGE = 'Age'


print('Name' in MyChoices)
