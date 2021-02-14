import yaml
from zineb.models.datastructure import Model


class Automate:
    tasks = []

    def __init__(self, path, response, model:Model, fields:list):
        with open(path, 'r') as f:
            self.model = model
            self.field = fields

            file = yaml.load(f, Loader=yaml.FullLoader)
            spider = file.get('spider', None)
            if spider is None:
                raise KeyError('Your Yaml file should start with a spider declaration')

            self.spider = spider
            self.register_tasks()
            for field in fields:
                for task in self.tasks:
                    model.add_expression(field, task, many=True)

    @property
    def get_model(self):
        return self.model

    def register_tasks(self):
        tasks = self.spider.get('tasks', [])
        self.tasks.extend(tasks)
