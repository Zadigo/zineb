import unittest
import pandas
from zineb.http.request import JsonRequest
from zineb.tests import create_test_json_request

# request = JsonRequest('https://matchstat.com/tennis/match-stats/m/23345521')
# request._send()

request = create_test_json_request()

class TestJsonRequest(unittest.TestCase):
    def test_response(self):
        self.assertIsInstance(request.json_response.raw_data, (dict, list))
        
        df = request.json_response.response_data
        self.assertIsInstance(df, pandas.DataFrame)
        # df = request.json_response.get_response_from_key('stats')
        

if __name__ == '__main__':
    unittest.main()
