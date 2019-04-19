import logging
import datetime

from flask import jsonify
from google.cloud import datastore


def cars_get(offset):  # noqa: E501
    """Get car locations

    Get a list of all car geolocations # noqa: E501


    :rtype: Cars
    """

    offsetDate = datetime.datetime.utcnow() - datetime.timedelta(hours=offset)
    offsetDate = offsetDate.isoformat()

    print(offsetDate)

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
