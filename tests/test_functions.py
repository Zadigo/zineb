from zineb.models.datastructure import Model
from zineb.models.functions import (Add, Divide, ExtractDay, ExtractMonth,
                                    ExtractYear, Multiply, Substract)
import unittest
from zineb.models.fields import IntegerField
from zineb.models.shortcuts import inline_model

class TestModel(Model):
    age = IntegerField()

model = TestModel()

class TestFunctions(unittest.TestCase):
    def test_addition(self):
        model.add_calculated_value('age', 18, Add(1))
        self.assertCountEqual(model, {'age': [19]})

if __name__ == '__main__':
    unittest.main()
