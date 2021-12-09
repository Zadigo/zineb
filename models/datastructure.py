import copy
import os
import secrets
from collections import OrderedDict, defaultdict
from functools import cached_property, lru_cache
from typing import Any, Callable, List, Union

from bs4 import BeautifulSoup
# from pydispatch import dispatcher
from zineb.exceptions import FieldError, ModelExistsError
from zineb.http.responses import HTMLResponse
from zineb.models.fields import Empty, Field
from zineb.models.functions import (Add, Divide, ExtractDay, ExtractMonth,
                                    ExtractYear, Math, Multiply, Substract,
                                    When)
from zineb.settings import settings
from zineb.utils._datastructures import SmartDict
from zineb.utils.formatting import LazyFormat


class ModelRegistry:
    """
    This class is a convienience container that remembers
    the models that were created and the order in which
    they were
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
        if self.has_model(name):
            raise ModelExistsError(name)

        self.counter = self.counter + 1
        return self.registry.setdefault(name, model)

    def get_model(self, name: str):
        return self.registry[name]()

    def has_model(self, name: str):
        return name in self.registry

model_registry = ModelRegistry()


class FieldMixin:
    parents = []
    # forward_fields_map = {}
    cached_fields = OrderedDict()
    
    @cached_property
    def field_names(self):
        return list(self.cached_fields.keys())

    @cached_property
    def fields_map(self):
        pass
    
    @cached_property
    def true_fields(self):
        return list(self.cached_fields.values())

    def get_field(self, name) -> Field:
        try:
            return self.cached_fields[name]
        except:
            raise FieldError(name, self.field_names)

    def has_fields(self, *names, raise_exception=False):
        result = all(map(lambda x: x in self.field_names, names))
        if raise_exception and not result:
            # FIXME: Should implement the field names that are
            # really missing as opposed to the names provided
            raise FieldError(LazyFormat('Field does not exist: '
            '{fields}', fields=', '.join(names)))
        return result


class ModelOptions(FieldMixin):
    """
    A container that stores the options
    of a given model including both the 
    fields and the Meta options
    """
    authorized_options = ['ordering', 'label', 'template_model']

    def __init__(self, options: Union[List[tuple[str]], dict]):
        self.model_name = None
        self.cached_options = OrderedDict(options)

        self.ordering_field_names = set()
        self.ascending_fields = []
        self.descending_fields = []
        self.ordering_booleans = []
        
        if self.has_option('ordering'):
            ordering = self.get_option_by_name('ordering')
            for field in ordering:
                self.ordering_field_names.add(field.removeprefix('-'))
            self.ascending_fields = [
                field for field in ordering 
                    if not field.startswith('-')
            ]
            self.descending_fields = [
                field for field in ordering 
                    if field.startswith('-')
            ]

            # Convert each ordering field on the
            # model to Booleans. This is what a
            # DataFrame accepts in order to sort
            # a particular column
            def convert_to_boolean(value):
                if value.startswith('-'):
                    return False
                return True
            self.ordering_booleans = list(map(convert_to_boolean, ordering))

    def __call__(self, options):
        # old_options = copy.deepcopy(self.cached_options)
        self.__init__(options)
        # self.cached_options = old_options | self.cached_options
        return self

    def __getitem__(self, name):
        return self.cached_options[name]

    def __repr__(self):
        return f"{self.__class__.__name__}(model={self.model_name})"

    def __getattr__(self, name):
        if name in self.field_names:
            try:
                return self.forward_field_map[name]
            except:
                raise ValueError('Forward relationship does not exist')
        raise AttributeError(LazyFormat('{klass} object has no attribute {attr}', 
        klass=self.__class__.__name__, attr=name))

    @property
    def is_template_model(self):
        # If the model is a template model,
        # it means that it can only serve to
        # add additional fields to a child model.
        # In that sense, we shouldn't be able to
        # add values to it or even save.
        return self.cached_options.get('template_model', False)

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

        declared_fields = set()
        for key, field_obj in attrs.items():
            if isinstance(field_obj, Field):
                field_obj._bind(key)
                declared_fields.add((key, field_obj))

        default_options = [
            ('label', f"models.base.{name}")
        ]
        meta = ModelOptions(default_options)

        # If the model is subclassed, resolve the MRO
        # to get all the fields from the superclass
        # [...] also maybe create direct relationship
        # with the parent model via a ForeignKey
        for parent in bases:
            if hasattr(parent, '_meta'):
                fields = getattr(getattr(parent, '_meta'), 'cached_fields', {})
                for key, field_obj in fields.items():
                    # If the field is registered twice (on the
                    # superclass and on the subclass), use the
                    # subclass version of the field
                    if field_obj not in declared_fields:
                        declared_fields.add((key, field_obj))
                    # Create the map that will allow us to register
                    # and use ForeignKey type fields in forward and
                    # backward relationships
                    # meta.forward_fields_map.update({key: field_obj})
                meta.parents.append(parent)

        meta.model_name = name
        if declared_fields:
            meta.cached_fields = OrderedDict(declared_fields)

        if 'Meta' in attrs:
            meta_dict = attrs.pop('Meta').__dict__
            non_authorized_options = []

            def check_option(item):
                key, _ = item
                if key.startswith('__'):
                    return False

                if key in meta.authorized_options:
                    return True
                
                non_authorized_options.append(key)
                return False

            options = list(filter(check_option, meta_dict.items()))
            if non_authorized_options:
                raise ValueError("Meta received an illegal "
                f"option. Valid options are: {', '.join(meta.authorized_options)}")
            default_options.extend(options)
            meta = meta(default_options)
            
        attrs['_meta'] = meta
        
        new_class = super_new(cls, name, bases, attrs)

        if declared_fields:
            # is_template_model = False
            # if meta.has_option('template_model'):
            #     is_template_model = meta.get_option_by_name('template_model')
            # # The parent model is just a template,
            # # we'll not create any ForeignKey
            # # relationship to the parent
            # if not is_template_model:
            #     relationships = [
            #         (f"{parent}_rel", ForeignKey(new_class, parent)) 
            #             for parent in new_class._meta.parents
            #     ]
            #     meta.cached_fields.update(relationship for relationship in relationships)

            # That's where is explicitely register
            # models that have declared fields and
            # that are actually user created models -;
            # this might seem odd to implement this block
            # but it allows us to do additional things on
            # on the new model and its meta
            model_registry.add(name, new_class)
            return new_class

        return new_class


class DataStructure(metaclass=Base):
    def __init__(self, html_document: BeautifulSoup=None, response: HTMLResponse=None):
        self._cached_result = SmartDict.new_instance(*self._meta.field_names)

        self.html_document = html_document
        self.response = response

        self.parser = self._choose_parser()

    def _get_field_by_name(self, field_name) -> Field:
        """
        Gets the cached field object that was registered
        on the model via the FieldDescriptor

        Parameters
        ----------

            - field_name (str): the field name to get
        """
        return self._meta.get_field(field_name)

    def _choose_parser(self):
        if self.html_document is not None:
            return self.html_document

        if self.response is not None:
            if not isinstance(self.response, HTMLResponse):
                raise TypeError(('The request object should be a '
                'zineb.response.HTMLResponse object.'))
            return self.response.html_page

    def _add_without_field_resolution(self, field_name: str, value:Any):
        """
        When the value of a field has already been
        resolved, just add it to the model. This is
        an internal function used for the purpose of
        other internal functions since there is no
        field resolution and raw data from the internet
        would be added as is
        """
        cached_values = self._cached_result.get_container(field_name)
        cached_values.append(value)
        self._cached_result.update(field_name, cached_values)

    def add_calculated_value(self, name: str, value: Any, *funcs):
        funcs = list(funcs)

        # TODO: Quick fix because the funcs is an optional
        # parameter and if ignored this raises an IndexError.
        # Maybe we should create a Case-function to wrap the
        # functions and force funcs as a required parameter
        if not funcs:
            raise ValueError("There were no functions to use.")

        for func in funcs:
            if not isinstance(func, (Add, Substract, Divide, Multiply)):
                raise TypeError('Function should be '
                'an instance of Calculate')

            setattr(func, 'model', self)
            setattr(func, 'field_name', name)

        if len(funcs) == 1:
            func._cached_data = value
            func.resolve()
            self.add_value(func.field_name, func._cached_data)
        else:
            for i in range(len(funcs)):
                if i == 0:
                    funcs[0]._cached_data = value
                else:
                    # When there a multiple functions, the
                    # _cached_data of the current function
                    # should be the _caclulat_result of the
                    # previous one. This technique allows
                    # us to run multiple expressions on
                    # one single value
                    funcs[i]._cached_data = funcs[i - 1]._cached_data
                funcs[i].resolve()
            # Once everything has been calculated,
            # use the data of the last function to
            # add the given value to the model
            self.add_value(funcs[-1].field_name, funcs[-1]._cached_data)

    def add_case(self, value: Any, case: Callable):
        """
        Add a value to the model based on a specific
        conditions determined by a When-function.

        Parameters
        ----------

            - value (Any): the value to test
            - case (Callable): When-function
        """
        if not isinstance(case, When):
            raise TypeError('Case should be a When class.')

        case._cached_data = value
        case.model = self
        field_name, value = case.resolve()
        self.add_value(field_name, value)

    def add_using_expression(self, name: str, tag: str, attrs: dict={}):
        """
        Adds a value to your Model object using an expression. Using this
        method requires that you pass and BeautifulSoup object to your model.

        Parameters
        ----------

            - name (str): the name of field on which to add a given value
            - tag (str): a tag to get on the HTML document
            - attrs (dict, Optional): attributes related to the element's tag on the page. Defaults to {}
        """
        obj = self._get_field_by_name(name)
        if self.parser is None:
            raise ValueError(('No valid parser could be used. '
            'Make sure you pass a BeautifulSoup '
            'or an HTTPResponse object to your model '
            'in order to resolve the expression.'))

        tag_value = self.parser.find(name=tag, attrs=attrs)
        obj.resolve(tag_value.string)
        resolved_value = obj._cached_result
        self._cached_result.update(name, resolved_value)

    def add_values(self, **attrs):
        """
        Add a single row at once on your model
        using either a dictionnary or keyword
        arguments

        Example
        -------

            add_values(name=Kendall, age=22)
        """
        self._fields.has_fields(list(attrs.keys()), raise_exception=True)
        self._cached_result.update_multiple(**attrs)

    def add_value(self, name: str, value: Any):
        """
        Adds a value to your Model object.

        Parameters
        ----------

            - name (str): the name of field on which to add a given value
            - value (Any): the value to add to the model
        """
        # FIXME: Due the way the mixins are ordered
        # on the ExtractYear, ExtractDay... classes,
        # the isinstance check on this fails therefore
        # trying to add a None string function item
        # to the model
        instances = (ExtractDay, ExtractMonth, ExtractYear, 
                     Add, Substract, Divide, Multiply)
        if isinstance(value, instances):
            value.model = self
            value.field_name = name
            return self._cached_result.update(name, value.resolve())

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
            resolved_value = str(obj._cached_result)
        
        self._cached_result.update(name, resolved_value)

    def resolve_fields(self):
        return self._cached_result.as_list()


class Model(DataStructure):
    """
    A Model is a class that helps you structure
    your scrapped data efficiently for later use

    Your custom models have to inherit from this
    base Model class and implement a set of fields
    from zineb.models.fields. For example:

            class MyModel(Model):
                name = CharField()

    Once you've created the model, you can then use
    it within your project like so:

            custom_model = MyModel()
            custom_model.add_value('name', 'p')
            custom_model.save()

            -> pandas.DataFrame
    """
    _cached_dataframe = None

    def __str__(self):
        return str(self._cached_result)
        
    def __repr__(self):
        return f"{self.__class__.__name__}"

    def __getitem__(self, field_name: str):
        return self._cached_result.get_container(field_name)
    
    # def __getattribute__(self, name):
    #     # When the acceses model.field_name
    #     # on the model, instead of returning the
    #     # field instance, we should return the
    #     # visual representation of the field
    #     meta = getattr(self, '_meta')
    #     if meta.has_field(name):
    #         smart_dict = getattr(self, '_cached_result')
    #         return smart_dict.get_container(name)
    #     return super().__getattribute__(name)
        
    # def __get__(self, attr):
    #     print(attr)

    def full_clean(self, dataframe, **kwargs):
        self._cached_dataframe = dataframe

    def clean(self, dataframe, **kwargs):
        """
        Put all additional functionnalities that you wish to
        run on the DataFrame here before calling the save
        function on your model
        """
        self._cached_dataframe = dataframe
        
    def save(self, commit: bool=True, filename: str=None, **kwargs):
        """
        Transform the collected data to a DataFrame which
        in turn will be saved to a JSON file.

        By setting commit to False, you will get a copy of the
        dataframe in order to run additional actions on it
        otherwise, the default behaviour will be to output
        to a file within your project.

        Parameters
        ----------

            commit (bool, optional): save to json file. Defaults to True.
            filename (str, optional): the file name to use. Defaults to None
        """
        # TODO:
        # signal.send(dispatcher.Any, self, tag='Pre.Save')
        dataframe = self.resolve_fields()

        self.full_clean(dataframe=dataframe)
        self.clean(self._cached_dataframe)

        if commit:
            if filename is None:
                filename = f'{secrets.token_hex(nbytes=5)}'
                
            # TODO:
            # signal.send(dispatcher.Any, self, tag='Post.Save')

            if settings.MEDIA_FOLDER is not None:
                filename = os.path.join(settings.MEDIA_FOLDER, filename)
                
            # return self._cached_dataframe.to_json(filename, orient='records')
            self._cached_result.save(commit=commit, filename=filename, **kwargs)
            return dataframe
        return self._cached_dataframe.copy()    
