import json
import logging
import datetime
import pytz

from google.cloud import pubsub_v1, datastore
from google.api_core import exceptions
import googlemaps

import config


def read_topic():
    client = pubsub_v1.SubscriberClient()
    db_client = datastore.Client()
    if hasattr(config, 'GEO_API_KEY'):
        gmaps = googlemaps.Client(key=config.GEO_API_KEY)
    subscription = client.subscription_path(config.TOPIC_PROJECT_ID,
                                            config.WORKITEMS_SUBSCTIPTION_NAME)
    logging.info('Start polling work items')
    while True:
        try:
            response = client.pull(subscription, 10)
        except exceptions.DeadlineExceeded:
            continue

        ack_ids = []
        for message in response.received_messages:
            mdata = json.loads(message.message.data)
            payload = mdata['data']
#            try:
            when = datetime.datetime.strptime(mdata['when'], '%Y-%m-%dT%H:%M:%S%z')
#            except:
#               when = datetime.datetime.strptime(mdata['when'], '%Y-%m-%dT%H:%M:%S').astimezone(pytz.utc)
            loc_key = db_client.key('WorkItem', payload['L2GUID'])
            entity = db_client.get(loc_key)
            if entity is None:
                entity = datastore.Entity(key=loc_key)
            if 'last_updated' not in entity or entity['last_updated'] < when:
                payload['last_updated'] = when
                if payload['end_timestamp']:
                    payload['end_timestamp'] = datetime.datetime.strptime(payload['end_timestamp'],
                                                                      '%d-%m-%Y %H:%M:%S').astimezone(pytz.utc)
                if payload['start_timestamp']:
                    payload['start_timestamp'] = datetime.datetime.strptime(payload['start_timestamp'],
                                                                        '%d-%m-%Y %H:%M:%S').astimezone(pytz.utc)
                if hasattr(config, 'GEO_API_KEY') and (payload['status'] in ['Te Plannen', 'Gepland', 'Niet Gereed']):
                    location = None
                    # Add extra object to the json to check whether it has already tried
                    # to geocode this location
                    # If this object is true, don't geocode
                    if 'isGeocoded' not in entity:
                        entity.update({
                            "isGeocoded": False
                        })
                    if (entity['isGeocoded'] == False):
                        if 'geometry' not in entity:
                            if 'zip' in payload and payload['zip'] != '':
                                postcode = ''.join([ch for ch in payload['zip'] if ch != ' '])
                                location = gmaps.geocode(postcode)
                            elif 'city' in payload and payload['city'] != '':
                                address = payload['city'] + ',Nederlands'
                                if 'street' in payload and payload['street'] != '':
                                    address = payload['street'] + ',' + address
                                location = gmaps.geocode(address)
                        if location:
                            entity.update({
                                "geometry": {
                                    "type": "Point",
                                    "coordinates": [
                                        location[0]['geometry']['location']['lng'],
                                        location[0]['geometry']['location']['lat']
                                    ]
                                }
                            })
                        entity.update({
                            "isGeocoded": True
                        })
                entity.update(payload)
                db_client.put(entity)
                logging.debug('Populate work item {} - {}'.format(entity.key, entity))
            else:
                logging.debug('Skipping {} - late notification {}/{}'
                             .format(payload, when, entity['last_updated']))
            ack_ids.append(message.ack_id)
        if ack_ids:
            client.acknowledge(subscription, ack_ids)
    pass


if __name__ == '__main__':
    read_topic()
