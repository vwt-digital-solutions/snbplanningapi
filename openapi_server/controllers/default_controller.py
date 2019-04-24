import logging
import datetime
import random

from flask import jsonify
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

    licensePlateItems = ['AA-BB-11', 'CC-DD-22', 'EE-FF-33', 'GG-HH-44', 'II-JJ-55']
    nameItems = ['Pietje Puk', 'Connie Moeleker', 'Alco Liest', 'Peter Celie', 'Kenny Boeijen']

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
            "properties": {
                "license_plate": random.choice(licensePlateItems),
                "driver_name": random.choice(nameItems)
            }
        })

    return jsonify(result)
