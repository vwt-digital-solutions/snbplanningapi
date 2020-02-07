import datetime

from flask import jsonify
from flask import make_response
from google.cloud import datastore


"""
API endpoints.
"""


def cars_get(offset):
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


def carsinfo_get(offset):
    """Get car info

    Get a list of all car information


    :rtype: CarsInfo

    """
    db_client = datastore.Client()
    query = db_client.query(kind='CarInfo')

    result = [{
            "id": entity.key.id_or_name,
            "license_plate": entity['license_plate'],
            "driver_name": entity['driver_name'],
            "token": entity['token']
        } for entity in query.fetch()]

    return make_response(jsonify(result), 200)


def carsinfo_post(body):
    """Post car info

    Post a car information


    :rtype: CarInfo id

    """
    carinfo = body
    entity = None
    db_client = datastore.Client()

    # for unknown reason attribute 'id' is received as 'id_'
    if 'id_' in carinfo and carinfo['id_'] is not None:
        carinfo_key = db_client.key('CarInfo', carinfo['id_'])
        entity = db_client.get(carinfo_key)
        if entity is None:
            entity = datastore.Entity(key=carinfo_key)
    else:
        entity = datastore.Entity(db_client.key('CarInfo'))

    entity.update({
        "license_plate": carinfo['license_plate'],
        "driver_name": carinfo['driver_name'],
        "token": carinfo['token']
    })
    db_client.put(entity)

    return make_response(jsonify(carinfo_id=entity.key.id_or_name), 201)


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
