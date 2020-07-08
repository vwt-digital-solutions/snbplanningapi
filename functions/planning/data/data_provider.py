from datetime import datetime, date, timedelta

from contrib.geocoding import geocode_address

from google.cloud import datastore
import googlemaps
import pytz

import config

db_client = datastore.Client()
gmaps = googlemaps.Client(key=config.GEO_API_KEY)


def add_key_as_id(entity):
    entity['id'] = entity.key.id_or_name
    return entity


def get_work_items(work_items=None):
    if work_items is None:
        work_items_query = db_client.query(kind='WorkItem')
        work_items_query.add_filter('task_type', '>=', 'Service Koper')

        work_items = list(work_items_query.fetch())

        date_to_select = (datetime.combine(date.today(), datetime.min.time()) + timedelta(days=1)).astimezone(pytz.utc)
        date_after_tomorrow = date_to_select + timedelta(days=1)

        work_items_niet_gereed = [work_item for work_item in work_items if work_item['status'] == 'Niet Gereed']
        work_items_te_plannen = [work_item for work_item in work_items if work_item['status'] == 'Te Plannen']

        work_items_schade = [work_item for work_item in work_items_te_plannen
                             if work_item.get('category', None) == 'Schade'
                             and work_item.get('resolve_before_timestamp', None)
                             and date_to_select < work_item.get('resolve_before_timestamp', None) > date_after_tomorrow]
        work_items_storing = [work_item for work_item in work_items_te_plannen
                              if work_item.get('category', None) == 'Storing'
                              and work_item.get('start_timestamp', None)
                              and date_to_select < work_item.get('start_timestamp', None) > date_after_tomorrow]

        work_items = [add_key_as_id(work_item) for work_item in
                      work_items_niet_gereed + work_items_schade + work_items_storing]

    return work_items


def get_engineers(engineers=None):
    if engineers is None:
        query = db_client.query(kind='Engineer')

        engineers_list = query.fetch()

        engineers = [add_key_as_id(entity) for entity in engineers_list]

    geocoded_engineers = []

    for engineer in engineers:
        try:
            if 'geometry' not in engineer:
                engineer = geocode_address(gmaps, engineer)
        except IndexError:
            pass
        geocoded_engineers.append(engineer)

    return geocoded_engineers


def get_availabilities(availabilities=None):
    if availabilities is None:
        query = db_client.query(kind='EmployeeAvailability')

        date_to_select = (datetime.combine(date.today(), datetime.min.time()) + timedelta(days=1)).astimezone(pytz.utc)
        query.add_filter('shift_date', '=', date_to_select)

        availability_list = query.fetch()

        availabilities = [add_key_as_id(entity) for entity in availability_list]

    return {availability['employee_number']: availability for availability in availabilities}
