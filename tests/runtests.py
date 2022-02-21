import unittest

from zineb.tests.timings import test_simple_project_timing
from zineb.tests.models.test_models import TestSimpleModel, TestModelRegistery

if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    suite = unittest.TestSuite()
    suite.addTest(TestSimpleModel('test_model_in_iteration'))
    suite.addTest(TestModelRegistery('test_can_get_all_models'))
    runner.run(suite)

    test_simple_project_timing()
