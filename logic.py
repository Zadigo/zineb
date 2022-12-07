import itertools
import os
import re

import pyaml
import yaml

from zineb.http.request import HTTPReques²

FUNCTIONS_REGEX = re.compile(
    r"^if (?P<lhs>\w+) (?P<operator>[\<\>] (?P<rhs>\w+) then (?P<method1>\w+))"
)


class Logic:
    def __init__(self, filename):
        self.pipeline = []
        with open('./tests/logic.yaml') as f:
            self.config = yaml.load(f, Loader=yaml.SafeLoader)
        self.jobs = self.config.get('jobs', {})
        self.workflows = self.config.get('workflows', {})['jobs']

    @property
    def get_pipeline(self):
        return list(self.pipeline)

    def get_workflow(self, name):
        pass

    def build_logic(self, using_workflow=None):
        workflow = self.jobs[using_workflow]
        goto = self.map_goto(workflow)
        actions = self.map_actions(workflow)
        self.pipeline = itertools.chain(goto, actions)
        # print(list(actions))

    @staticmethod
    def map_goto(workflow):
        response = 0
        value = workflow['goto']
        for item in value:
            url = item.get('url', None)
            ping = item.get('ping', False)
            on_sucess = item.get('ping_success', 'stop')

            if url is None:
                break

            instance = HTTPRequest(url)

            if ping:
                response = os.system(f"ping -c 1 {url}")

                if response != 0 and on_sucess == 'stop':
                    break

            yield instance, response

    @staticmethod
    def map_actions(workflow):
        actions = workflow['actions']
        get_actions = actions.get('get', {})
        follow_actions = actions.get('follow', {})

        items = get_actions['tag']
        for item in items:
            yield tuple(item.values())


l = Logic('logic.yaml')
a = l.build_logic(using_workflow='workflow_a')
print(l.get_pipeline)
