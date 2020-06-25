from contrib.geocoding import geocode_address

from datetime import datetime
import dateutil.parser

from google.cloud import datastore
import googlemaps

from node import Node, NodeType

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
        work_items = [add_key_as_id(work_item) for work_item in work_items if work_item['status'] == 'Te Plannen']

    try:
        if config.PLANNING_ENGINE_DEBUG:
            work_items = work_items[200:600]
    except AttributeError:
        pass

    return [Node(NodeType.location, work_item['id'], work_item) for work_item in work_items]


def get_engineers(engineers=None):
    if engineers is None:
        query = db_client.query(kind='Engineer')

        engineers_list = query.fetch()

        engineers = [add_key_as_id(entity) for entity in engineers_list]

    plannable_engineers = []
    unplannable_engineers = []

    for engineer in engineers:
        try:
            if 'geometry' not in engineer:
                engineer = geocode_address(gmaps, engineer)
                plannable_engineers.append(engineer)
        except IndexError:
            unplannable_engineers.append(engineer['id'])

    return [Node(NodeType.engineer, engineer['id'], engineer) for engineer in plannable_engineers], \
        unplannable_engineers


def set_priority_for_work_item(node):
    work_item = node.entity
    if 'dgs' in work_item and work_item['dgs']:
        priority = 5
    elif 'task_type' in work_item and 'Premium' in work_item['task_type']:
        priority = 4
    elif 'category' in work_item and work_item['category'] == 'Storing':
        priority = 3
    elif 'category' in work_item and work_item['category'] == 'Schade':
        priority = 2
    else:
        priority = 1

    work_item['priority'] = priority

    return node


def convert_to_date_or_none(date_to_convert):
    if isinstance(date_to_convert, datetime):
        return date_to_convert
    if isinstance(date_to_convert, str):
        try:
            return dateutil.parser.isoparse(date_to_convert)
        except ValueError:
            # Invalid date string
            return None
        except OverflowError:
            # Date is bigger than largest int
            return None
    return None


def prioritize_and_filter_work_items(work_items, engineers):
    """ The algorithm can run into some issues when there are is a disproportionate amount of workitems
     compared to the number of engineers. This function will add a priority value to every workitem,
     sort them by priority, and only return the most urgent workitems.
    """
    work_items = [set_priority_for_work_item(work_item) for work_item in work_items]

    work_items_storing = [work_item for work_item in work_items if work_item.entity.get('category', None) == 'Schade']
    work_items_schade = [work_item for work_item in work_items if work_item.entity.get('category', None) == 'Storing']
    other_work_items = [work_item for work_item in work_items if work_item.entity.get('category', None) != 'Storing'
                        and work_item.entity.get('category', None) != 'Schade']

    engineers_schade = [engineer for engineer in engineers if engineer.entity.get('role', None) == 'Lasser']
    engineers_storing = [engineer for engineer in engineers if engineer.entity.get('role', None) == 'Metende']

    work_items_schade = sorted(work_items_schade,
                               key=lambda i: (-i.entity['priority'],
                                              convert_to_date_or_none(i.entity['resolve_before_timestamp']) is None,
                                              convert_to_date_or_none(i.entity['resolve_before_timestamp'])
                                              ))
    work_items_storing = sorted(work_items_storing,
                                key=lambda i: (-i.entity['priority'],
                                               convert_to_date_or_none(i.entity['start_timestamp']) is None,
                                               convert_to_date_or_none(i.entity['start_timestamp'])))

    filtered_work_items = work_items_schade[:len(engineers_schade)] + \
        work_items_storing[:len(engineers_storing)] + \
        other_work_items

    return filtered_work_items, [work_item for work_item in work_items if work_item not in filtered_work_items]
