from cache import cache

from flask import jsonify
from flask import make_response

from google.cloud import datastore

import logging
import config

from contrib.cars import get_car_locations, get_car_info_tokens, is_assigned
from openapi_server.models import Token, TokensList

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

    car_locations = get_car_locations(db_client, True, offset)

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
def list_tokens(offset, assigned=None):
    """Enumerate tokens

    :param assigned: When set to true, only return tokens that have already been assigned a CarInfo entity.
    When set to false, only return tokens that have not been assigned a CarInfo entity.
    When not set, returns all tokens.

    :rtype list of strings

    """

    car_locations = list(get_car_locations(db_client, assigned, offset))

    car_locations.sort(key=lambda x: x.get('license') or 'ZZZZZZ', reverse=False)

    if assigned is not None:
        car_tokens = get_car_info_tokens(db_client)

        car_locations = [car_location for car_location in car_locations
                         if is_assigned(car_location.key.id_or_name, car_tokens, assigned)]

    tokens = []

    for entity in car_locations:
        token = Token.from_dict(entity)
        token.id = str(entity.key.id_or_name)
        tokens.append(token)

    result = TokensList(items=tokens)

    return make_response(jsonify(result), 200)


def map_configurations_get():
    """Get the map configurations
    :rtype: str
    """
    return make_response(jsonify(config.MAPS_API_KEY), 200)
