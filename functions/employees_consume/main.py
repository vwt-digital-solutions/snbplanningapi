import logging
import pandas as pd
from google.cloud import datastore


class DBProcessor(object):
    def __init__(self):
        self.client = datastore.Client()

    def process(self, payload):
        batch = self.client.batch()
        batch.begin()

        for employee_dict in payload['employees']:
            engineer = datastore.Entity(self.client.key('Engineer', int(employee_dict['driver_employee_number'])))
            engineer.update({**employee_dict})
            batch.put(engineer)
            logging.debug('Updating engineer {}'.format(engineer.key))
        batch.commit()


def process_csv_file(data, context):
    """
    This function reads a CSV file uploaded to the Division cloud storages bucket,
    and updates or creates the associated DataStore entities.

    This function was written in the same structure as other Cloud Functions in this project.
    Mainly because this allows us to easily switch to a PubSub messaging based consume function.
    """

    if 'employees.csv' not in data['name']:
        return

    filename = 'gs://{0}/{1}'.format(data['bucket'], data['name'])
    parser = DBProcessor()

    try:
        df = pd.read_csv(filename)
        parser.process({'employees': df.to_dict('records')})
    except Exception as e:
        logging.info('Processing of divisions failed.')
        logging.debug(e)
        raise e
