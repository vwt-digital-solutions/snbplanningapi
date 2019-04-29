import logging
import datetime
import random

from flask import jsonify
from flask import make_response
from google.cloud import datastore


def cars_get(offset):  # noqa: E501
    """Get car locations

    Get a list of all car geolocations # noqa: E501


    :rtype: Cars
    """

    offsetDate = datetime.datetime.utcnow() - datetime.timedelta(hours=offset)
    offsetDate = offsetDate.isoformat()

    db_client = datastore.Client()
    query = db_client.query(kind='CarLocation')
    query.add_filter('when', '>=', offsetDate)
    query_iter = query.fetch()
    result = {
        "type": "FeatureCollection",
        "features": []
    }
    for entity in query_iter:
        logging.info('{}'.format(entity))
        result['features'].append({
            "type": "Feature",
            "geometry": entity['geometry'],
            "properties": {}
        })

    return jsonify(result)


def carsinfo_get(offset):  # noqa: E501
    """Get car info

    Get a list of all car information # noqa: E501


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

    return jsonify(result)


def carsinfo_post(body):  # noqa: E501
    """Post car info

    Post a list of all updated car information # noqa: E501


    :rtype: CarsInfo
    """

    return make_response('Cars updated', 201)


def is_assigned(token, assigned, car_tokens):
    if assigned is not None:
        return (assigned and token in car_tokens) or (not assigned and token not in car_tokens)
    else:
        return True


def list_tokens(assigned):  # noqa: E501
    """Enumerate tokens

    :rtype array of strings
    """
    db_client = datastore.Client()
    tokens_query = db_client.query(kind='CarLocation')
    cars_query = db_client.query(kind='CarInfo')
    car_tokens = []
    if assigned is not None:
        car_tokens = [ci['token'] for ci in cars_query.fetch() if ci['token'] is not None and len(ci['token']) > 0]

    tokens = [token.key.id_or_name for token in tokens_query.fetch() if is_assigned(token.key.id_or_name, assigned,
                                                                                    car_tokens)]

    return jsonify(tokens)
