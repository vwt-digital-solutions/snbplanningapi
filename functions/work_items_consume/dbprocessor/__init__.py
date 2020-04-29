import logging
import dateutil.parser

from google.cloud import datastore


class DBProcessor(object):

    def __init__(self, client):
        self.client = client

    def process(self, payload, gmaps):
        when = dateutil.parser.isoparse(payload['when'])

        work_item = payload['data']
        work_item_entity = self.get_work_item(work_item, when, gmaps)

        if work_item_entity is not None:
            self.client.put(work_item_entity)

    def get_work_item(self, work_item, when, gmaps):
        if 'id' not in work_item:
            loc_key = self.client.key('WorkItem', work_item['L2GUID'])
        else:
            loc_key = self.client.key('WorkItem', work_item['id'])
        entity = self.client.get(loc_key)

        if work_item.get('status') not in ['Te Plannen', 'Gepland', 'Niet Gereed']:
            # Remove inactive work from DataStore
            if entity:
                self.client.delete(loc_key)
            return None
        elif not entity or entity['last_updated'] < when:
            if entity is None:
                entity = datastore.Entity(key=loc_key)
            work_item['last_updated'] = when
            return self.update_db_workitem(entity, gmaps, work_item)
        else:
            logging.debug('Skipping {} - late notification {}/{}'
                          .format(work_item, when, entity['last_updated']))

            return None

    @staticmethod
    def update_db_workitem(entity, gmaps, work_item):
        if work_item['end_timestamp']:
            work_item['end_timestamp'] = dateutil.parser.isoparse(work_item['end_timestamp'])
        if work_item['start_timestamp']:
            work_item['start_timestamp'] = dateutil.parser.isoparse(work_item['start_timestamp'])
        if work_item['resolve_before_timestamp']:
            work_item['resolve_before_timestamp'] = dateutil.parser.isoparse(work_item['resolve_before_timestamp'])
        if gmaps is not None:
            location = None
            # Add extra object to the json to check whether it has already tried
            # to geocode this location
            # If this object is true, don't geocode
            if 'isGeocoded' not in entity:
                entity.update({
                    "isGeocoded": False
                })
            if not entity['isGeocoded']:
                if 'geometry' not in entity:
                    if 'zip' in work_item and work_item['zip'] != '':
                        postcode = ''.join([ch for ch in work_item['zip'] if ch != ' '])
                        location = gmaps.geocode(postcode)
                    elif 'city' in work_item and work_item['city'] != '':
                        address = work_item['city'] + ',Nederlands'
                        if 'street' in work_item and work_item['street'] != '':
                            address = work_item['street'] + ',' + address
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

        entity.update(work_item)
        logging.debug('Populate work item {} - {}'.format(entity.key, entity))
        return entity
