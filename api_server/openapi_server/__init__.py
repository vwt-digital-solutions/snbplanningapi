import logging
import os

import config

import connexion
from flask_cors import CORS
from flask import request
from flask import g

from openapi_server import encoder

logging.basicConfig(level=logging.INFO)

app = connexion.App(__name__, specification_dir='./openapi/')
app.app.json_encoder = encoder.JSONEncoder
app.add_api('openapi.yaml',
            arguments={'title': 'SNBPlanning API'},
            pythonic_params=True,
            validate_responses=True
)
if 'GAE_INSTANCE' in os.environ:
    CORS(app.app, origins=config.ORIGINS)
else:
    CORS(app.app)


@app.app.before_request
def before_request():
    g.user = ''
    g.ip = ''


@app.app.after_request
def after_request_callback(response):
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
