from contrib.geocoding import geocode_address

from google.cloud import datastore
import googlemaps

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
        work_items = [add_key_as_id(work_item) for work_item in work_items if
                      work_item['status'] == 'Te Plannen' or
                      work_item['status'] == 'Niet Gereed']

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
