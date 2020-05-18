from google.cloud import datastore

from functions.planning.node import Node, NodeType

import config

from api_server.contrib.cars import get_car_locations

db_client = datastore.Client()


def get_work_items():
    work_items_query = db_client.query(kind='WorkItem')
    work_items_query.add_filter('task_type', '>=', 'Service Koper')

    work_items = list(work_items_query.fetch())
    work_items = [work_item for work_item in work_items if work_item['status'] == 'Te Plannen']

    try:
        if config.PLANNING_ENGINE_DEBUG:
            work_items = work_items[100:400]
    except AttributeError:
        pass

    return [Node(NodeType.location, work_item.key.id_or_name, work_item) for work_item in work_items]


def get_cars():
    engineers = get_car_locations(db_client, assigned_to_car_info=True)

    try:
        if config.PLANNING_ENGINE_DEBUG:
            engineers = engineers[50:150]
    except AttributeError:
        pass

    return [Node(NodeType.car, engineer.key.id_or_name, engineer) for engineer in engineers]
