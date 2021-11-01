# import unittest

# from zineb.models.functions import (Add, Divide, ExtractDay, ExtractMonth,
#                                     ExtractYear, Multiply, Substract, When)
# from zineb.tests.models import BareModel

# # class TestModel(Model):
# #     age = IntegerField()

# model = BareModel()

# class TestMathFunctions(unittest.TestCase):
#     def setUp(self):
#         self.values = [18]

#     def test_addition(self):
#         for value in self.values:
#             model.add_calculated_value('age', value, Add(1))
#             self.assertDictEqual(model, {'age': [19]})
    
#     def test_substraction(self):
#         for value in self.values:
#             model.add_calculated_value('age', value, Substract(1))
#             self.assertDictEqual(model, {'age': [19]})


# class TestWhenFunction(unittest.TestCase):
#     def setUp(self):
#         self.when = When('age__gt=15', 11)

#     def test_resolution(self):
#         model.add_case(18, self.when)
#         self.assertDictEqual(model._cached_result.as_values(), {'age': [11]})


# class TestExtractDates(unittest.TestCase):
#     def setUp(self) -> None:
#         return super().setUp()



# if __name__ == '__main__':
#     unittest.main()
