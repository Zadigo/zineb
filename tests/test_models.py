import unittest
from collections import OrderedDict

import pandas
from models import fields
from zineb.http.request import HTTPRequest
from zineb.models.datastructure import Model

request = HTTPRequest('http://example.com')
request._send()

class Player(Model):
    name = fields.NameField()


def custom_function(value):
    return value + 100


class Celebrity(Model):
    firstname = fields.NameField()
    lastname = fields.CharField()
    birthdate = fields.DateField('%d/%m/%Y')
    age = fields.AgeField('%d/%m/%Y')
    url = fields.UrlField()
    height = fields.IntegerField()
    weight = fields.IntegerField()
    spike = fields.FunctionField(
        custom_function,
        output_field=fields.IntegerField(),
    )
    block = fields.FunctionField(
        custom_function,
        output_field=fields.IntegerField()
    )
    

class TestModel(unittest.TestCase):
    def setUp(self):
        self.player = Player(response=request.html_response)

    def test_fields(self):
        self.assertIsInstance(self.player._fields.cached_fields, OrderedDict)
        self.assertTrue(self.player._fields.cached_fields)
        self.assertIn('name', self.player._fields.cached_fields)

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

    def test_iteration(self):
        # When adding multiple values to the model,
        # for whatever reasons the _validators variable
        # gets populated multiple times with validators
        self.player.add_value('name', 'Kendall Jenner')
        self.player.add_value('name', 'Hailey Baldwin')

        name_instance = self.player._get_field_by_name('name')
        self.assertEqual(len(name_instance._validators), 0)

    def test_field_type(self):
        name_instance = self.player._get_field_by_name('name')
        self.assertIsInstance(name_instance, fields.Field)

    def test_field_cache(self):
        self.assertEqual(len(self.player._fields.cached_fields), 1)


class TestComplexModels(unittest.TestCase):
    def setUp(self):
        self.model = Celebrity(response=request._http_response)

    def test_birthdate_field(self):
        self.model.add_value('age', '3/6/1996')


if __name__ == "__main__":
    unittest.main()
