from threading import Thread

import connexion
from flask_cors import CORS
from flask import request
from flask import g

import os
import config
import logging

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

@app.app.before_request
def before_request():
    g.user = ''
    g.ip = ''

@app.app.after_request
def after_request_callback( response ):
    if 'x-appengine-user-ip' in request.headers:
        logger.info('x-appengine-user-ip', request.headers.get('x-appengine-user-ip'))
        g.ip = request.headers.get('x-appengine-user-ip')
    elif 'X-Real-IP' in request.headers:
        logger.info('X-Real-IP', request.headers.get('X-Real-IP'))
        g.ip = request.headers.get('X-Real-IP')
    elif 'HTTP_X_REAL_IP' in os.environ:
        logger.info('HTTP_X_REAL_IP', request.headers.get('HTTP_X_REAL_IP'))
        g.ip = os.environ["HTTP_X_REAL_IP"]

    logger = logging.getLogger('auditlog')
    auditlog_list = list(filter(None, [
        request.url,
        g.ip,
        request.headers.get('User-Agent'),
        response.status,
        g.user
    ]))

    logger.info(' | '.join(auditlog_list))

    return response
