"""cars controller module"""
from datetime import datetime, timedelta
from flask import json
from flask import jsonify
from flask import Response
from flask import make_response
from google.cloud import datastore


def make_get_response(response, status_code: int = 200,
                      cache_control: tuple = ('no-store',)) -> Response:
    """
    creates the HTTP response.

    :param response: response body (JSON-formatted).
    :param status_code: response status code.
    :param cache_control: cache control header settings.
    :return: HTTP response object.
    """
    resp: Response = Response()
    resp.status_code = status_code
    resp.response = json.dumps(response)
    # customized cache-control header.
    for header in cache_control:
        resp.headers.add_header('cache-control', header)
    resp.content_type = 'application/json'
    # remove default connection header.
    resp.headers.remove('connection')
    return resp


def format_cars_get_feature(query_item) -> dict:
    """
    formats a query item into the correct feature format for the HTTP response body.

    :param query_item: item of the query result.
    :return: formatted response body feature.
    """
    return {"type": "Feature", "geometry": query_item["geometry"],
            "properties": {"token": query_item.key.id_or_name}}


def cars_get(offset: int = 168) -> Response:
    """
    gets the most recent car information.

    :param offset: retrospect in hours.
    :return: corresponding HTTP response.
    """
    treshold = (datetime.utcnow() - timedelta(hours=offset)).isoformat()
    query = datastore.Client().query(kind="CarLocation")
    query.add_filter("when", ">=", treshold)
    query = query.fetch()
    response = {"type": "FeatureCollection",
                "features": [format_cars_get_feature(q) for q in query]}
    return make_get_response(response, 200, ('private', 'max-age=300'))


def format_carsinfo_get_feature(query_item) -> dict:
    """
    formats a query item into the correct feature format for the HTTP response body.

    :param query_item: item of the query result.
    :return: formatted response body feature.
    """
    return {"id": query_item.key.id_or_name,
            "license_plate": query_item["license_plate"],
            "driver_name": query_item["driver_name"],
            "token": query_item["token"]}


def carsinfo_get() -> Response:
    """
    gets the most recent static car information.

    :return: corresponding HTTP response.
    """
    query = datastore.Client().query(kind="CarInfo")
    return make_get_response([format_carsinfo_get_feature(q) for q in query.fetch()])


def carsinfo_post(body):
    """Post car info

    Post a car information # noqa: E501


    :rtype: CarInfo id
    """
    carinfo = body
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


def is_assigned(token, assigned, car_tokens):
    """

    :param token:
    :param assigned:
    :param car_tokens:
    :return:
    """
    return assigned == token in car_tokens if assigned is not None else True


def list_tokens(assigned):
    """Enumerate tokens

    :rtype array of strings
    """
    db_client = datastore.Client()
    tokens_query = db_client.query(kind='CarLocation')
    cars_query = db_client.query(kind='CarInfo')
    car_tokens = []
    if assigned is not None:
        car_tokens = [ci['token'] for ci in cars_query.fetch()
                      if ci['token'] is not None and len(ci['token']) > 0]

    tokens = [token.key.id_or_name for token in tokens_query.fetch()
              if is_assigned(token.key.id_or_name, assigned, car_tokens)]
    return jsonify(tokens)
