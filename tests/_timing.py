import time
import os
import subprocess

def calculate_time(func):
    def wrapper():
        start = time.time()
        func()
        end_result = round((time.time() - start), 2)
        print(f'Executed in {end_result} seconds.')
    return wrapper


@calculate_time
def test_timing_model_creation():
    from zineb.models.datastructure import Model
    from zineb.models import fields

    class TestModel(Model):
        name = fields.CharField()
        age = fields.IntegerField()

    _ = TestModel()


@calculate_time
def test_timing_datacontainer():
    from zineb.models.datastructure import DataContainer

    _ = DataContainer.as_container(*['name', 'age'])


@calculate_time
def test_timing_request():
    from zineb.http.request import HTTPRequest

    request = HTTPRequest('http://example.com')
    request._send()


@calculate_time
def test_simple_project_timing():
    os.environ.setdefault('ZINEB_SPIDER_PROJECT', 'zineb.tests.testproject.settings')

    cmd = ['python', os.path.join(os.path.dirname(__file__), 'testproject', 'manage.py'), 'start']
    subprocess.call(cmd, stderr=subprocess.STDOUT)

if __name__ == '__main__':
    test_simple_project_timing()
