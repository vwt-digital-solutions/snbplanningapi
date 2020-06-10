from datetime import datetime

import pytz
from google.cloud import datastore
import logging


class DBProcessor(object):
    def __init__(self):
        self.client = datastore.Client()
        self.updated_availabilities = {}

    def process(self, payload):
        batch = self.client.batch()
        batch.begin()

        for appointment in payload['appointments']:
            self.update_availability(appointment)

        for (key, availability) in self.updated_availabilities.items():
            batch.put(availability)

        batch.commit()

    def update_availability(self, appointment):
        id = '{0}-{1}'.format(appointment['userId'],
                              datetime.strptime(appointment['startDate'], '%d-%m-%Y %H:%M:%S').date())

        entity = self.updated_availabilities.get(id, None)

        if entity is None:
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

        self.updated_availabilities[id] = entity

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
