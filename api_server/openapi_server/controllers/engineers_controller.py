from flask import jsonify, make_response, request
from google.cloud import datastore

from cache import cache
import logging
from openapi_server.models import Engineer, EngineersList, Error
from openapi_server.controllers.util import HALSelfRef, HALEmbedded


"""
API endpoints.
"""
db_client = datastore.Client()
logger = logging.getLogger(__name__)


@cache.memoize(timeout=300)
def engineers_list(business_unit=None):
    """Get info of all engineers

    Get a list of all engineers' information
    """

    # !NOTE We might want to change the datastore entity to Engineers
    query = db_client.query(kind="CarInfo")

    if business_unit:
        query.add_filter('business_unit', '=', business_unit)

    query_res = list(query.fetch())

    engineers = []
    for engineer in query_res:
        engineers.append(HALEmbedded(engineer=create_engineer(engineer)))

    return make_response(jsonify(EngineersList(
        items=engineers,
        links=HALSelfRef(request.url))
    ), 200)


@cache.memoize(timeout=300)
def get_engineer(engineer_id):
    """Get engineer info

    Get info for one engineer
    :rtype: Engineer

    """

    try:
        engineer_id = int(engineer_id)
    except ValueError:
        response = Error('400', "This engineer_id is not an integer value")
        return make_response(jsonify(response), 400)

    # !NOTE We might want to change the datastore entity to Engineers
    key = db_client.key("CarInfo", engineer_id)
    engineer = None
    try:
        engineer = db_client.get(key=key)
    except ValueError:
        response = Error('400', "The specified id is not valid")
        return make_response(jsonify(response), 400)

    if engineer:
        response = HALEmbedded(
            engineer=create_engineer(engineer)
        )
        return make_response(jsonify(response), 200)

    response = Error('404', "This Engineer wasn't found")
    return make_response(jsonify(response), 400)


def create_engineer(engineer):
    """ A helper method for creating an Engineer with HAL references
    :rtype: Engineer
    """
    return Engineer.from_dict({
        **HALSelfRef(
            path=f'{request.url_root}engineers/{engineer.key.id_or_name}'
        ),
        **engineer,
        "id": engineer.key.id_or_name
    })
