from zineb.app import Spider
from zineb.models import fields, functions
from zineb.models.datastructure import Model

# class SuperModel(Model):
#     class Meta:
#         template_model = True


class GreatModel(Model):
    lastname = fields.CharField()


class SomeModel(Model):
    title = fields.CharField()
    # content = fields.TextField()
    # emails = fields.IntegerField()
    # date_of_birth = fields.DateField()
    # firstname = fields.NameField()
    # data = fields.JsonField()
    # linkedin = fields.URLField()
    # email = fields.EmailField()
    # domains = fields.ListField()
    # restaurant = fields.RegexField(r'^(restaurant)\-google')
    # other_value = fields.CharField()
    lastnames = fields.RelatedModel(GreatModel)


class MySpider(Spider):
    start_urls = ['http://example.com']

    def start(self, response, request, **kwargs):
        title = response.find('h1')
        content = response.find('p')
        model = SomeModel()
        # model.add_value('title', title.text)
        # model.add_value('content', content.text)
        # model.add_value('firstname', 'julie')
        # model.add_value('linkedin', 'http://example.com')
        # model.add_value('restaurant', 'restaurant-google')
        # model.add_value('date_of_birth', '1987-1-1')
        # model.add_value('data', {'height': 175})
        # model.add_value('domains', [1, 2, 3])
        # model.add_value('email', 'email@gmail.com')
        # model.add_value('emails', 1)
        # model.add_calculated_value('emails', 1, functions.Substract(1))
        # model.add_value('restaurant', 'restaurant-google')
        # model.add_case('enterprise', functions.When(
        #     'other_value__eq=enterprise', 'startup'))

        model.add_value('title', 'Kendall')
        model.lastnames.add_value('lastname', 'Marion')
        model.add_value('title', 'Kylie')
        print(model)


if __name__ == '__main__':
    spider = MySpider()
