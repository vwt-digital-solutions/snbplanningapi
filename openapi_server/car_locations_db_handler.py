import json
import logging

from google.cloud import pubsub_v1, datastore
from google.api_core import exceptions

import config


def read_topic():
    client = pubsub_v1.SubscriberClient()
    db_client = datastore.Client()
    subscription = client.subscription_path(config.TOPIC_PROJECT_ID,
                                            config.TOKEN_SUBSCRIPTION_NAME)
    logging.info('Start polling car locations')
    while True:
        try:
            response = client.pull(subscription, 10)
        except exceptions.DeadlineExceeded:
            continue

        ack_ids = []
        for message in response.received_messages:
            mdata = json.loads(message.message.data)
            if 'token' in mdata:
                loc_key = db_client.key('CarLocation', mdata['token'])
                entity = db_client.get(loc_key)
                if entity is None:
                    entity = datastore.Entity(key=loc_key)
                if 'when' not in entity or entity['when'] < mdata['when']:
                    entity.update({
                        "geometry": mdata['geometry'],
                        "when": mdata['when']
                    })
                    db_client.put(entity)
                    logging.debug('Populate location {} - {}'.format(entity.key, entity))
                else:
                    logging.debug('Skipping {} - late notification {}/{}'
                                 .format(mdata['token'], mdata['when'], entity['when']))
            ack_ids.append(message.ack_id)
        if ack_ids:
            client.acknowledge(subscription, ack_ids)
    pass
