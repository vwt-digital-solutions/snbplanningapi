import logging
import os
import openapi_server

from Flask_AuditLog import AuditLog
from Flask_No_Cache import CacheControl
from flask_caching import Cache
from flask_sslify import SSLify

app = openapi_server.app

flask_app = app.app

logging.basicConfig(level=logging.INFO)

AuditLog(app)
CacheControl(app)
if 'GAE_INSTANCE' in os.environ:
    SSLify(app.app, permanent=True)


cache_config = {
    "CACHE_TYPE": "simple",
    "CACHE_DEFAULT_TIMEOUT": 300
}

cache = Cache(config=cache_config)

cache.init_app(flask_app)
