from google.cloud import datastore
import logging


class DBProcessor(object):
    def __init__(self):
        self.client = datastore.Client()
        pass

    def process(self, payload):
        batch = self.client.batch()
        batch.begin()

        for division_dict in payload['divisions']:
            division = datastore.Entity(self.client.key('Divisions'), int(division_dict['Afdeling']))
            division.update({
                'name': '{0} - {1}'.format(division_dict['Nivo 1'], division_dict['Nivo 2'])
            })
            batch.put(division_dict)
            logging.debug('Updating business_unit {} - {}'.format(division.key, division))
        batch.commit()
