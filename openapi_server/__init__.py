from threading import Thread

import connexion
from flask_cors import CORS

from openapi_server import encoder
from . import car_locations_db_handler

app = connexion.App(__name__, specification_dir='./openapi/')
app.app.json_encoder = encoder.JSONEncoder
app.add_api('openapi.yaml',
            arguments={'title': 'snbplanningtool'},
            pythonic_params=True)
CORS(app.app)


thread = Thread(target=car_locations_db_handler.read_topic)
thread.start()
