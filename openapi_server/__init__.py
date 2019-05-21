from threading import Thread

import connexion
from flask_cors import CORS
from flask import request
from flask import g

import config
import logging
import sys
from pythonjsonlogger import jsonlogger

from openapi_server import encoder
from . import car_locations_db_handler
from . import workitems_db_handler

handler = logging.StreamHandler(sys.stdout)
formatter = jsonlogger.JsonFormatter()
handler.setFormatter(formatter)
root_logger = logging.getLogger()
root_logger.setLevel(level=logging.INFO)
root_logger.addHandler(handler)

app = connexion.App(__name__, specification_dir='./openapi/')
app.app.json_encoder = encoder.JSONEncoder
app.add_api('openapi.yaml',
            arguments={'title': 'snbplanningtool'},
            pythonic_params=True)
CORS(app.app)

if hasattr(config, 'TOKEN_SUBSCRIPTION_NAME'):
    thread = Thread(target=car_locations_db_handler.read_topic)
    thread.start()

if hasattr(config, 'WORKITEMS_SUBSCTIPTION_NAME'):
    thread = Thread(target=workitems_db_handler.read_topic)
    thread.start()

@app.app.before_request
def before_request():
    g.user = ''
    g.ip = ''

@app.app.after_request
def after_request_callback( response ):
    root_logger.info(' | '.join([
        request.url,
        g.ip,
        request.headers.get('User-Agent'),
        response.status,
        g.user
    ]))

    return response
