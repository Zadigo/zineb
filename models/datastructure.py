import re
import secrets
from collections import OrderedDict
from typing import Any, List, Union

import pandas
from bs4 import BeautifulSoup
from bs4.element import ResultSet, Tag
from pydispatch import dispatcher
from zineb.exceptions import FieldError, ParserError
from zineb.http.responses import HTMLResponse
from zineb.models.fields import Field
from zineb.signals import signal


class ModelRegistry:
    """
    This class is a convienience class that remembers
    the models that were created and in which order.
    """
    counter = 0
    registry = OrderedDict()

    def __getitem__(self, name: str):
        return self.registry[name]

    def __iter__(self):
        return iter(self.models)

    @property
    def models(self):
        return list(self.registry.values())

    def add(self, name: str, model: type):
        self.counter = self.counter + 1
        return self.registry.setdefault(name, model)

    def get_model(self, name: str):
        return self.registry[name]()

    def has_model(self, name: str):
        return name in self.registry


class FieldDescriptor:
    cached_fields = OrderedDict()
    
    def __getitem__(self, key) -> Field:
        return self.cached_fields[key]

    def field_names(self):
        return self.cached_fields.keys()


class ModelOptions:
    def __init__(self, options: Union[List[tuple[str]], dict]):
        self.cached_options = OrderedDict(options)

        self.ordering_field_names = set()
        self.ascending_fields = []
        self.descending_fields = []
        self.ordering_booleans = []
        
        if self.has_option('ordering'):
            ordering = self.get_option_by_name('ordering')
            self.ordering_field_names = list({
                field.removeprefix('-') for field in ordering
            })
            self.ascending_fields = [
                field for field in ordering 
                    if not field.startswith('-')
            ]
            self.descending_fields = [
                field for field in ordering 
                    if field.startswith('-')
            ]

            def convert_to_boolean(value):
                if value.startswith('-'):
                    return False
                return True
            self.ordering_booleans = list(map(convert_to_boolean, ordering))

    def __call__(self, options):
        self.__init__(options)
        return self

    def __getitem__(self, name):
        return self.cached_options[name]

    def get_option_by_name(self, name):
        return self.cached_options.get(name)

    def has_option(self, name):
        return name in self.cached_options


class Base(type):
    model_registry = ModelRegistry()

    def __new__(cls, name, bases, attrs):
        super_new = super().__new__
        parents = [b for b in bases if isinstance(b, Base)]

        if not parents:
            return super_new(cls, name, bases, attrs)

        if name != 'Model':
            # Normally, we should have all the fields
            # and/or remaining methods of the class
            declared_fields = []
            for key, value in attrs.items():
                if isinstance(value, Field):
                    declared_fields.append((key, value))

            descriptor = FieldDescriptor()
            descriptor.cached_fields = OrderedDict(declared_fields)

            meta = ModelOptions([])
            if 'Meta' in attrs:
                meta_dict = attrs.pop('Meta').__dict__
                authorized_options = ['ordering']
                non_authorized_options = []

                def check_option(item):
                    key, _ = item
                    if key.startswith('__'):
                        return False
                    if key in authorized_options:
                        return True
                    non_authorized_options.append(key)
                    return False

                options = list(filter(check_option, meta_dict.items()))
                if non_authorized_options:
                    raise ValueError("Meta received an illegal "
                    f"option. Valid options are: {', '.join(non_authorized_options)}")
                meta = meta(options)

            new_class = super_new(cls, name, bases, attrs)
            setattr(new_class, '_fields', descriptor)
            setattr(new_class, '_meta', meta)

            cls.model_registry.add(name, new_class)
            return new_class

        return super_new(cls, name, bases, attrs)


class DataStructure(metaclass=Base):
    def __init__(self, html_document: BeautifulSoup=None, 
                 response: HTMLResponse=None):
        self._cached_result = {}

        self.html_document = html_document
        self.response = response

        self.parser = self._choose_parser()

    def _get_field_by_name(self, name) -> Field:
        """
        Gets the cached field object that was registered
        on the model

        Parameters
        ----------

            - name (str): the field name to get

        Raises
        ------

            KeyError: When the field is absent

        Returns
        -------

            Field: returns zineb.fields.Field object
        """
        try:
            return self._fields.cached_fields[name]
        except:
            raise FieldError(name, self._fields.field_names())

    def _choose_parser(self):
        if self.html_document is not None:
            return self.html_document

        if self.response is not None:
            if not isinstance(self.response, HTMLResponse):
                raise TypeError(('The request object should be a '
                'zineb.response.HTMLResponse object.'))
            return self.response.html_page

    def add_using_expression(self, name: str, tag: str, attrs: dict):
        """
        Adds a value to your Model object using an expression. Using this
        method requires that you pass and BeautifulSoup object to your model.

        Parameters
        ----------

                - name (str): the name of field on which to add a given value
                - tag (str): a tag to get on the HTML document
                - attrs (dict): attributes related to the element's tag on the page
        """
        obj = self._get_field_by_name(name)
        tag_value = self.parser.find(name=tag, attrs=attrs)
        obj.resolve(tag_value.string)
        resolved_value = obj._cached_result

        cached_field = self._cached_result.get(name, None)
        if cached_field is None:
            self._cached_result.setdefault(name, [])
            cached_field = self._cached_result.get(name)
        cached_field.append(resolved_value)
        self._cached_result.update({name: cached_field})

    def add_value(self, name: str, value: Any):
        """
        Adds a value to your Model object.

        Parameters
        ----------

            - field_name (str): the name of field on which to add a given value
            - value (str): the value to add to the model
        """
        obj = self._get_field_by_name(name)
        obj.resolve(value)
        resolved_value = obj._cached_result

        if obj.name == 'date':
            # Some fields such as the DateField does not
            # store a string but a function. For example,
            # in this case, a datetime.datetime object is
            # stored. In that case, we have to resolve to
            # the true value of the field. Otherwise the
            # user might get something unexpected
            resolved_value = str(obj._cached_result.date())
        
        cached_field = self._cached_result.get(name, None)            
        if cached_field is None:
            self._cached_result.setdefault(name, [])
            cached_field = self._cached_result.get(name)
        cached_field.append(resolved_value)
        # ?? To prevent unbalanced columns for example
        # when the user adds a value to field but not
        # to another, maybe add a None value to the
        # rest of the fields so that the len always
        # stays equals between columns
        # for field in self._fields.field_names():
        #     if field not in self._cached_result:
        #         self._cached_result.setdefault(field, [])
        #         self._cached_result[field].extend([None])
        #     else:
        #         self._cached_result[field].extend([None])
        self._cached_result.update({name: cached_field})

    def add_expression(self, **expressions):
        """
        Add multiple values to your model using a
        set of expressions.
        """
        pass

    def resolve_fields(self):
        """
        Implement the data into a Pandas
        Dataframe
        """
        df = pandas.DataFrame(
            self._cached_result, 
            columns=self._fields.field_names(),
        )

        if self._meta.has_option('ordering'):
            # if self._meta.ordering_field_names and not self._meta.ordering_booleans:
            #     number_of_fields = len(self._meta.ordering_field_names):
            #     self._meta.ordering_booleans = [True for _ in range(0, number_of_fields)]
            df = df.sort_values(
                by=self._meta.ordering_field_names,
                ascending=self._meta.ordering_booleans
            )
        return df


class Model(DataStructure):
    """
    A Model is a class that helps you structure
    your scrapped data efficiently for later use

    Your custom models have to inherit from this
    base Model class and implement a set of fields
    from zineb.models.fields. For example:

            class MyCustomModel(Model):
                name = CharField()

    Once you've created the model, you can then use
    it within your project like so:

            custom_model = MyCustommodel()
            custom_model.add_value('name', 'p')
            custom_model.resolve_fields()

            -> pandas.DataFrame
    """
    _cached_dataframe = None

    def __str__(self) -> str:
        return str(self._cached_result)
        
    def __repr__(self):
        return f"{self.__class__.__name__}"

    def __getitem__(self, field):
        return self._cached_result.get(field, None)

    def __setitem__(self, field, value):
        self.add_value(field, value)

    def clean(self, dataframe: pandas.DataFrame, **kwargs):
        """
        Put all additional functionnalities that you wish to
        run on the DataFrame here before calling the save
        function on your model.

        Parameters
        ----------

            dataframe (pandas.DataFrame): [description]
        """
        self._cached_dataframe = dataframe
        
    def save(self, commit=True, filename=None, **kwargs):
        """
        Save the model's dataframe to a file.

        By setting commit to False, you will get a copy of the
        dataframe in order to run additional actions on it

        Parameters
        ----------

            commit (bool, optional): save immediately. Defaults to True.
            filename (str, optional): the file name to use. Defaults to None.

        Returns
        -------

            dataframe: pandas dataframe object
        """
        signal.send(dispatcher.Any, self, tag='Pre.Save')
        dataframe = self.resolve_fields()

        self.clean(dataframe=dataframe)

        if commit:
            if filename is None:
                filename = f'{secrets.token_hex(nbytes=5)}.json'
            else:
                if not filename.endswith('json'):
                    filename = f'{filename}.json'

            signal.send(dispatcher.Any, self, tag='Post.Save')
            return self._cached_dataframe.to_json(filename, orient='records')
        return self._cached_dataframe.copy()    
