import unittest

from zineb.http.user_agent import UserAgent


class TestUserAgent(unittest.TestCase):
    def setUp(self):
        self.agents = UserAgent()

    def test_user_loading(self):
        self.assertTrue(self.agents.has_agents)
        self.assertIsNone(self.agents.current_agent)


if __name__ == '__main__':
    unittest.main()
