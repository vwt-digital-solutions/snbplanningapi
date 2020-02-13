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
            if 'carlocations' in mdata:
                for carloc in mdata['carlocations']:
                    update_carlocation(db_client, carloc)
            elif 'token' in mdata:
                update_carlocation(db_client, mdata)
            ack_ids.append(message.ack_id)
        if ack_ids:
            client.acknowledge(subscription, ack_ids)


def update_carlocation(db_client, carloc):
    loc_key = db_client.key('CarLocation', carloc['token'])
    entity = db_client.get(loc_key)
    if entity is None:
        entity = datastore.Entity(key=loc_key)
    if 'when' not in entity or entity['when'] < carloc['when']:
        entity.update({
            "geometry": carloc['geometry'],
            "when": carloc['when']
        })
        db_client.put(entity)
        logging.debug('Populate location {} - {}'.format(entity.key, entity))
    else:
        logging.debug('Skipping {} - late notification {}/{}'
                      .format(carloc['token'], carloc['when'], entity['when']))
