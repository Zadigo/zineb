import inspect
import unittest

from zineb.tests.models import test_fields
from zineb.tests.models.test_models import TestModel
# from zineb.tests.timings import test_simple_project_timing

def get_test_functions(test_class):
    methods = []
    instance = test_class()
    for i, method in enumerate(inspect.getmembers(instance, inspect.ismethod)):
        name, item = method
        if name.startswith('test_'):
            if not callable(item):
                print(f"{i}. Skipping method {method} for {instance}")
                continue
            methods.append(name)
    return methods


def add_to_suite(suite, methods):
    for method in methods:
        suite.addTest(method)


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    suite = unittest.TestSuite()
    
    # e.g. suite.addTest(TestModel('test_can_add_value'))
    
    # Fields
    add_to_suite(suite, get_test_functions(test_fields.TestField))
    # add_to_suite(suite, get_test_function(test_fields.TestCharfields))
    # add_to_suite(suite, get_test_function(test_fields.TestBooleanField))
    # add_to_suite(suite, get_test_function(test_fields.TestCommaSeparatedField))
    # add_to_suite(suite, get_test_function(test_fields.TestValueField))
    
    # Models
    # add_to_suite(suite, get_test_function(TestModel))
        
    
    runner.run(suite)

    # test_simple_project_timing()
