import datetime
import pytz
import config

from flask import jsonify
from flask import make_response
from google.cloud import datastore

from cache import cache

work_items_statuses = ['Te Plannen', 'Gepland', 'Niet Gereed']

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

    return make_response(jsonify(result), 200, {'cache-control': 'private, max-age=300'})


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

    return [res for res in query.fetch() if res['status'] in work_items_statuses]
