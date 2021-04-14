import re
import secrets
from collections import OrderedDict
from typing import Any

import pandas
from bs4 import BeautifulSoup
from bs4.element import ResultSet, Tag
from pydispatch import dispatcher
from zineb.exceptions import FieldError, ParserError
from zineb.http.responses import HTMLResponse
from zineb.models.fields import Field
from zineb.signals import signal


class FieldDescripor:
    cached_fields = OrderedDict()
    
    def __getitem__(self, key) -> Field:
        return self.cached_fields[key]

    def field_names(self):
        return self.cached_fields.keys()


class ModelOptions:
    def __init__(self, options):
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

    def __getitem__(self, name):
        return self.cached_options[name]

    def get_option_by_name(self, name):
        return self.cached_options.get(name)

    def has_option(self, name):
        return name in self.cached_options


class Base(type):
    def __new__(cls, name, bases, attrs):
        super_new = super().__new__
        parents = [b for b in bases if isinstance(b, Base)]

        if not parents:
            return super_new(cls, name, bases, attrs)

        if name != 'Model':
            # Normally, we should have all the fields
            # anad/or remaining methods of the class
            declared_fields = []
            for key, value in attrs.items():
                if isinstance(value, Field):
                    declared_fields.append((key, value))

            descriptor = FieldDescripor()
            descriptor.cached_fields = OrderedDict(declared_fields)
            # descriptor.cached_fields.update(**attrs)
            # new_attrs.update(
            #     {
            #         '_meta': descriptor, 
            #         '__module__': class_module, 
            #         '__qualname__': class_qualname
            #     }
            # )
            # new_class = super_new(cls, name, bases, new_attrs)
            # setattr(new_class, '_fields', fields)

            meta = None
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
                    raise ValueError(f"Meta received an illegal options: {', '.join(non_authorized_options)}")
                meta = ModelOptions(options=options)
            else:
                meta = ModelOptions(options=[])

            new_class = super_new(cls, name, bases, attrs)
            setattr(new_class, '_fields', descriptor)
            setattr(new_class, '_meta', meta)
            return new_class

        return super_new(cls, name, bases, attrs)


class Registry:
    def _create_base_dict(self):
        base = {}
        for field in self._fields:
            base.setdefault(field)
        return base


class DataStructure(metaclass=Base):
    def __init__(self, html_document: BeautifulSoup=None, 
                 html_tag: Tag=None, response: HTMLResponse=None):
        self._cached_result = {}
        self.html_document = html_document
        self.html_tag = html_tag
        self.response = response
        self.parser = self._choose_parser()

    @staticmethod
    def _expression_resolver(expression):
        try:
            tag_name, pseudo = expression.split('__', 1)
        except:
            # If no pseudo is passed, just use the default
            # text one by appending it to the expression
            expression = expression + '__text'
            tag_name, pseudo = expression.split('__', 1)

        matched_elements = re.search(r'(?P<tag>\w+)(?P<marker>\.|\#)?(?P<attr>\w+)?', tag_name)
        named_elements = matched_elements.groupdict()

        attrs = {}
        markers = {'.': 'class', '#': 'id'}
        marker = named_elements.get('marker', None)
        if marker is not None:
            try:
                named_marker = markers[marker]
            except:
                raise KeyError('Marker is not a recognized marker')
            else:
                attrs.update({named_marker: named_elements.get('attr')})
        return named_elements.get('tag'), pseudo, attrs

    def _resolve_pseudo(self, pseudo, tag):
        allowed_pseudos = ['text', 'href', 'src']
        if pseudo not in allowed_pseudos:
            raise ValueError('Pseudo is not an authorized pseudo')

        if pseudo == 'text':
            return getattr(tag, 'text')
        else:
            return tag.attrs.get(pseudo)

    def _get_field_by_name(self, name) -> Field:
        """
        Gets the cached field object that was registered
        on the model

        Parameters
        ----------

            name (str): the field name to get

        Raises
        ------

            KeyError: When the field is absent

        Returns
        -------

            type: returns zineb.fields.Field object
        """
        try:
            return self._fields.cached_fields[name]
        except:
            raise FieldError(name, self._fields.field_names())

    def _choose_parser(self):
        # In case we get both the HTML document
        # and a tag, use the most global element
        # in order to have better results
        if self.html_document and self.html_tag:
            return self.html_document

        if self.html_tag is not None:
            return self.html_tag

        if self.html_document is not None:
            return self.html_document

        if self.response is not None:
            if not isinstance(self.response, HTMLResponse):
                raise TypeError('The request object should be a zineb.response.HTMLResponse object')
            return self.response.html_page

    def add_expression(self, name, expression, many=False):
        """
        Adds a value to your Model object using an expression

        Parameters
        ----------

                field_name (str): the name of field on which to add a given value
                expression (str): an expression used to query or parse tags in the document
        """
        obj = self._get_field_by_name(name)

        tag_name, pseudo, attrs = self._expression_resolver(expression)

        if self.parser is None:
            raise ParserError()

        if many:
            tags = self.parser.find_all(tag_name, attrs=attrs)
            results = [self._resolve_pseudo(pseudo, tag) for tag in tags]
        else:
            tag = self.parser.find(tag_name, attrs=attrs)
            results = [self._resolve_pseudo(pseudo, tag)]

        cached_field = self._cached_result.get(name, None)
        if cached_field is None:
            self._cached_result.setdefault(name, [])
            cached_field = self._cached_result.get(name)
        
        def _field_resolution(x):
            obj.resolve(x)
            return obj._cached_result

        if len(results) > 1:
            results = map(lambda x: _field_resolution(x), results)
        else:
            obj.resolve(results[0])
            results = [obj._cached_result]
        cached_field.extend(results)
        self._cached_result.update({name: cached_field})

    def add_value(self, name: str, value: Any):
        """
        Adds a value to your Model object. This definition does not
        require a BeautifulSoup object

        Parameters
        ----------

                field_name (str): the name of field on which to add a given value
                value (str): the value to add to the model
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

    def resolve_fields(self):
        """
        Translate the data to a pandas DataFrame
        """
        df = pandas.DataFrame(
            self._cached_result, 
            columns=self._fields.field_names(),
        )

        if self._meta.has_option('ordering'):
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
            custom_modem.resolve_fields()

            -> pandas.DataFrame
    """
    def __str__(self) -> str:
        return str(self._cached_result)
        
    def __repr__(self):
        return f"{self.__class__.__name__}"

    def __getitem__(self, field):
        return self._cached_result.get(field, None)

    def __setitem__(self, field, value):
        self.add_value(field, value)

    # def clean(self, dataframe: pandas.DataFrame, **kwargs):
    #     """
    #     Put all additional functionnalities that you wish to
    #     run on the DataFrame here before calling the save
    #     function on your model.

    #     Parameters
    #     ----------

    #         dataframe (pandas.DataFrame): [description]
    #     """
    #     pass
        
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
        df = self.resolve_fields()

        # self.clean(dataframe=df)

        if commit:
            if filename is None:
                filename = f'{secrets.token_hex(nbytes=5)}.json'
            else:
                if not filename.endswith('json'):
                    filename = f'{filename}.json'

            signal.send(dispatcher.Any, self, tag='Post.Save')
            return df.to_json(filename, orient='records')
        return df.copy()    
