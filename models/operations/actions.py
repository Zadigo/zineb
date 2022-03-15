class Action:
    method_name = None

    def __init__(self, field_name, value, field):
        self.model = None
        self.field_name = field_name
        self.value = value
        self.field = field


class AddValue(Action):
    method_name = 'add_value'
    
