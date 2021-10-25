class RelatedField:
    pass


class ForeignKey(RelatedField):
    """A special field used to create forward and
    backward relation with a model"""

    def __init__(self, model, parent):
        self.model = model
        self.parent = parent
