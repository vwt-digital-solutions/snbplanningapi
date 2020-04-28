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

    work_items_list = [WorkItem.from_dict(res) for res in result]

    response = WorkItemsList(items=work_items_list)
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

    work_items = [remap_attributes(res, work_item_attribute_map)
                  for res in query.fetch() if res['status'] in work_items_statuses]
    return work_items
