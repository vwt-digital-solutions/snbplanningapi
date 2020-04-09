import datetime
import pytz

from flask import jsonify
from flask import make_response
from google.cloud import datastore

from cache import cache
from openapi_server.controllers.util import remap_attributes
from openapi_server.models import WorkItem, WorkItemsList, Error

work_items_statuses = ['Te Plannen', 'Gepland', 'Niet Gereed']
work_item_attribute_map = {
    'L2GUID': 'l2_guid',
    'isGeocoded': 'is_geocoded'
}
task_type_categories = {
    'service': 'Service',
    'nls': 'NLS',
    'ftth': 'FttH',
}


"""
Controller functions
"""


@cache.memoize(timeout=300)
def list_work_items(active=False, task_type_category='service'):  # noqa: E501
    """Get a list of work items

    Get a list of work items # noqa: E501

    :rtype: a response containing an array of work items
    """
    if task_type_category not in task_type_categories:
        error = Error('400',
                      'task_type_category is not valid. Possible choices are: {0}'
                      .format(', '.join(task_type_categories.keys()))
                      )
        return make_response(jsonify(error), 400)

    result = get_work_items(task_type_categories[task_type_category])

    if active:
        result = [res for res in result if
                  isinstance(res.get('start_timestamp', None), datetime.datetime) and
                  isinstance(res.get('end_timestamp', None), datetime.datetime) and
                  res.get('start_timestamp', None) < datetime.datetime.now(pytz.utc) < res.get('end_timestamp', None)]

    work_items_list = [WorkItem.from_dict(str(res)) for res in result]

    response = WorkItemsList(items=work_items_list)
    return make_response(jsonify(response), 200, {'Cache-Control': 'private, max-age=300'})


"""
Helper functions
"""


@cache.memoize(timeout=300)
def get_work_items(task_type_category_search_value):
    """Get a list of work items

    Get a list of work items from the DataStore # noqa: E501

    :rtype: array of work items
    """
    db_client = datastore.Client()
    query = db_client.query(kind='WorkItem')

    query.add_filter('task_type', '>=', task_type_category_search_value)
    query.add_filter('task_type', '<=', '{0}z'.format(task_type_category_search_value))

    work_items = [remap_attributes(res, work_item_attribute_map)
                  for res in query.fetch() if res['status'] in work_items_statuses]
    return work_items
