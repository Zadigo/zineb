class Migrations:
    # Indicates migration fileson which
    # a migration file depends on
    dependencies = []
    initial = False
    actions = []
    model_options = []

    def __init__(self, name):
        self.name = name

    def __hash__(self):
        return hash(self.name)

    def apply(self):
        for action in self.actions:
            pass

    def get_name(self):
        if self.initial:
            return 'initial'
        return 'rand_migration_name'
