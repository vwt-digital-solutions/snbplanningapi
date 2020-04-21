import datetime

from flask import jsonify
from flask import make_response
from google.cloud import datastore

from cache import cache
import logging
from openapi_server.models import Car, CarDistance, CarDistances, CarsList, Token, TokensList, Error
from openapi_server.contrib.distance import calculate_distance, calculate_travel_times

"""
API endpoints.
"""
db_client = datastore.Client()
logger = logging.getLogger(__name__)


@cache.memoize(timeout=300)
def car_locations_list(offset):
    """Get car locations

    Get a list of all car geolocations.

    :return: Returns a GEOJSON FeatureCollection object.
    This function only includes CarLocations whose token is assigned to a CarInfo.

    :rtype: Cars
    """

    car_locations = get_car_locations(True, offset)

    result = {
        "type": "FeatureCollection",
        "features": []
    }

    for entity in car_locations:
        result['features'].append({
            "type": "Feature",
            "geometry": entity['geometry'],
            "properties": {
                "token": entity.key.id_or_name
            }
        })

    return make_response(jsonify(result), 200, {'Cache-Control': 'private, max-age=300'})


@cache.memoize(timeout=300)
def cars_list(offset, business_unit=None):
    """Get car info

    Get a list of all car information


    :rtype: CarsInfo

    """
    query = db_client.query(kind='CarInfo')

    if business_unit is not None:
        query.add_filter('business_unit', '=', business_unit)

    query_iter = query.fetch()

    car_locations = list(db_client.query(kind='CarLocation').fetch())

    result = []

    for entity in query_iter:
        car = Car.from_dict(entity)
        car.id = str(entity.key.id_or_name)

        search_list = [car_location for car_location in car_locations if car_location.key.id_or_name == car.token]
        if len(search_list) > 0:
            car.license_plate = search_list[0].get('license', None)

        result.append(car)

    result = CarsList(items=result)

    return make_response(jsonify(result), 200)


def cars_post(body):
    """Post car info

    Post a car information


    :rtype: CarInfo id

    """
    car_info = Car.from_dict(body).to_dict()

    # Remove unnecessary and read-only fields.
    del car_info['id']
    del car_info['license_plate']

    entity = None

    # for unknown reason attribute 'id' is received as 'id_'
    if 'id_' in body and body['id_'] is not None:
        try:
            car_info_key = db_client.key('CarInfo', int(body['id_']))
        except ValueError:
            logger.warning(f"String to int conversion on {cars_post.__name__} with {body['id_']}")
            return make_response(jsonify("The client should not repeat this request without modification."), 400)
        entity = db_client.get(car_info_key)
        if entity is None:
            entity = datastore.Entity(key=car_info_key)
    else:
        # Check if a car with that token already exists.
        query = db_client.query(kind='CarInfo')
        query.add_filter('token', '=', body['token'])
        if len(list(query.fetch())) > 0:
            error = Error('400', 'A Car with that token already exists.')
            return make_response(jsonify(error), 400)

        entity = datastore.Entity(db_client.key('CarInfo'))

    entity.update(car_info)
    db_client.put(entity)

    car = Car.from_dict(entity)

    car_locations = list(db_client.query(kind='CarLocation').fetch())
    search_list = [car_location for car_location in car_locations if car_location.key.id_or_name == car.token]
    if len(search_list) > 0:
        car.license_plate = search_list[0].get('license', None)

    return make_response(jsonify(car), 201)


@cache.memoize(timeout=300)
def list_tokens(offset, assigned=None):
    """Enumerate tokens

    :param assigned: When set to true, only return tokens that have already been assigned a CarInfo entity.
    When set to false, only return tokens that have not been assigned a CarInfo entity.
    When not set, returns all tokens.

    :rtype list of strings

    """

    car_locations = list(get_car_locations(assigned, offset))

    car_locations.sort(key=lambda x: x.get('license') or 'ZZZZZZ', reverse=False)

    if assigned is not None:
        car_tokens = get_car_info_tokens()

        car_locations = [car_location for car_location in car_locations
                         if is_assigned(car_location.key.id_or_name, car_tokens, assigned)]

    tokens = []

    for entity in car_locations:
        token = Token.from_dict(entity)
        token.id = str(entity.key.id_or_name)
        tokens.append(token)

    result = TokensList(items=tokens)

    return make_response(jsonify(result), 200)


@cache.memoize(timeout=300)
def car_distances_list(work_item: str, offset, sort, limit, cars: str = None):
    """Get a list of carlocations together with their travel time in seconds,
     ordered by the distance from specified workitem"""

    work_item_entity = db_client.get(db_client.key('WorkItem', work_item))

    car_locations = get_car_locations(True, offset)

    if work_item_entity is None:
        return make_response(jsonify("Work Item not found"), 404)

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


"""
Helper functions
"""


def is_assigned(token, car_tokens, assigned=None):
    """Check if a token had an associated CarInfo or not.

    :param token: The token to check.
    :param assigned: When this value is set to True, check if the token is assigned,
    when set to false, check if the token is not assigned. If assigned is None, always return True
    :param car_tokens: This list of tokens to check against

    :rtype bool

    """
    if assigned is not None:
        return (assigned and token in car_tokens) or (not assigned and token not in car_tokens)

    return True


@cache.memoize(timeout=300)
def get_car_locations(assigned_to_car_info=True, offset=None):
    """
    Retrieve a list of carLocations from CarLocations

    :param db_client: The datastore Client.
    :param assigned_to_car_info: Determines wether to return locations linked to a car info object or not.
    :param offset: Maximum number of hours since the CarLocation was last updated.

    :rtype a list of CarLocation entities
    """

    query = db_client.query(kind='CarLocation')

    if offset is not None:
        offset_date = datetime.datetime.utcnow() - datetime.timedelta(hours=offset)
        offset_date = offset_date.isoformat()

        query.add_filter('when', '>=', offset_date)

    query_iter = query.fetch()

    # Filter query on CarInfo tokens
    if assigned_to_car_info:
        car_info_tokens = get_car_info_tokens()
        query_iter = [car_location for car_location in query_iter
                      if is_assigned(car_location.key.id_or_name, car_info_tokens, True)]
    else:
        query_iter = list(query_iter)

    return query_iter


@cache.memoize(timeout=300)
def get_car_info_tokens():
    """Retrieve a list of tokens from CarInfo

    :param db_client: The datastore Client.

    :rtype a list of strings

    """
    cars_query = db_client.query(kind='CarInfo')

    car_tokens = [car_info['token'] for
                  car_info in cars_query.fetch()
                  if 'token' in car_info is not None and len(car_info['token']) > 0]

    return car_tokens
