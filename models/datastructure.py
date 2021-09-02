import os
import secrets
from collections import OrderedDict, defaultdict
from functools import cached_property
from typing import Any, List, Union

from bs4 import BeautifulSoup
from pydispatch import dispatcher
from zineb.exceptions import FieldError, ModelExistsError
from zineb.http.responses import HTMLResponse
from zineb.models.expressions import Calculate
from zineb.models.fields import Field
from zineb.settings import settings
from zineb.signals import signal


class DataContainers:
    """
    A container that regroups all the data that
    has been parsed by the model fields
    
    Parameters
    ----------

        - names: list of field names
    """
    values = defaultdict(deque)

    @classmethod
    def as_container(cls, *names):
        # In order to prevent the values
        # parameter to reinstantiate with
        # the names when using this class,
        # we'll create a new instance of
        # the class and return it. In that
        # sense, this will prevent
        for name in names:
            cls.values[name]
        instance = cls()
        setattr(instance, 'names', list(names))
        return instance

    def __repr__(self):
        return self.values

    def __str__(self):
        return str(self.values)

    def get_container(self, name: str):
        return self.values[name]

    def update(self, name: str, value: Any):
        self.values[name].append(value)

    def finalize(self):
        """
        Makes sure that all the arrays
        are of same lengths before returning
        the containers.This adds None to the
        unbalanced containers.

        Returns
        -------

            - OrderedDict: the finalized values 
        """
        containers = list(self.values.values())
        container_lengths = [len(container) for container in containers]
        max_length = max(container_lengths)

        def fill_none_values(container):
            values_to_complete = max_length - len(container)
            for _ in range(values_to_complete):
                container.append(None)
            return container

        for i in range(0, len(containers)):
            if len(containers[i]) < max_length:
                fill_none_values(containers[i])

        new_values = []

        for i in range(0, len(self.names)):
            new_values.append((self.names[i], containers[i]))

        return OrderedDict(new_values)


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


class FieldDescriptor:
    """A class that contains and stores
    all the given fields of a model"""

    cached_fields = OrderedDict()
    
    def __getitem__(self, key) -> Field:
        return self.cached_fields[key]

    @cached_property
    def field_names(self):
        return list(self.cached_fields.keys())


class ModelOptions:
    """A container that stores all the options
    of a given model

    Parameters
    ----------

        - options (Union[List[tuple[str]], dict]): list of options
    """
    def __init__(self, options: Union[List[tuple[str]], dict]):
        self.cached_options = OrderedDict(options)

        self.ordering_field_names = set()
        self.ascending_fields = []
        self.descending_fields = []
        self.ordering_booleans = []
        
        if self.has_option('ordering'):
            ordering = self.get_option_by_name('ordering')
            # self.ordering_field_names = list({
            #     field.removeprefix('-') for field in ordering
            # })
            for field in ordering:
                self.ordering_field_names.add(
                    field.removeprefix('-')
                )
            self.ascending_fields = [
                field for field in ordering 
                    if not field.startswith('-')
            ]
            self.descending_fields = [
                field for field in ordering 
                    if field.startswith('-')
            ]

            # Convert each ordering field on the
            # model Booleans. This is what a
            # DataFrame accepts in or to order
            # the data
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
    def __new__(cls, name, bases, attrs):
        super_new = super().__new__
        parents = [b for b in bases if isinstance(b, Base)]

        if not parents:
            return super_new(cls, name, bases, attrs)

        if name != 'Model':
            # Normally, we should have all the fields
            # and/or remaining methods of the class
            declared_fields = set()
            for key, item in attrs.items():
                if isinstance(item, Field):
                    declared_fields.add((key, item))

            descriptor = FieldDescriptor()
            descriptor.cached_fields = OrderedDict(declared_fields)

            meta = ModelOptions([])
            if 'Meta' in attrs:
                # TODO: If the user does not pass
                # a 'class Meta', this could be a
                # serious issue and break
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
                    f"option. Valid options are: {', '.join(authorized_options)}")
                meta = meta(options)

            new_class = super_new(cls, name, bases, attrs)
            setattr(new_class, '_fields', descriptor)
            setattr(new_class, '_meta', meta)

            model_registry.add(name, new_class)
            return new_class

        return super_new(cls, name, bases, attrs)


class DataStructure(metaclass=Base):
    def __init__(self, html_document: BeautifulSoup=None, 
                 response: HTMLResponse=None):
        self._cached_result = {}

        self.html_document = html_document
        self.response = response

        self.parser = self._choose_parser()

    def _get_field_by_name(self, field_name) -> Field:
        """
        Gets the cached field object that was registered
        on the model via the FieldDescriptor

        Parameters
        ----------

            - name (str): the field name to get

        Raises
        ------

            - FieldError: if the field does not exist

        Returns
        -------

            - Field (type): zineb.fields.Field
        """
        try:
            return self._fields.cached_fields[field_name]
        except:
            raise FieldError(field_name, self._fields.field_names)

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
        other internal functions.

        Parameters
        ----------

            value (Any): value to add to the the model
        """
        cached_values = self._cached_result.get(field_name, [])
        cached_values.append(value)
        self._cached_result.update({ field_name: cached_values })

    def add_calculated_value(self, value: Any, *funcs):
        funcs = list(funcs)

        all_field_names = []
        unique_field_names = set()
        for func in funcs:
            if not isinstance(func, Calculate):
                raise TypeError('Function should be an instance of Calculate')

            setattr(func, 'model', self)
            # Technically, the funcs should
            # apply to the same field on the
            # model or this could create
            # inconsistencies
            all_field_names.append(func.field)
            unique_field_names.add(func.field)

        all_field_names = set(all_field_names)
        result = unique_field_names.difference(all_field_names)
        if result:
            raise ValueError('Functions should apply to the same field')

        if len(funcs) == 1:
            func._cached_data = value
            func.resolve()
            self.add_value(func.field, func._calculated_result)
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
                    funcs[i]._cached_data = funcs[i - 1]._calculated_result
                funcs[i].resolve()
            # Once everything has been calculated,
            # use the data of the last function to
            # add the given value to the model
            self.add_value(funcs[-1].field, funcs[-1]._calculated_result)

    def add_case(self, value: Any, case):
        """
        Add a value to the model based on a specific
        conditions determined by a When-function.

        Parameters
        ----------

            value (Any): the value to test
            case (Type): When function
        """
        # cases = list(cases)
        case._cached_result = value
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
            raise ValueError(('No valid parser could be user. '
            'Make sure you pass a BeautifulSoup '
            'or an HTTPRespsone object to your model that can be used '
            'to resolve the expression'))

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

            - name (str): the name of field on which to add a given value
            - value (Any): the value to add to the model
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
        
        self._add_without_field_resolution(name, resolved_value)

    def add_expression(self, **expressions):
        """
        Add multiple values to your model using a
        set of expressions.
        """
        pass

    def add_related_value(self, name: str, related_field: str, value: Any):
        """
        Add a value to a field based on the last
        result of another field.

        The related fields should be of the same data type
        or this might raise errors.

        Parameters
        ----------

            - name (str): name of the field to which to add the value
            - related_field (str): name of the base field from which to derive a result
            - value (Any): the value to add to the original field
        """
        if name == related_field:
            raise ValueError('Name and related name should not be the same.')

        related_field_object = self._get_field_by_name(related_field)
        
        self.add_value(name, value)
        cached_values = self._cached_result.get(name)

        last_value = cached_values[-1]
        related_field_object.resolve(last_value)

        related_field_values = self._cached_result.get(related_field, [])
        related_field_values.append(related_field_object._cached_result)
        self._cached_result.update({ related_field: related_field_values })

    def resolve_fields(self):
        """
        Implement the data into a Pandas
        Dataframe and return the result
        """
        # TODO: Before doing anything with
        # the data, we either need to check
        # that the lists are of same length
        # or ensure that everytime an element
        # is added to one the arrays and not
        # in the other, to put a None value
        df = pandas.DataFrame(
            self._cached_result, 
            columns=self._fields.field_names,
        )

        if self._meta.has_option('ordering'):
            try:
                df = df.sort_values(
                    by=self._meta.ordering_field_names,
                    ascending=self._meta.ordering_booleans
                )
            except KeyError:
                raise KeyError(("Looks like a field is not part of your model."
                "Please check your ordering fields."))
        return df


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

    def __str__(self) -> str:
        return str(self._cached_result)
        
    def __repr__(self):
        return f"{self.__class__.__name__}"

    def __getitem__(self, field_name: str):
        return self._cached_result.get(field_name, None)

    # def __setitem__(self, field_name: str, value: Any):
    #     self.add_value(field_name, value)

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
        Transform the collected data to a DataFrame which
        in turn will be saved to a JSON file.

        By setting commit to False, you will get a copy of the
        dataframe in order to run additional actions on it
        otherwise, the default behaviour will be to output
        to a file within your project.

        Parameters
        ----------

            commit (bool, optional): save to json file. Defaults to True.
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

            if settings.MEDIA_FOLDER is not None:
                filename = os.path.join(settings.MEDIA_FOLDER, filename)
                
            return self._cached_dataframe.to_json(filename, orient='records')
        return self._cached_dataframe.copy()    
