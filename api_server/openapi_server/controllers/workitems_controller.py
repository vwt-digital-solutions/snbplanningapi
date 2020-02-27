import datetime
import pytz
import config

from flask import jsonify
from flask import make_response
from google.cloud import datastore

from cache import cache
from openapi_server.models import WorkItem

work_items_statuses = ['Te Plannen', 'Gepland', 'Niet Gereed']
work_item_attribute_map = {
    'L2GUID': 'l2_guid',
    'isGeocoded': 'is_geocoded'
}


"""
Controller functions
"""


@cache.memoize(timeout=300)
def list_work_items(active=False):  # noqa: E501
    """Get a list of work items

    Get a list of work items # noqa: E501

    :rtype: a response containing an array of work items
    """
    result = get_work_items()

    if active:
        result = [res for res in result if
                  isinstance(res.get('start_timestamp', None), datetime.datetime) and
                  isinstance(res.get('end_timestamp', None), datetime.datetime) and
                  res.get('start_timestamp', None) < datetime.datetime.now(pytz.utc) < res.get('end_timestamp', None)]

    work_items_list = [WorkItem.from_dict(res) for res in result]

    return make_response(jsonify(work_items_list), 200, {'cache-control': 'private, max-age=300'})


"""
Helper functions
"""


@cache.cached(timeout=300, key_prefix='retrieve_workitems_from_datastore')
def get_work_items():
    """Get a list of work items

    Get a list of work items from the DataStore # noqa: E501

    :rtype: array of work items
    """
    db_client = datastore.Client()
    query = db_client.query(kind='WorkItem')
    if hasattr(config, 'TASK_TYPE_STARTSWITH'):
        query.add_filter('task_type', '>=', config.TASK_TYPE_STARTSWITH)

    work_items = [remap_attributes(res) for res in query.fetch() if res['status'] in work_items_statuses]
    return work_items


def remap_attributes(work_item):
    """Map attributes from one key to another on the given dictionary.

    :rtype: a dictionary
        """
    for(from_key, to_key) in work_item_attribute_map.items():
        work_item[to_key] = work_item.get(from_key, None)
        del work_item[from_key]

    return work_item
