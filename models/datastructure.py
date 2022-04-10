import bisect
import os
import secrets
from collections import OrderedDict, defaultdict, namedtuple
from functools import cached_property, lru_cache
from importlib import import_module

# from zineb.checks.messages import DEBUG
from zineb.exceptions import FieldError, ModelExistsError
from zineb.http.responses import HTMLResponse
from zineb.models.functions import (Add, Divide, ExtractDay, ExtractMonth,
                                    ExtractYear, Multiply, Substract, When)
from zineb.settings import settings
from zineb.utils.containers import SmartDict
from zineb.utils.formatting import LazyFormat

DEFAULT_META_OPTIONS = {
    'constraints', 'ordering', 'verbose_name',
    'include_id_field'
}

class ModelRegistry:
    """
    This class is a convienience container that remembers
    the models that were created and the order
    """
    counter = 0
    registry = defaultdict(dict)

    def __getitem__(self, name: str):
        return self.registry[name]

    @cached_property
    def models(self):
        return list(self.registry.values())

    def add(self, name, model):
        if name in self.registry:
            raise ModelExistsError(name)

        self.counter = self.counter + 1
        self.registry[name] = model


model_registry = ModelRegistry()


class ModelOptions:
    """
    A container that stores the options
    of a given model including both the 
    fields and the Meta options
    """
    def __init__(self, model, model_name):
        self.model = model
        model_name = model.__name__
        self.model_name = model_name.lower()
        self.verbose_name = model_name.title()
        self.field_names = []
        self.fields_map = {}
        self.related_model_fields = {}
        self.parents = set()
        self.ordering = []
        self.constraints = []
        
    def __repr__(self):
        return f'<{self.__class__.__name__} for {self.verbose_name}>'
    
    @property
    def has_ordering(self):
        return self.ordering
        
    def _check_ordering_fields(self):
        for name in self.ordering:
            if name not in self.field_names:
                raise FieldError(name, self.field_names)
            
    def _checks(self):
        return [
            self._check_ordering_fields
        ]
        
    def _prepare(self):
        # Include the ID field by default for functions
        # or definitions that might require using this
        from zineb.models.fields import AutoField
        self.add_field('id', AutoField())

    def add_field(self, name, field):
        if name in self.fields_map:
            raise ValueError('Field is already present on the model')
        
        if getattr(field, 'is_relationship_field', False):
            # We have to keep track of a two way relationship:
            # one from model1 -> model2 and the reverse from
            # model1 <- model2 where model1.field accesses
            # model1 and model2.field_set accesses model2
            self.related_model_fields[name] = field
        self.fields_map[name] = field
        self.field_names.append(name)
        
        field.creation_counter = len(self.field_names) - 1
        
        sorted_names = []
        for name in self.field_names:
            bisect.insort(sorted_names, name)
        self.field_names = sorted_names
        
    def update_fields(self, fields):
        for name, items in fields:
            field, parent = items
            self.parents[parent] = field

    def add_meta_options(self, options):
        for name, value in options:
            if name not in DEFAULT_META_OPTIONS:
                raise ValueError(LazyFormat("Meta for model '{name}' received "
                "and illegal option '{option}'", name=self.verbose_name, option=name))
            setattr(self, name, value)
        
            
        # TODO: Alter the check so that if the field
        # starts with a - on the ordering, that it
        # does not create an error
        # for check in self._checks():
        #     check()
            
    def get_field(self, name):
        try:
            return self.fields_map[name]
        except KeyError:
            raise FieldError(name, self.field_names, model_name=self.model_name)
        
    def get_ordering(self):
        def remove_prefix(value):
            return value.removeprefix(('-'))
        
        ascending_fields = [
            field for field in self.ordering
                if not field.startswith('-')
        ]
        
        descending_fields = [
            field for field in self.ordering
                if field.startswith('-')
        ]
    
        # Create a map that can be used by the internal
        # python sorted method. The Ascending order is
        # represented by the minus
        ordering_map = [
            (remove_prefix(name), name.startswith('-'))
                for name in self.ordering
        ]
        ordering = namedtuple('Ordering', ['ascending_fields', 'descending_fields', 'booleans'])
        return ordering(ascending_fields, descending_fields, ordering_map)    

        
class Base(type):
    def __new__(cls, name, bases, attrs):
        super_new = super().__new__
        
        parents = [b for b in bases if isinstance(b, Base)]
        if not parents:
            return super_new(cls, name, bases, attrs)

        meta_attributes = attrs.pop('Meta', None)
        
        # "Remove" all the declared fields on the model.
        # They will be replaced later on with descriptor
        # that wil load the fields true value directly
        # from the data container
        new_attrs = {}
        for item_name, value in attrs.items():
            if not hasattr(value, 'update_model_options'):
                new_attrs[item_name] = value
                
        new_class = super_new(cls, name, bases, new_attrs)

        meta = ModelOptions(new_class, name)
        setattr(new_class, '_meta', meta)
        
        # If the model is subclassed, resolve the MRO
        # to get all the fields from the superclass
        super_class_fields = []
        for parent in bases:
            if hasattr(parent, '_meta'):
                fields = parent._meta.fields_map
                for name, field in fields.items():
                    super_class_fields.append({name: (field, parent)})
                    
        # Get all the declared items on the model
        # regardless whether they are fields or not
        # and if they have update_model_options function
        # we would then know that they should be included
        # to the ModelOptions class defining their own
        # way of how they should be integrated
        for name, item in attrs.items():
            if hasattr(item, 'update_model_options'):                
                item.update_model_options(new_class, name)
            else:
                setattr(cls, name, item)
            
                
        # Get the Meta options class
        if meta_attributes is not None:
            meta_dict = meta_attributes.__dict__
            
            declared_options = []
            for key, value in meta_dict.items():
                if key.startswith('__'):
                    continue
                declared_options.append((key, value))
            meta.add_meta_options(declared_options)
                        
        # # If the model is subclassed, resolve the MRO
        # # to get all the fields from the superclass
        # # [...] also maybe create direct relationship
        # # with the parent model via a ForeignKey
        # for parent in bases:
        #     if hasattr(parent, '_meta'):
        #         fields = getattr(getattr(parent, '_meta'), 'cached_fields', {})
        #         for key, field_obj in fields.items():
        #             # If the field is registered twice (on the
        #             # superclass and on the subclass), use the
        #             # subclass version of the field
        #             if field_obj not in declared_fields:
        #                 declared_fields.add((key, field_obj))
        #             # Create the map that will allow us to register
        #             # and use ForeignKey type fields in forward and
        #             # backward relationships
        #             # meta.forward_fields_map.update({key: field_obj})
        #         meta.parents.append(parent)

        # meta.model_name = name
        # if declared_fields:
        #     meta.cached_fields = OrderedDict(declared_fields)

        # # if 'Meta' in attrs:
        # #     meta_dict = attrs.pop('Meta').__dict__
        # #     non_authorized_options = []

        # #     def check_option(item):
        # #         key, _ = item
        # #         if key.startswith('__'):
        # #             return False

        # #         if key in meta.authorized_options:
        # #             return True
                
        # #         non_authorized_options.append(key)
        # #         return False

        # #     options = list(filter(check_option, meta_dict.items()))
        # #     if non_authorized_options:
        # #         raise ValueError("Meta received an illegal "
        # #         f"option. Valid options are: {', '.join(meta.authorized_options)}")
        # #     default_options.extend(options)
        # #     meta = meta(default_options)
            
        # # attrs['_meta'] = meta

        # if declared_fields:
        #     # is_template_model = False
        #     # if meta.has_option('template_model'):
        #     #     is_template_model = meta.get_option_by_name('template_model')
        #     # # The parent model is just a template,
        #     # # we'll not create any ForeignKey
        #     # # relationship to the parent
        #     # if not is_template_model:
        #     #     relationships = [
        #     #         (f"{parent}_rel", ForeignKey(new_class, parent)) 
        #     #             for parent in new_class._meta.parents
        #     #     ]
        #     #     meta.cached_fields.update(relationship for relationship in relationships)

        #     # That's where is explicitely register
        #     # models that have declared fields and
        #     # that are actually user created models -;
        #     # this might seem odd to implement this block
        #     # but it allows us to do additional things on
        #     # on the new model and its meta
        #     model_registry.add(name, new_class)
        #     return new_class
        new_class._prepare()
        return new_class
    
    def _prepare(cls):
        cls._meta._prepare()
        model_registry.add(cls.__name__, cls)


class Model(metaclass=Base):
        
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
    """
    
    _cached_resolved_data = None
    
    def __init__(self, html_document=None, response=None):
        self._data_container = SmartDict.new_instance(self)
        
        # When the class is instantiated, that's where
        # we finalize the relationships between all the
        # classes by making sure that they are
        # correctly instantiated
        related_model_fields = self._meta.related_model_fields
        if related_model_fields:
            for field in related_model_fields.values():
                if isinstance(field.related_model, type):
                    setattr(field, 'related_model', field.related_model())

        self.html_document = html_document
        self.response = response

        self.parser = self._choose_parser()

    def __str__(self):
        # data = self._data_container.as_list()
        return str(self.resolve_all_related_fields())

    def __repr__(self):
        return f"{self.__class__.__name__}"
    
    def __hash__(self):
        attrs = [self._meta.verbose_name, len(self._meta.field_names)]
        if self._meta.include_id_field:
            attrs.append(self.id)
        return hash(tuple(attrs))
    
    def __getattr__(self, name):
        id_names = ['id', 'pk']
        if name in id_names:
            field = self._meta.get_field('id')
            return field._tracked_id
        
    def __reduce__(self):
        return self.__class__, (self._meta.verbose_name,), {}
    
    def __eq__(self, obj):
        if not isinstance(obj, Model):
            raise ValueError('Object to compare is not a Model')
        return all([
            self._meta.model_name == obj._meta.model_name,
            self._meta.field_names == obj._meta.field_names
        ])
        
    @lru_cache(maxsize=10)
    def resolve_all_related_fields(self):
        # When return the data, we have to map all
        # the related fields in order to return their
        new_data = self._data_container.as_list()
        related_model_fields = self._meta.related_model_fields
        if related_model_fields:
            for name, field in related_model_fields.items():
                related_model_data = field.related_model._data_container.as_list()
                for item in new_data:
                    item[name] = related_model_data
        return new_data
    
    def _get_field_by_name(self, field_name):
        """
        Gets the cached field object that was registered
        on the model via the FieldDescriptor
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

    def _add_without_field_resolution(self, field_name, value):
        """
        When the value of a field has already been
        resolved, just add it to the model. This is
        an internal function used for the purpose of
        other internal functions since there is no
        field resolution and raw data from the internet
        would be added as is
        """
        cached_values = self._data_container.get_container(field_name)
        cached_values.append(value)
        self._data_container.update(field_name, cached_values)
        
    def _checks_for_fields(self):
        errors = []
        for field in self._meta.fields_map.values():
            errors.extend(field.checks())
        return errors
    
    def checks(self):
        # This is the main collector for all the errors
        # that might have occured during the creation
        # of the the current model
        return [
            *self._checks_for_fields()
        ]
        
    def update_id_field(self):
        if self._meta.include_id_field:
            field = self._meta.get_field('id')
            field.resolve()
    
    def add_calculated_value(self, name, value, *funcs):
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
            # TODO: Do not trust the user and check
            # if the field actually exists on the
            # model before passing to the func
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
                    # should be the _caclulate_result of the
                    # previous one. This technique allows
                    # us to run multiple expressions on
                    # one single value
                    funcs[i]._cached_data = funcs[i - 1]._cached_data
                funcs[i].resolve()
            # Once everything has been calculated,
            # use the data of the last function to
            # add the given value to the model
            self.add_value(funcs[-1].field_name, funcs[-1]._cached_data)
            self.update_id_field()

    def add_case(self, value, case):
        """
        Add a value to the model based on a specific
        conditions determined by a When-function.
        """
        if not isinstance(case, When):
            raise TypeError('Case should be a When class.')

        case._cached_data = value
        case.model = self
        field_name, value = case.resolve()
        self.add_value(field_name, value)
        self.update_id_field()

    def add_using_expression(self, name, tag, attrs={}):
        """
        Adds a value to your Model object using an expression. Using this
        method requires that you pass and BeautifulSoup object to your model.
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
        self._data_container.update(name, resolved_value)
        self.update_id_field()

    def add_values(self, **attrs):
        """
        Add a single row at once on your model
        using either a dictionnary or keyword
        arguments
        """
        self._fields.has_fields(list(attrs.keys()), raise_exception=True)
        self._data_container.update_multiple(**attrs)
        self.update_id_field()

    def add_value(self, name, value):
        """
        Adds a value to the Model object
        """
        # FIXME: Due the way the mixins are ordered
        # on the ExtractYear, ExtractDay... classes,
        # the isinstance check on this fails therefore
        # trying to add a None string function item
        # to the model
        instances = (ExtractDay, ExtractMonth, ExtractYear)
        
        if isinstance(value, instances):
            value.model = self
            value.field_name = name
            value.resolve()
            return self._data_container.update(name, value._cached_data)

        obj = self._get_field_by_name(name)
        obj.resolve(value)
        resolved_value = obj._cached_result

        if obj.internal_name == 'DateField':
            # Some fields such as the DateField does not
            # store a string but a function. For example,
            # in this case, a datetime.datetime object is
            # stored. In that case, we have to resolve to
            # the true value of the field. Otherwise the
            # user might get something unexpected
            resolved_value = str(obj._cached_result)
        
        self._data_container.update(name, resolved_value)
        self.update_id_field()

    def full_clean(self, **kwargs):
        # data = self._data_container.as_list()
        data = self.resolve_all_related_fields()
        self._cached_resolved_data = data
        self.clean(data)

    def clean(self, dataframe, **kwargs):
        """
        Put all additional functionnalities that you wish to
        run on the DataFrame here before calling the save
        function on your model
        """
        
    def save(self, commit=True, filename=None, **kwargs):
        """
        Transform the collected data to a DataFrame which
        in turn will be saved to a JSON file.

        By setting commit to False, you will get a copy of the
        dataframe in order to run additional actions on it
        otherwise, the default behaviour will be to output
        to a file within your project.
        """
        # TODO: Send a signal before the model
        # is saved
        
        self.full_clean()

        if commit:
            if filename is None:
                filename = f'{secrets.token_hex(nbytes=5)}'
                
            # TODO: Send a signal after the model
            # is saved
    
            if settings.MEDIA_FOLDER is not None:
                filename = os.path.join(settings.MEDIA_FOLDER, filename)
                
            self._data_container.execute_save(commit=commit, filename=filename, **kwargs)
        return self._cached_resolved_data    
