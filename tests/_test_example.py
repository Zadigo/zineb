# from zineb.app import Zineb
# from zineb.models.datastructure import Model
# from zineb.models import fields
# from zineb.http.pipelines import CallBack


# class ExampleModel(Model):
#     title = fields.CharField(max_length=50)


# class Example(Zineb):
#     start_urls = ['http://example.com']

#     def start(self, response, **kwargs):
#         model = ExampleModel()
        
#         request = kwargs.get('request')
#         link = response.html_page.find('a').attrs.get('href')
#         return CallBack(link, self.parse_title)

#     def parse_title(self):
#         pass

# example = Example()



from models.fields import CommaSeperatedField
from zineb.models.fields import IntegerField
from zineb.models.datastructure import Model
from zineb.models.fields import CharField, ArrayField

# class Kendall(Model):
#     name = CharField(max_length=150)
#     age = IntegerField(min_value=15, max_value=50)

#     class Meta:
#         other_options = None
