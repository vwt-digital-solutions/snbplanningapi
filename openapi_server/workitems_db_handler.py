import json
import logging
import datetime
import pytz

from google.cloud import pubsub_v1, datastore
from google.api_core import exceptions

import config


def read_topic():
    client = pubsub_v1.SubscriberClient()
    db_client = datastore.Client()
    subscription = client.subscription_path(config.TOPIC_PROJECT_ID,
                                            config.WORKITEMS_SUBSCTIPTION_NAME)
    logging.info('Start pooling work items')
    while True:
        try:
            response = client.pull(subscription, 10)
        except exceptions.DeadlineExceeded:
            continue

        ack_ids = []
        for message in response.received_messages:
            mdata = json.loads(message.message.data)
            payload = mdata['data']
            try:
                when = datetime.datetime.strptime(mdata['when'], '%Y-%m-%dT%H:%M:%S%z')
            except:
                when = datetime.datetime.strptime(mdata['when'], '%Y-%m-%dT%H:%M:%S').astimezone(pytz.utc)
            loc_key = db_client.key('WorkItem', payload['L2GUID'])
            entity = db_client.get(loc_key)
            if entity is None:
                entity = datastore.Entity(key=loc_key)
            if 'last_updated' not in entity or entity['last_updated'] < when:
                payload['last_updated'] = when
                payload['EindDatumTijd'] = datetime.datetime.strptime(payload['EindDatumTijd'],
                                                                      '%d-%m-%Y %H:%M:%S').astimezone(pytz.utc)
                payload['StartDatumTijd'] = datetime.datetime.strptime(payload['StartDatumTijd'],
                                                                       '%d-%m-%Y %H:%M:%S').astimezone(pytz.utc)
                entity.update(payload)
                db_client.put(entity)
                logging.info('Populate work item {} - {}'.format(entity.key, entity))
            else:
                logging.info('Skipping {} - late notification {}/{}'
                             .format(payload, when, entity['last_updated']))
            ack_ids.append(message.ack_id)
        if ack_ids:
            client.acknowledge(subscription, ack_ids)
    pass


if __name__ == '__main__':
    read_topic()
