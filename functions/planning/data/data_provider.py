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
        engineers = get_car_locations(db_client, assigned_to_engineer=True)
        engineers = [add_key_as_id(engineer) for engineer in engineers]
    else:
        engineers = car_locations

    try:
        if config.PLANNING_ENGINE_DEBUG:
            engineers = engineers[:100]
    except AttributeError:
        pass

    return [Node(NodeType.car, engineer['id'], engineer) for engineer in engineers]


def get_engineers(engineers=None):
    if engineers is None:
        query = db_client.query(kind='Engineer')

        engineers_list = query.fetch()

        return [add_key_as_id(entity) for entity in engineers_list]

    return engineers


def set_priority_for_work_item(node):
    work_item = node.entity
    if 'task_type' in work_item and 'Premium' in work_item['task_type']:
        priority = 4
    elif 'category' in work_item and work_item['category'] == 'Storing':
        priority = 3
    elif 'category' in work_item and work_item['category'] == 'Schade':
        priority = 2
    else:
        priority = 1

    work_item['priority'] = priority

    return node


def prioritize_and_filter_work_items(work_items, engineers):
    """ The algorithm can run into some issues when there are is a disproportionate amount of workitems
     compared to the number of engineers. This function will add a priority value to every workitem,
     sort them by priority, and only return the most urgent workitems.
    """
    work_items = [set_priority_for_work_item(work_item) for work_item in work_items]

    return work_items
