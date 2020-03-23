from google.cloud import datastore
import logging


class DBProcessor(object):
    def __init__(self):
        self.client = datastore.Client()
        pass

    def process(self, payload):
        batch = self.client.batch()
        batch.begin()

        for car_location in payload['carlocations']:
            car_location_entity = self.get_car_location(car_location)

            # Check if get_car_location returned an entity.
            if car_location_entity is not None:
                batch.put(car_location_entity)

        batch.commit()

    def get_car_location(self, car_location):
        loc_key = self.client.key('CarLocation', car_location['token'])
        entity = self.client.get(loc_key)
        if entity is None:
            entity = datastore.Entity(key=loc_key)
        if 'when' not in entity or entity['when'] < car_location['when']:
            entity.update({
                "geometry": car_location['geometry'],
                "when": car_location['when'],
                "status": car_location.get('what', None),
                "license": car_location.get('license', None)
            })
            return entity
            logging.debug('Populate location {} - {}'.format(entity.key, entity))
        else:
            logging.debug('Skipping {} - late notification {}/{}'
                          .format(car_location['token'], car_location['when'], entity['when']))

            return None
