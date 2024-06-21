class Field:
    def __init__(self):
        self.field_name = None

    def _internal_type(self):
        return str 
    
    def update_form_fields(self, name, instance):
        pass

    def resolve(self, data):
        return self._internal_type(data[self.field_name])


class CharField(Field):
    def __init__(self):
        pass

