from functools import cached_property, lru_cache

from zineb.exceptions import ForeignKeyError


class BaseRelationship:
    model = None
    related_model = None

    def __init__(self):
        self.is_one_to_one = True
        self._model_container = []
        self._related_model_fields = {}
        self._related_models = {}
        self._related_field_names = []
        self._related_models_data_containers = {}

    def __repr__(self):
        class_name = self.__class__.__name__
        if self.is_one_to_one:
            return f'<{class_name}({self.model._meta.model_name} [1 -> 1] {self.related_model._meta.model_name})>'
        return f'<{class_name}({self.model._meta.model_name} [1 -> x] {self.related_model._meta.model_name})>'

    def update_relationship_options(self, model):
        from zineb.models.datastructure import Model
        if not isinstance(model, Model):
            raise ValueError()

        related_model_fields = model._meta.related_model_fields
        # The model has not related_model_fields,
        # we know by definition that this model
        # has not relationships
        if not related_model_fields:
            raise ValueError("The model does not have any relationship fields")

        # A Model can have multiple RelatedModel fields,
        # so we need to keep track of all of them by
        # destructuring certain parameters for the class
        self._related_model_fields = related_model_fields
        for key, field in self._related_model_fields.items():
            related_model = field.related_model
            self._related_models[key] = related_model
            self._related_models_data_containers[key] = related_model._data_container
            self._related_field_names.append(key)

        self.model = model
        self._model_container = model._data_container

    def get_related_item(self, field_name, item_id):
        related_model = self._related_models[field_name]
        result = list(
            filter(
                lambda x: x['id'] == item_id, 
                related_model._data_container.as_list()
            )
        )
        if len(result) == 0:
            raise ForeignKeyError(
                field_name, 
                related_model._meta.verbose_name
            )
        return result[-1]

    def enforce_constraint(self):
        pass

    def resolve_relationships(self):
        pass


class OneToOneRelationship(BaseRelationship):
    def enforce_constraint(self, for_value):
        # In a one to one relationship,
        # a value can be added to the related
        # model only if the ID also exists on
        # on the related model e.g. 1 <-> 1
        model_ids = self.model._data_container.get_container('id')
        related_model_ids = self._related_model_container.get_container('id')
        if for_value not in model_ids and for_value not in related_model_ids:
            raise ValueError()

    @lru_cache(maxsize=5)
    def resolve_relationships(self):
        resolved_items = []
        # Resolve the relationship between one or
        # multiple models by matching the identical
        # ID of the model to its related model
        for item in self._model_container.as_list():
            for key in self._related_field_names:
                related_item = self.get_related_item(key, item['id'])
                item[key] = related_item
            resolved_items.append(item)
        return resolved_items


class ManyToManyRelationship(BaseRelationship):
    def __init__(self):
        super().__init__()
        self.is_one_to_one = False
