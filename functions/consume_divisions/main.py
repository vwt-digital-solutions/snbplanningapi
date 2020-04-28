import logging
import pandas as pd

from dbprocessor import DBProcessor


def process_csv_file(data, context):
    """
    This function reads a CSV file uploaded to the Division cloud storages bucket,
    and updates or creates the associated DataStore entities.

    This function was written in the same structure as other Cloud Functions in this project.
    Mainly because this allows us to easily switch to a PubSub messaging based consume function.
    """

    filename = 'gs://{0}/{1}'.format(data['bucket'], data['name'])
    parser = DBProcessor()

    try:
        df = pd.read_csv(filename)
        parser.process({'divisions': df.to_dict('records')})
    except Exception as e:
        logging.info('Processing of divisions failed.')
        logging.debug(e)
        raise e
