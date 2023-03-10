from flask import Flask, jsonify
from flask_cors import CORS

from zineb.settings import settings

app = Flask(__name__)
CORS(app, resources={r'/*': {'origins': 'http://localhost:8080/'}})


@app.route('/ping', methods=['GET'])
def ping_pong():
    return jsonify('pong!')


if __name__ == '__main__':
    app.run()
