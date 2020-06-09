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

    car_locations = list(db_client.query(kind='CarLocation').fetch())
    car_locations_dict_by_token = {e.key.id_or_name: e for e in car_locations}
    car_locations_dict_by_license_plate = {e['license']: e for e in car_locations if 'license' in e}

    engineers = []
    for engineer in query_res:
        # Cross reference against CarLocations to check if we can find the engineer's license plate.
        if 'token' in engineer:
            car_location = car_locations_dict_by_token.get(engineer['token'], None)

        if car_location is None and 'license_plate' in engineer:
            car_location = car_locations_dict_by_license_plate.get(engineer['license_plate'], None)

        if car_location is not None:
            engineer.license_plate = car_location.get('license', None)
            engineer.token = car_location.key.id_or_name

        engineers.append(HALEmbedded(engineer=create_engineer(engineer)))

    return make_response(jsonify(EngineersList(
        items=engineers,
        links=HALSelfRef(request.url))
    ), 200)


def engineers_post(body):
    """Post engineer information

    :rtype: CarInfo id

    """
    car_info = Engineer.from_dict(body).to_dict()

    # Remove unnecessary and read-only fields.
    del car_info['id']
    del car_info['license_plate']
    del car_info['division']

    entity = None

    # for unknown reason attribute 'id' is received as 'id_'
    if 'id' in body and body['id'] is not None:
        try:
            car_info_key = db_client.key('CarInfo', int(body['id']))
        except ValueError:
            logger.warning(f"String to int conversion on {engineers_post().__name__} with {body['id']}")
            return make_response(jsonify("The client should not repeat this request without modification."), 400)
        entity = db_client.get(car_info_key)
        if entity is None:
            entity = datastore.Entity(key=car_info_key)
    else:
        # Check if an Engineer with that token already exists.
        query = db_client.query(kind='CarInfo')
        query.add_filter('token', '=', body['token'])
        if len(list(query.fetch())) > 0:
            error = Error('400', 'A Car with that token already exists.')
            return make_response(jsonify(error), 400)

        entity = datastore.Entity(db_client.key('CarInfo'))

    entity.update(car_info)
    db_client.put(entity)

    car = Engineer.from_dict(entity)
    car.id = str(entity.key.id_or_name)

    car_locations = list(db_client.query(kind='CarLocation').fetch())
    search_list = [car_location for car_location in car_locations if car_location.key.id_or_name == car.token]
    if len(search_list) > 0:
        car.license_plate = search_list[0].get('license', None)
        car.token = search_list[0].key.id_or_name

    return make_response(jsonify(car), 201)


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
