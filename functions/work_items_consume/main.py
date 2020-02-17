import base64
import googlemaps
import json
import logging

import config
from dbprocessor import DBProcessor

parser = DBProcessor()


def topic_to_datastore(request):
    gmaps = None
    if hasattr(config, 'GEO_API_KEY'):
        gmaps = googlemaps.Client(key=config.GEO_API_KEY)

    # Extract data from request
    envelope = json.loads(request.data.decode('utf-8'))

    payload = base64.b64decode(envelope['message']['data'])

    # Extract subscription from subscription string
    try:
        envelope = {
            'subscription': 'test_subscription'
        }
        subscription = envelope['subscription'].split('/')[-1]
        logging.info(f'Message received from {subscription} [{payload}]')

        parser.process(json.loads(payload), gmaps)

    except Exception as e:
        logging.info('Extract of subscription failed')
        logging.debug(e)
        raise e

    # Returning any 2xx status indicates successful receipt of the message.
    # 204: no content, delivery successfull, no further actions needed
    return 'OK', 204


topic_to_datastore(None)
