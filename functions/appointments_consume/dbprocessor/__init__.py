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

        for appointments in payload['appointments']:
            availability = self.get_availability(appointments)

            # Check if get_car_location returned an entity.
            if availability is not None:
                batch.put(availability)

        batch.commit()

    def get_availability(self, appointment):
        id = '{0}-{1}'.format(appointment['userId'],
                              datetime.strptime(appointment['startDate'], '%d-%m-%Y %H:%M:%S').date())
        key = self.client.key('EmployeeAvailability', id)
        entity = self.client.get(key)

        if entity is None:
            entity = datastore.Entity(key=key)

        appointments = entity.get('appointments', [])

        appointments.append({
            'created_on': parse_date(appointment['createdOn']),
            'start_date': parse_date(appointment['startDate']),
            'end_date': parse_date(appointment['endDate']),
            'description': appointment['description'],
            'user_id': appointment['userId'],
            'type_id': appointment['typeId'],
            'state': appointment['state'],
            'fullname': appointment['fullname'],
            'employee_number': appointment['registratienummer'],
        })

        entity.update({
            'appointments': appointments,
        })

        logging.debug('Populate availability with appointment {}'.format(entity.key))

        return entity


def parse_date(date_string, local_time_zone=pytz.timezone('Europe/Amsterdam')):
    """
    :param date_string: A date string in the format '%d-%m-%Y %H:%M:%S'
    :param local_time_zone: Override this timezone if the date to parse is in another timezone than Europe/Amsterdam
    :return: An ISO-formatted date string in UTC.
    """
    if not date_string:
        return ''
    date = datetime.datetime.strptime(date_string, '%d-%m-%Y %H:%M:%S')
    date = local_time_zone.localize(date)
    date = date.astimezone(pytz.utc)

    return date.isoformat()
