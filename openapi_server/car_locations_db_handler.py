import json
import logging

from google.cloud import pubsub_v1, datastore

import config


def read_topic():
    client = pubsub_v1.SubscriberClient()
    subscription = client.subscription_path(config.TOPIC_PROJECT_ID,
                                            config.SUBSCRIPTION_NAME)
    db_client = datastore.Client()
    logging.info('Start pooling car locations')
    while True:
        response = client.pull(subscription, 10)
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
                    logging.info('Populate location {} - {}'.format(entity.key, entity))
                else:
                    logging.info('Skipping {} - late notification {}/{}'
                                 .format(mdata['token'], mdata['when'], entity['when']))
    pass
