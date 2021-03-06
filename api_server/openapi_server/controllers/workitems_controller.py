import datetime
import pytz
from contrib.cars import get_car_locations
from contrib.distance import calculate_travel_times, calculate_distance

from flask import make_response, request, jsonify
from google.cloud import datastore

from cache import cache
from openapi_server.controllers.util import remap_attributes, HALSelfRef, HALEmbedded
from openapi_server.models import WorkItem, WorkItemsList, Error, CarDistances, CarDistance

work_items_statuses = ['Te Plannen', 'Gepland', 'Niet Gereed']
work_item_attribute_map = {
    'L2GUID': 'l2_guid',
    'isGeocoded': 'is_geocoded'
}
business_unit_task_types = {
    'service': 'Service',
    'nls': 'NLS',
    'ftth': 'FttH',
}


"""
Controller functions
"""


@cache.memoize(timeout=300)
def list_work_items(active=False, business_unit='service'):  # noqa: E501
    """Get a list of work items

    Get a list of work items # noqa: E501

    :rtype: a response containing an array of work items
    """
    if business_unit not in business_unit_task_types:
        error = Error('400',
                      'business_unit is not valid. Possible choices are: {0}'
                      .format(', '.join(business_unit_task_types.keys()))
                      )
        return make_response(jsonify(error), 400)

    result = get_work_items(business_unit_task_types[business_unit])

    if active:
        result = [res for res in result if
                  isinstance(res.get('start_timestamp', None), datetime.datetime) and
                  isinstance(res.get('end_timestamp', None), datetime.datetime) and
                  res.get('start_timestamp', None) < datetime.datetime.now(pytz.utc) < res.get('end_timestamp', None)]

    response = WorkItemsList(items=result)
    return make_response(jsonify(response), 200, {'Cache-Control': 'private, max-age=300'})


@cache.memoize(timeout=300)
def get_work_item(work_item_id):  # noqa: E501
    """Get a work item

    Get a single work item # noqa: E501

    :rtype: a response containing a work item
    """
    db_client = datastore.Client()

    key = db_client.key("WorkItem", work_item_id)
    work_item = db_client.get(key=key)

    if work_item:
        response = HALEmbedded(workitem=create_workitem(work_item))
    else:
        response = {}

    return make_response(jsonify(response), 200, {'Cache-Control': 'private, max-age=300'})


"""
Helper functions
"""


@cache.memoize(timeout=300)
def get_work_items(business_unit):
    """Get a list of work items

    Get a list of work items from the DataStore # noqa: E501

    :rtype: array of work items
    """
    db_client = datastore.Client()
    query = db_client.query(kind='WorkItem')

    query.add_filter('task_type', '>=', business_unit)
    query.add_filter('task_type', '<=', '{0}z'.format(business_unit))

    work_items = [create_workitem(res, False)
                  for res in query.fetch() if res['status'] in work_items_statuses]
    return work_items


def create_workitem(entity, with_hal=True):
    """ A helper method for creating a workitem with HAL references
    :rtype: WorkItem
    """

    work_item_dict = remap_attributes(entity, work_item_attribute_map)

    if with_hal:
        work_item = WorkItem.from_dict({
            **HALSelfRef(
                path=f'{request.url_root}workitems/{entity.key.id_or_name}'
            ),
            **work_item_dict,
        })
    else:
        work_item = WorkItem.from_dict(work_item_dict)

    work_item.id = entity.key.id_or_name

    return work_item


@cache.memoize(timeout=300)
def car_distances_list(workitem_id: str, offset, sort, limit, cars: str = None):
    """Get a list of carlocations together with their travel time in seconds,
     ordered by the distance from specified workitem"""
    db_client = datastore.Client()

    work_item_entity = db_client.get(db_client.key('WorkItem', workitem_id))

    car_locations = get_car_locations(db_client, True, offset)

    if work_item_entity is None:
        response = Error('400', "Work Item not found")
        return make_response(jsonify(response), 404)

    if cars is not None:
        tokens = cars.split(',')
        car_locations = [car_location for car_location in car_locations if car_location.key.id_or_name in tokens]

    # Calculate euclidean distances for all locations
    euclidean_distances = [(calculate_distance(work_item_entity, car_location), car_location)
                           for car_location in car_locations]

    # Sort and splice distances.
    sorted_euclidean_distances = sorted(euclidean_distances, key=lambda tup: tup[0])
    spliced_euclidean_distances = sorted_euclidean_distances[:limit * 2]

    # Calculate actual travel times, resort and splice.
    travel_times = calculate_travel_times(work_item_entity, [tup[1] for tup in spliced_euclidean_distances])
    sorted_travel_times = sorted(travel_times, key=lambda travel_time: travel_time[sort])
    spliced_travel_times = sorted_travel_times[:limit]

    # Generate valid CarDistances response.
    car_distances = [CarDistance(**travel_time) for travel_time in spliced_travel_times]
    result = CarDistances(items=car_distances)

    return make_response(jsonify(result), 200)
