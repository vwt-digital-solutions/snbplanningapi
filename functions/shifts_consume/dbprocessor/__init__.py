from datetime import datetime

import pytz
from google.cloud import datastore
import logging


class DBProcessor(object):
    def __init__(self):
        self.client = datastore.Client()
        pass

    def process(self, payload):
        batch = self.client.batch()
        batch.begin()

        for shift in payload['shift']:
            availability = self.get_availability(shift)

            # Check if get_car_location returned an entity.
            if availability is not None:
                batch.put(availability)

        batch.commit()

    def get_availability(self, shift):
        shift_date = datetime.strptime(shift['startDate'], '%d-%m-%Y %H:%M:%S').date()
        id = '{0}-{1}'.format(shift_date, shift['registratienummer'])
        key = self.client.key('EmployeeAvailability', id)
        entity = self.client.get(key)

        if entity is None:
            entity = datastore.Entity(key=key)

        start_date = parse_date(shift['startDate'])
        end_date = parse_date(shift['endDate'])

        entity.update({
            'employee_number': shift['registratienummer'],
            'shift_date': str(shift_date),
            'shift_start_date': start_date,
            'shift_end_date': end_date,
            'active': shift['isActive'],
            'name': shift['name'],
        })

        logging.debug('Populate shift {}'.format(entity.key))

        return entity


def parse_date(date_string, local_time_zone=pytz.timezone('Europe/Amsterdam')):
    """
    :param date_string: A date string in the format '%d-%m-%Y %H:%M:%S'
    :param local_time_zone: Override this timezone if the date to parse is in another timezone than Europe/Amsterdam
    :return: An ISO-formatted date string in UTC.
    """
    if not date_string:
        return ''
    date = datetime.strptime(date_string, '%d-%m-%Y %H:%M:%S')
    date = local_time_zone.localize(date)
    date = date.astimezone(pytz.utc)

    return date.isoformat()
