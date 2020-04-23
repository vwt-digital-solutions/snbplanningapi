import logging
from google.cloud import storage as gcs
import csv

from dbprocessor import DBProcessor


def process_csv_file(data, context):
    """
    This function reads a CSV file uploaded to the Division cloud storages bucket,
    and updates or creates the associated DataStore entities.

    This function was written in the same structure as other Cloud Functions in this project.
    Mainly because this allows us to easily switch to a PubSub messaging based consume function.
    """

    filename = '{0}/{1}'.format(data['bucket'], data['name'])
    parser = DBProcessor()

    try:
        with gcs.open(filename) as csvfile:
            reader = csv.DictReader(csvfile)
            parser.process({'divisions': reader})
    except Exception as e:
        logging.info('Processing of divisions failed.')
        logging.debug(e)
        raise e
