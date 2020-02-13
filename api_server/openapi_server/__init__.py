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

# if hasattr(config, 'TOKEN_SUBSCRIPTION_NAME'):
#    thread = Thread(target=car_locations_db_handler.read_topic)
#    thread.start()

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
        g.ip = request.headers.get('x-appengine-user-ip')

    logger = logging.getLogger('auditlog')
    auditlog_list = list(filter(None, [
        "Request Url: {}".format(request.url),
        "IP: {}".format(g.ip),
        "User-Agent: {}".format(request.headers.get('User-Agent')),
        "Response status: {}".format(response.status),
        "UPN: {}".format(g.user)
    ]))

    logger.info(' | '.join(auditlog_list))

    return response
