import unittest

import pandas
from models.fields import (AgeField, CharField, DateField, FunctionField,
                           ImageField, IntegerField, NameField, UrlField)
from zineb.http.request import HTTPRequest
from zineb.models.datastructure import Model

request = HTTPRequest('http://example.com')
request._send()

class Player(Model):
    name = NameField()


def custom_function(value):
    return value + 100


class Celebrity(Model):
    firstname = NameField()
    lastname = CharField()
    birthdate = DateField('%d/%m/%Y')
    age = AgeField('%d/%m/%Y')
    url = UrlField()
    height = IntegerField()
    weight = IntegerField()
    spike = FunctionField(
        custom_function,
        output_field=IntegerField(),
    )
    block = FunctionField(
        custom_function,
        output_field=IntegerField()
    )
    

class TestModel(unittest.TestCase):
    def setUp(self):
        self.player = Player(response=request.html_response)

    def test_adding_value(self):
        self.player.add_value('name', 'Kendall Jenner')

    # def test_adding_expression(self):
    #     self.player.add_expression('name', 'h1')
    #     # self.assertIsInstance(self.player._cached_result, dict)
    #     # self.assertIsInstance(self.player._cached_result[-1], dict)
    #     # Testing the data itself
    #     # self.assertEqual(self.player._cached_result[0]['name'], 'Example Domain')
    #     # self.assertListEqual(self.player._cached_result, [{'name': 'Example Domain'}])

    @unittest.expectedFailure
    def test_cannot_add_non_existing_field(self):
        # Normally we should not be able to add
        # a field that is not present on the model
        self.player.add_value('age', 'h1')

    def test_non_existing_field_error(self):
        with self.assertRaises(KeyError) as context:
            self.player.add_value('age', 'h1')

    @unittest.expectedFailure
    def test_cannot_add_different_value(self):
        self.player.add_value('name', 1)


class TestComplexModels(unittest.TestCase):
    def setUp(self):
        self.model = Celebrity(response=request._http_response)

    def test_birthdate_field(self):
        self.model.add_value('age', '3/6/1996')


if __name__ == "__main__":
    unittest.main()
