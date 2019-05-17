from threading import Thread

import connexion
from flask_cors import CORS
from flask import request
from flask import g

import config
import logging
import json

from openapi_server import encoder
from . import car_locations_db_handler
from . import workitems_db_handler

logging.basicConfig(level=logging.INFO)

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

@app.app.after_request
def after_request_callback( response ):
    user = '' if g.user is None else g.user

    logging.info(' | '.join([
        request.url,
        request.remote_addr,
        request.headers.get('User-Agent'),
        response.status,
        user
    ]))

    return response
