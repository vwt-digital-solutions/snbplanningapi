"""cars controller module"""
from datetime import datetime, timedelta
from flask import json
from flask import jsonify
from flask import Response
from google.cloud import datastore


def make_http_response(response, status_code: int = 200,
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
    return make_http_response(response, 200, ('private', 'max-age=300'))


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
    return make_http_response([format_carsinfo_get_feature(q) for q in query.fetch()])


def carsinfo_post(body: dict) -> tuple:
    """

    :param body:
    :return:
    """
    client = datastore.Client()
    # The attribute 'id' is received as 'id_' (unknown reason).
    body["id"] = body["id_"]
    del body["id_"]
    if "id" in body and body["id"] is not None:
        key = client.key("CarInfo", body["id"])
        entity = client.get(key)
        entity = datastore.Entity(key=key) if entity is None else entity
    else:
        entity = datastore.Entity(client.key("CarInfo"))
    entity.update({"license_plate": body["license_plate"],
                   "driver_name": body["driver_name"],
                   "token": body["token"]})
    client.put(entity)
    return {"carinfo_id": entity.key.id_or_name}, 201


def is_assigned(assigned, token, car_tokens) -> bool:
    """
    determines whether or not a token is assigned.

    :param assigned: assignment indicator.
    :param token: token value.
    :param car_tokens: list of existing car tokens.
    :return: token assignment indicator.
    """
    return assigned == token in car_tokens if assigned is not None else True


def list_tokens(assigned: object) -> tuple:
    """
    car token listing method.

    :param assigned: assignment indicator.
    :return: list of existing car tokens.
    """
    client = datastore.Client()
    cars, tokens = client.query(kind="CarInfo"), client.query(kind="CarLocation")
    car_tokens = []
    if assigned is not None:
        car_tokens = [car["token"] for car in cars.fetch() if car["token"] is not None and len(car["token"]) > 0]
    tokens = [token.key.id_or_name for token in tokens.fetch()
              if is_assigned(assigned, token.key.id_or_name, car_tokens)]
    return jsonify(tokens), 200
