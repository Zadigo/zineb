import unittest

from models.fields import IntegerField
from zineb.models.fields import Function


class TestFunction(unittest.TestCase):
    def setUp(self):
        def custom_method(value):
            return value + 1

        self.field = Function(
            IntegerField(),
            custom_method
        )

    def test_field_result(self):
        result = self.field.resolve(10)
        self.assertEqual(result, 11)

if __name__ == "__main__":
    unittest.main()
