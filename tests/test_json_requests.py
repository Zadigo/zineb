import unittest
import pandas
from zineb.http.request import JsonRequest

request = JsonRequest('https://matchstat.com/tennis/match-stats/m/23345521')
request._send()

class TestJsonRequest(unittest.TestCase):
    def test_response(self):
        self.assertIsInstance(request.json_response.raw_data, dict)
        
        df = request.json_response.get_response_from_key('stats')
        self.assertIsInstance(df, pandas.DataFrame)

if __name__ == "__main__":
    unittest.main()
