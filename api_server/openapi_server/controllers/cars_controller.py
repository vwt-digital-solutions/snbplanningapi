import datetime

from flask import jsonify
from flask import make_response
from google.cloud import datastore

from cache import cache
from openapi_server.models import Car, CarDistance, CarDistances
from openapi_server.contrib.distance import calculate_distance

"""
API endpoints.
"""


@cache.memoize(timeout=300)
def car_locations_list(offset):
    """Get car locations

    Get a list of all car geolocations.

    :return: Returns a GEOJSON FeatureCollection object.
    This function only includes CarLocations whose token is assigned to a CarInfo.

    :rtype: Cars

    """
    db_client = datastore.Client()

    # Get initial query of all car locations
    offset_date = datetime.datetime.utcnow() - datetime.timedelta(hours=offset)
    offset_date = offset_date.isoformat()
    query = db_client.query(kind='CarLocation')
    query.add_filter('when', '>=', offset_date)
    query_iter = query.fetch()

    # Filter query on CarInfo tokens
    car_info_tokens = get_car_info_tokens(db_client)
    query_iter = [car_location for car_location in query_iter
                  if is_assigned(car_location.key.id_or_name, car_info_tokens, True)]

    result = {
        "type": "FeatureCollection",
        "features": []
    }

    for entity in query_iter:
        result['features'].append({
            "type": "Feature",
            "geometry": entity['geometry'],
            "properties": {
                "token": entity.key.id_or_name
            }
        })

    return make_response(jsonify(result), 200, {'cache-control': 'private, max-age=300'})


@cache.memoize(timeout=300)
def cars_list(offset):
    """Get car info

    Get a list of all car information


    :rtype: CarsInfo

    """
    db_client = datastore.Client()
    query = db_client.query(kind='CarInfo')

    query_iter = query.fetch()

    result = []

    for entity in query_iter:
        car = Car.from_dict(entity)
        car.id = str(entity.key.id_or_name)
        result.append(car)

    return make_response(jsonify(result), 200)


def cars_post(body):
    """Post car info

    Post a car information


    :rtype: CarInfo id

    """
    car_info = Car.from_dict(body).to_dict()
    entity = None
    db_client = datastore.Client()

    # for unknown reason attribute 'id' is received as 'id_'
    if 'id_' in body and body['id_'] is not None:
        car_info_key = db_client.key('CarInfo', int(body['id_']))
        entity = db_client.get(car_info_key)
        if entity is None:
            entity = datastore.Entity(key=car_info_key)
        car_info['id'] = entity.key.id_or_name
    else:
        entity = datastore.Entity(db_client.key('CarInfo'))

    entity.update(car_info)
    db_client.put(entity)

    return make_response(jsonify(carinfo_id=str(entity.key.id_or_name)), 201)


@cache.cached(timeout=300, key_prefix="list_tokens")
def list_tokens(assigned):
    """Enumerate tokens

    :param assigned: When set to true, only return tokens that have already been assigned a CarInfo entity.
    Defaults to false.

    :rtype list of strings

    """
    db_client = datastore.Client()
    tokens_query = db_client.query(kind='CarLocation')
    car_tokens = []

    if assigned is not None:
        car_tokens = get_car_info_tokens(db_client)

    tokens = [token.key.id_or_name for token in tokens_query.fetch()
              if is_assigned(token.key.id_or_name, car_tokens, assigned)]

    return jsonify(tokens)


@cache.memoize(timeout=300)
def car_distances_list(work_item: str, sort, limit):
    """Get a list of carlocations together with their travel time in seconds,
     ordered by the distance from specified workitem"""

    db_client = datastore.Client()

    work_item_entity = db_client.get(db_client.key('WorkItem', work_item))

    # Get all CarLocations
    query = db_client.query(kind='CarLocation')
    query_iter = query.fetch()

    # Filter CarLocations on matchin CarInfo
    car_info_tokens = get_car_info_tokens(db_client)
    query_iter = [car_location for car_location in query_iter
                  if is_assigned(car_location.key.id_or_name, car_info_tokens, True)]

    # Calculate euclidean distances for all locations
    car_distances = [(calculate_distance(work_item_entity, car_location), car_location)
                     for car_location in query_iter]

    # Sort and splice distances.
    car_distances = sorted(car_distances, key=lambda tup: tup[0])
    car_distances = car_distances[:limit]

    # Generate valid CarDistances response.
    car_distances = [CarDistance(token=tup[1].key.id_or_name, distance=tup[0], travel_time=round(tup[0] * 90)) for tup in car_distances]
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


def get_car_info_tokens(db_client: datastore.Client):
    """Retrieve a list of tokens from CarInfo

    :param db_client: The datastore Client.

    :rtype a list of strings

    """
    cars_query = db_client.query(kind='CarInfo')

    car_tokens = [car_info['token'] for
                  car_info in cars_query.fetch()
                  if car_info['token'] is not None and len(car_info['token']) > 0]

    return car_tokens
