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
            print('division')
            print(division_dict)
            division = datastore.Entity(self.client.key('Divisions', int(division_dict['Afdeling'])))
            division.update({
                'name': '{0} - {1}'.format(division_dict['Nivo 1'], division_dict['Nivo 2']),
                'business_unit': division_dict.get('Business unit', '')
            })
            if division_dict['Status'] == 'Vervallen':
                batch.delete(division.key)
                logging.debug('Removing business_unit {} - {}'.format(division.key, division))
            else:
                batch.put(division)
                logging.debug('Updating business_unit {} - {}'.format(division.key, division))
        batch.commit()
