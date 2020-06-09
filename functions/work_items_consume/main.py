import base64
import json
import logging
import config
import googlemaps

from google.cloud import datastore
from dbprocessor import DBProcessor


client = datastore.Client()
parser = DBProcessor(client)


def topic_to_datastore(request):
    gmaps = None
    if hasattr(config, 'GEO_API_KEY'):
        gmaps = googlemaps.Client(key=config.GEO_API_KEY)

    # Extract data from request
    envelope = json.loads(request.data.decode('utf-8'))
    payload = base64.b64decode(envelope['message']['data'])

    # Extract subscription from subscription string
    try:
        subscription = envelope['subscription'].split('/')[-1]
        logging.info(f'Message received from {subscription}')
        parser.process(json.loads(payload), gmaps)
    except Exception:
        logging.exception('Extract of subscription failed')

    # Returning any 2xx status indicates successful receipt of the message.
    # 204: no content, delivery successfull, no further actions needed
    return 'OK', 204
