import re
import secrets
from collections import OrderedDict

import pandas
from zineb.http.responses import HTMLResponse
from zineb.models.fields import Field


class FieldDescripor:
    cached_fields = OrderedDict
    
    def __getitem__(self, key) -> Field:
        return self.cached_fields[key]


class ModelOptions:
    def __init__(self, options:dict = {}):
        pass


class Base(type):
    def __new__(cls, name, bases, attrs):
        super_new = super().__new__
        parents = [b for b in bases if isinstance(b, Base)]

        if not parents:
            return super_new(cls, name, bases, attrs)

        # fields = []
        if name != 'Model':
            # new_attrs = {}
            # class_module = attrs.pop('__module__')
            # class_qualname = attrs.pop('__qualname__')

            # fields = list(attrs.keys())
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
                authorize_options = []

                def check_option(key, value):
                    return key, value

                options = [check_option(key, value) for key, value in meta_dict.items()]
                meta = ModelOptions(options=options)

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
# class DataStructure(Registry, metaclass=Base):
    def __init__(self, html_document=None, html_tag=None, response=None):
        self._cached_result = {}
        self.html_document = html_document
        self.html_tag = html_tag
        self.response = response
        self.parser = self._choose_parser()

    @staticmethod
    def _expression_resolver(expression: str):
        attr = None
        if '__' in expression:
            expression, attr = expression.split('__', 1)
        tag_id = tag_class = {}
        tag = re.search(r'^(\w+)(?=\.|\#)', expression)
        if tag:
            tag = tag.group()[-1]
        a = re.search(r'(?<=\.)(?P<class>\w+\-?\w+)', expression)
        b = re.search(r'(?<=\#)(?P<id>\w+\-?\w+)', expression)
        if a:
            tag_id = a.groupdict()
        if b:
            tag_class = b.groupdict()
        return tag, tag_id | tag_class, attr

    def _get_field_by_name(self, name):
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
            return self._meta.cached_fields[name]
        except:
            raise KeyError(f"The field is not present on your model. Available fields are: {', '.join(self._meta.cached_fields)}")

    def _choose_parser(self):
        # In case we get both the HTML document
        # and a tag, use the most global element
        # in order to have a better change to get
        # something from it
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

    def _parse_tags(self, tags, field_name, field_obj, base, attributes=None):
        for index, tag in enumerate(tags):
            new_base = base.copy()
            if attributes is not None:
                lhs, rhs = attributes
                if lhs == 'id':
                    if index == rhs:
                        new_base.update({field_name: field_obj.resolve(tag.text)})
            else:
                new_base.update({field_name: field_obj.resolve(tag.text)})
            # self._cached_result.append(new_base)

    # def add_expression(self, name, expression):
    #     """
    #     Adds a value to your Model object using an expression

    #     Parameters
    #     ----------

    #             field_name (str): the name of field on which to add a given value
    #             expression (str): an expression used to query or parse tags in the document
    #     """
    #     obj = self._resolve(name)

    #     allow_pseudos = ['text', 'href', 'src']
    #     tag, attrs, pseudo = self._expression_resolver(expression)
    #     if pseudo not in allow_pseudos:
    #         raise TypeError(f"Pseudo should be one of {', '.join(allow_pseudos)}")
        
    #     # In this specific case, only find the first
    #     # occurrence of a given tag on the page or
    #     # within the HTML soup object
    #     tag = self.parser.find(tag, attrs=attrs)

    #     element_text = None
    #     if tag or tag is not None:
    #         element_text = None
    #         if pseudo == 'text':
    #             element_text = tag.text
    #         else:
    #             element_attrs = tag.attrs
    #             if tag.has_attr(pseudo):
    #                 element_text = element_attrs.get(pseudo)

    #         resolved_value = obj.resolve(element_text)

    #         cached_field = self._cached_result.get(name, None)
    #         if cached_field is None:
    #             self._cached_result.setdefault(name, [])
    #             cached_field = self._cached_result.get(name)
    #         cached_field.append(resolved_value)
    #         self._cached_result.update({name: cached_field})

    def add_value(self, name, value):
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
        
        cached_field = self._cached_result.get(name, None)            
        if cached_field is None:
            self._cached_result.setdefault(name, [])
            cached_field = self._cached_result.get(name)
        cached_field.append(resolved_value)
        self._cached_result.update({name: cached_field})

    def resolve_fields(self):
        if self._cached_result:
            # Check that the arrays are
            # of equal length before running
            # the DataFrame otherwise it will
            # raise an error

            return pandas.DataFrame(
                self._cached_result, 
                columns=self._meta.cached_fields,
                # dtype=[]
            )
        return self._cached_result


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
        df = self.resolve_fields()
        if commit:
            if filename is None:
                filename = f'{secrets.token_hex(nbytes=5)}.json'
            else:
                if not filename.endswith('json'):
                    filename = f'{filename}.json'
            return df.to_json(filename, orient='records')
        return df.copy()    
