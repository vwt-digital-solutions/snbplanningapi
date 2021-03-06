import logging
import os
import openapi_server

from cache import cache

from Flask_AuditLog import AuditLog
from Flask_No_Cache import CacheControl
from flask_sslify import SSLify

app = openapi_server.app

flask_app = app.app

logging.basicConfig(level=logging.INFO)

AuditLog(app)
CacheControl(app)
if 'GAE_INSTANCE' in os.environ:
    SSLify(app.app, permanent=True)

cache.init_app(flask_app)
