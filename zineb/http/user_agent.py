import gzip
import random
from functools import cached_property

from zineb.settings import settings


class UserAgent:
    def __init__(self):
        # user_agents_file = settings.GLOBAL_ZINEB_PATH / 'http/user_agents.rar'
        # print(user_agents_file)
        # content = gzip.open(user_agents_file)
        self.agents = self.get_user_agents
        self.current_agent = None

    @cached_property
    def get_user_agents(self):
        user_agents_file = settings.GLOBAL_ZINEB_PATH + '/http/user_agents.txt'
        with open(user_agents_file, mode='r') as f:
            agents = [_.strip() for _ in f.readlines()]
            # Save the current list of user agents
            # to the settings as cache mechanism
            settings.USER_AGENTS = agents
        return agents
    
    @property
    def has_agents(self):
        return len(self.get_user_agents) > 0

    def get_random_agent(self):
        """
        Get a random user agent from a list of agents
        """
        user_agents_from_settings = settings.get('USER_AGENTS', [])
        self.agents.extend(user_agents_from_settings)
        random.shuffle(self.agents)
        self.current_agent = random.choice(list(set(self.agents)))
        return self.current_agent


# TODO: RotatingProxy
