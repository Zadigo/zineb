import bisect
import csv
import json
import os
import secrets
from collections import defaultdict, namedtuple
from functools import cached_property, lru_cache
from pathlib import Path

from zineb.exceptions import FieldError, ModelExistsError
from zineb.http.responses import HTMLResponse
from zineb.models.fields import Value, Field
from zineb.models.functions import (Add, Divide, ExtractDay, ExtractMonth,
                                    ExtractYear, Multiply, Substract, When)
from zineb.utils.containers import ModelSmartDict
from zineb.utils.formatting import LazyFormat

# FIXME: This raises a circular import error
# from zineb.models.fields import Value


DEFAULT_META_OPTIONS = {
    'constraints', 'ordering', 'verbose_name'
}

class ModelRegistry:
    """
    This class is a convienience container that remembers
    the models that were created and the order
    """
    counter = 0
    registry = defaultdict(dict)

    def __getitem__(self, name):
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
    for a given model such as fields,
    constraints...
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
        # NOTE: These are the initial constraints.
        # We might need to create another variable.
        self.constraints = []
        self.initial_model_meta = None
        
    def __repr__(self):
        return f'<{self.__class__.__name__} for {self.verbose_name}>'

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
    
    def _run_checks(self, declared_fields=None):
        checks = [
            self._check_fields_ordering
        ]
        for check in checks:
            # Since the model is not yet instantiated,
            # we used the declared collected fields to
            # run the check at the very top level. Other
            # option would be to run this check at the
            # __init__ level
            check(declared_fields)
    
    def _check_fields_ordering(self, declared_fields):
        for field in self.get_option_by_name('ordering'):
            for declared_field in declared_fields:
                if field not in declared_field:
                    raise FieldError(field, [])

    def get_option_by_name(self, name):
        return self.cached_options.get(name)

    def has_option(self, name):
        return name in self.cached_options
    
    @property
    def has_ordering(self):
        return self.ordering
        
    def _check_ordering_fields(self):
        for name in self.ordering:
            if name not in self.field_names:
                raise FieldError(name, self.field_names)
            
    def _check_constraints(self):
        names = set()
        duplicates = []
        
        for constraint in self.constraints:
            names.add(constraint.name)
            
            if constraint.name in  names:
                duplicates.append(constraint.name)
                
        if duplicates:
            raise ValueError('Constraints should have a unique name')
            
    def _checks(self):
        return [
            self._check_ordering_fields,
            self._check_constraints
        ]
        
    def _prepare(self):
        """Final step to prepare the model for
        final use in a project"""
        # Include the ID field by default for functions
        # or definitions that might require using this.
        # If we have not inherited from an ID field
        # skip this process
        from zineb.models.fields import AutoField
        self.set_field_names()
        if not self.has_field('id'):
            auto_field = AutoField(auto_created=True)
            self.add_field('id', auto_field)
        
    def has_field(self, name):
        return name in self.field_names
    
    # TODO: Is this useful ??
    # def add_constraint(self, name):
    #     pass
        
    def add_field(self, name, field):
        if name in self.fields_map:
            raise ValueError(f"Field '{name}' is already present on the model '{self.model_name}'")
        
        if getattr(field, 'is_relationship_field', False):
            # We have to keep track of a two way relationship:
            # one from model1 -> model2 and the reverse from
            # model1 <- model2 where model1.field accesses
            # model2 and model2.field_set accesses model1
            self.related_model_fields[name] = field
        self.fields_map[name] = field
        self.field_names.append(name)
        
        field.creation_counter = len(self.field_names) - 1
        self.set_field_names()
        
    def set_field_names(self):
        sorted_names = []
        names = self.fields_map.keys()
        for name in names:
            bisect.insort(sorted_names, name)
        self.field_names = sorted_names
        
    # def update_fields(self, fields):
    #     for name, items in fields:
    #         field, parent = items
    #         self.parents[parent] = field

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

        # TODO:
        # declared_fields = set()
        # for key, field_obj in attrs.items():
        #     if isinstance(field_obj, Field):
        #         field_obj._bind(key, model=cls)
        #         declared_fields.add((key, field_obj))

        meta_attributes = attrs.pop('Meta', None)
        
        # "Remove" all the declared fields on the model.
        # They will be replaced later on with a descriptor
        # that wil load the fields true value directly
        # from the data container
        new_attrs = {}
        for item_name, value in attrs.items():
            # "update_model_options" is a method that
            # explicitly tells the Meta class that 
            # the ModelOptions should reference the
            # object that requires it to be bound
            # to the given model
            if not hasattr(value, 'update_model_options'):
                new_attrs[item_name] = value
                
        new_class = super_new(cls, name, bases, new_attrs)

        meta = ModelOptions(new_class, name)
        meta.initial_model_meta = meta_attributes
        setattr(new_class, '_meta', meta)
        
        # If the model is subclassed, resolve the MRO
        # to get all the fields from the superclass
        super_class_fields = []
        for parent in bases:
            if hasattr(parent, '_meta'):
                fields = parent._meta.fields_map
                meta.parents.add(parent)
                
                for name, field in fields.items():
                    super_class_fields.append((name, field, parent))
                                
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
                
        # Now that we've resolved all fields
        # from the model itself, deal with
        # those present on the parent
        if super_class_fields:
            for item in super_class_fields:
                field_name, field, parent = item

                if meta.has_field(field_name):
                    continue
                                
                meta.fields_map[field_name] = field
                
            # If the superclass has a Meta that the user
            # has configured, we have to inherit from it 
            # and copy the values in the subclass's meta
            if parent._meta.initial_model_meta is not None:
                meta_attributes_to_update = {'ordering', 'constraints', 'initial_model_meta'}
                for attribute in meta_attributes_to_update:
                    setattr(meta, attribute, getattr(parent, attribute))
            
        # Deal with all the options on 
        # the "Meta" of the given model
        if meta_attributes is not None:
            meta_dict = meta_attributes.__dict__
            
            declared_options = []
            for key, value in meta_dict.items():
                if key.startswith('__'):
                    continue
                declared_options.append((key, value))
            meta.add_meta_options(declared_options)
                        
        new_class._prepare()
        return new_class
    
    def _prepare(cls):
        cls._meta._prepare()
        model_registry.add(cls.__name__, cls)


class Model(metaclass=Base):
        
    """
    A Model is a class that helps you structure
    your scrapped data efficiently for later use. It has to 
    inherit from this base Model class and implement fields.

    >>> class MyModel(Model):
            name = CharField()

    Once you've created the model, you can then use
    it within your project like so:

    >>> model = MyModel()
    ... model.add_value('name', 'Kendall')
    ... model.save()
    ... [{"name": "Kendall"}]
    """
    
    _cached_resolved_data = None
    
    def __init__(self):
        self._data_container = ModelSmartDict.new_instance(self)
        
        # When the class is instantiated, that's where
        # we finalize the relationships between all the
        # classes by making sure that they are
        # correctly instantiated
        related_model_fields = self._meta.related_model_fields
        if related_model_fields:
            for field in related_model_fields.values():
                if isinstance(field.related_model, type):
                    setattr(field, 'related_model', field.related_model())

        # self.html_document = html_document
        # self.response = response

        # self.parser = self._choose_parser()
        
        # When the model is initialized, we bind it
        # to the constraint if there are any
        for constraint in self._meta.constraints:
            constraint.update_model_options(self)

        # Errors aggregated from the different
        # other pieces that compose the model
        self.global_errors = []

    def __str__(self):
        # data = self._data_container.as_list()
        return str(self.resolve_all_related_fields())

    def __repr__(self):
        return f"{self.__class__.__name__}"
    
    def __hash__(self):
        attrs = [self._meta.verbose_name, len(self._meta.field_names), self.id]
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

    @staticmethod
    def check_special_function(value):
        """Checks if the incoming value is a special function
        e.g. ExtractYear, ExtractMonth and resolves it to
        its true self"""
        # FIXME: Due the way the mixins are ordered
        # on the ExtractYear, ExtractDay... classes,
        # the isinstance check on this fails therefore
        # trying to add a None string function item
        # to the model
        # FIXME: Value is not deep cleaned when using
        # the special functions
        return isinstance(value, (ExtractDay, ExtractMonth, ExtractYear))
        
    @property
    def _get_internal_data(self):
        return dict(self._cached_result.values)
        
    @lru_cache(maxsize=10)
    def resolve_all_related_fields(self):
        # When returning the data, we have to map all
        # the related fields in order to return their
        # own values
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

    def _bind_to_value_field(self, field_name, data):
        instance = Value(data)
        instance.field_name = field_name
        return instance
        
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
        # TODO: Maybe move this to the
        # options class
        field = self._meta.get_field('id')
        field.resolve()
    
    def add_calculated_value(self, name, value, *funcs):
        """Adds a value to the model after running an 
        arithmetic operation
        
        >>> model.add_calculated_value("age", 21, Add(3), Substract(1))
        ... 23
        """
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
        
        # value = self.check_special_function(name, value)

        if len(funcs) == 1:
            func = funcs[-1]
            func._cached_data = Value(value)
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
        conditions determined by a When-function

        >>> model.add_case("kendall", When("name_eq=kendall", "Kendall"))
        ... "Kendall"
        """
        if not isinstance(case, When):
            raise TypeError('Case should be a When class.')

        # We let the user test against the
        # raw value directly. This opens more
        # options for him
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
        Add a single row at once on the model
        using either a dictionnary or keywords

        >>> model.add_values(name="Kendall")
        >>> model.add_values({"name": "Kendall"})
        """
        # FIXME: The user can just add values without any
        # formatting whatsoever? This should be fixed in
        # order that the values that are added be deep_cleaned
        # formatted correctly for consistency
        self._fields.has_fields(list(attrs.keys()), raise_exception=True)
        self._data_container.update_multiple(**attrs)
        self.update_id_field()

    def add_value(self, name, value):
        """
        Adds a value to the model

        >>> model.add_value("name", "Kendall")
        """
        # FIXME: Due the way the mixins are ordered
        # on the ExtractYear, ExtractDay... classes,
        # the isinstance check on this fails therefore
        # trying to add a None string function item
        # to the model

        obj = self._get_field_by_name(name)

        state = self.check_special_function(value)
        if state:
            value.model = self
            value.field_name = name
            value.resolve()
            resolved_value = value._cached_data
        else:
            if not isinstance(value, Value):
                # We know that the Value field deep_cleans
                # and formats the raw value. Makes no sense
                # to redo all of this if we already have a
                # Value instance
                value = self._bind_to_value_field(obj.field_name, value)

            obj.resolve(value)
            resolved_value = obj._cached_result

            if obj.internal_name == 'DateField':
                # Some fields such as the DateField does not
                # store a string but a function. For example,
                # in this case, a datetime.datetime objec.
                # Therefore we have to resolve the true value of the field
                # otherwise the user might get something unexpected
                resolved_value = str(obj._cached_result)

        # Before saving the value to the model, check
        # constraints aka existing values if the user
        # has required this step
        result = self.check_constraints(resolved_value)
        if result:
            self._data_container.update(name, resolved_value)
            self.update_id_field()

    def check_constraints(self, clean_value):
        constraint_errors = []
        for constraint in self._meta.constraints:
            constraint_result = constraint(clean_value)
            constraint_errors.extend(constraint_result)
        self.global_errors.extend(constraint_errors)
        return False if constraint_errors else True

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
        
    def save(self, commit=True, filename=None, extension='json', **kwargs):
        """
        Transform the collected data to a DataFrame which
        in turn can be saved to a JSON file.

        By setting commit to False, you will get a copy of the
        dataframe in order to run additional actions on it
        otherwise, the default behaviour will be to output
        to a file within your project.
        """
        # TODO: Send a signal before the model
        # is saved - pre_save
        
        self.full_clean()

        if commit:
            from zineb.settings import settings
            from zineb.utils.encoders import DefaultJsonEncoder
            
            if filename is None:
                filename = f'{secrets.token_hex(nbytes=5)}'
                
            try:
                path = Path(settings.MEDIA_FOLDER)
                if not path.exists():
                    path.mkdir()
            except:
                raise Exception('Could not find media folder')
            else:
                full_path = path.joinpath(filename)
                
                acceptable_extensions = ['json', 'csv']
                if extension not in acceptable_extensions:
                    raise ValueError('Extension should b one of csv or json')
                
                full_path = f"{full_path}.{extension}"
                
                if extension == 'json':
                    data = json.loads(json.dumps(self._data_container.as_list()))
                    with open(full_path, mode='w', encoding='utf-8') as f:
                        json.dump(data, f, indent=2, sort_keys=2, cls=DefaultJsonEncoder)
                
                if extension == 'csv':
                    with open(full_path, mode='w', newline='\n', encoding='utf-8') as f:
                        writer = csv.writer(f)
                        writer.writerows(self._data_container.as_csv())    
            
                
            # TODO: Send a signal after the model
            # is saved - post_save
                
            # self._data_container.execute_save(commit=commit, filename=filename, **kwargs)
        return self._cached_resolved_data    
