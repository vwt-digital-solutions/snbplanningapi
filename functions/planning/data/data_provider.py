from google.cloud import datastore

from node import Node, NodeType

import config

from contrib.cars import get_car_locations

db_client = datastore.Client()


def add_key_as_id(entity):
    entity['id'] = entity.key.id_or_name
    return entity


def get_work_items(work_items=None):
    if work_items is None:
        work_items_query = db_client.query(kind='WorkItem')
        work_items_query.add_filter('task_type', '>=', 'Service Koper')

        work_items = list(work_items_query.fetch())
        work_items = [add_key_as_id(work_item) for work_item in work_items if work_item['status'] == 'Te Plannen']

    try:
        if config.PLANNING_ENGINE_DEBUG:
            work_items = work_items[200:600]
    except AttributeError:
        pass

    return [Node(NodeType.location, work_item['id'], work_item) for work_item in work_items]


def get_cars(car_locations=None):
    if car_locations is None:
        engineers = get_car_locations(db_client, assigned_to_car_info=True)
        engineers = [add_key_as_id(engineer) for engineer in engineers]
    else:
        engineers = car_locations

    try:
        if config.PLANNING_ENGINE_DEBUG:
            engineers = engineers[:100]
    except AttributeError:
        pass

    return [Node(NodeType.car, engineer['id'], engineer) for engineer in engineers]


def get_car_info(car_info=None):
    if car_info is None:
        query = db_client.query(kind='CarInfo')

        car_info_list = query.fetch()

        return [add_key_as_id(entity) for entity in car_info_list]

    return car_info
