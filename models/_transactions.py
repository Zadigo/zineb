import datetime
import secrets

from django.forms.widgets import Widget

class Transaction:
    """
    Represents the global transactions for a Model. The main
    purpose of a transaction is to be able to snapshot the
    specific state of a model at any point in time and  
    """
    REFERENCE = None
    GLOBAL_THREAD = {}
    model = None

    def __enter__(self, *execs):
        pass

    def __exit__(self):
        return False

    def __hash__(self):
        return hash(self.REFERENCE + self.model.__name__)

    @classmethod
    def _new(cls, model):
        cdate = datetime.datetime.now()
        instance = cls()
        cls.GLOBAL_THREAD.update(references=set())
        # new_reference = cls.generate_reference(cls)
        # new_reference = secrets.token_hex(5)
        # if new_reference in cls.references:
        #     new_reference = secrets.token_hex(5)

        instance.model = model
        new_reference = instance.generate_reference()
        instance.REFERENCE = new_reference
        attrs = (cdate.timestamp(), new_reference, instance)
        instance.GLOBAL_THREAD.get('references').add(attrs)
        return instance

    @property
    def references(self):
        return self.GLOBAL_THREAD.get('references', set())

    def generate_reference(self):
        new_reference = secrets.token_hex(5)
        if new_reference in self.references:
            new_reference = secrets.token_hex(5)
        return f'transaction-{new_reference}'

    def commit(self, model):
        cdate = datetime.datetime.now()
        reference = self.generate_reference()
        attrs = (cdate.timestamp(), reference, model)
        self.references.add(attrs)

    def rollback(self):
        """
        Rollback to the last known reference or
        model state
        """
        references = self.GLOBAL_THREAD.get('references')
        return references[-1]

    def savepoint(self):
        pass

    def save_model(self):
        """
        Save
        """
