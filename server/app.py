import json
import os
from zineb.server.serializers import SPIDER_TYPES

import flask
import subprocess
from flask import Flask, request
from flask.templating import render_template
from rest_framework.response import Response as RestResponse
from flask.wrappers import Response
from zineb.server.serializers import ValidateSpiderCreation
from zineb.settings import settings


app = Flask(__name__)


@app.route('/api/v1/settings', methods=['get'])
def global_settings(**kwargs):
    response = {
        'LOG_TO_FILE': settings.LOG_TO_FILE,
        'SPIDERS': [
            {
                'name': 'MySpider',
                'last_execution': '2020-01-11'
            },
            {
                'name': 'SomeSpider',
                'last_execution': '2020-01-11'
            }
        ]
    }
    return response


@app.route('/api/v1/spiders', methods=['get', 'post'])
def spiders(**kwargs):
    if request.method == 'POST':
        spider_name = request.json.get('name', None)
        spider_type = request.json.get('spider_type', None)
        true_type = list(filter(lambda x: spider_type in x, SPIDER_TYPES))
        if len(true_type) > 0:
            # Create new spider here
            items = spider_name.split(' ')
            if len(items) > 1:
                items = map(lambda x: x.title(), items)
                name = ', '.join(items)
            else:
                name = spider_name.title()
            # TODO: Create spider
            return {'SPIDERS': [{'name': spider_name, 'last_execution': '2021-1-1'}]}, 201
        else:
            return Response('Spider type is not valid', 404,  mimetype='application/json')
    
    if request.method == 'GET':
        return Response(settings.SPIDERS, status=200, mimetype='application/json')


@app.route('/', methods=['get', 'post'])
def index(**kwargs):
    return render_template('index.html', name='index')


if __name__ == '__main__':
    app.run(debug=True)
