import json

import config
from cache import cache

import requests
from flask import jsonify, request, make_response

from google.auth.transport.requests import Request
from google.oauth2 import id_token
from google.cloud import datastore

from openapi_server.controllers.engineers_controller import create_engineer
from openapi_server.controllers.util import HALSelfRef, HALEmbedded

from openapi_server.models import PlanningItem, PlanningItemsList, WorkItem

db_client = datastore.Client()

"""
Controller functions
"""


@cache.memoize(timeout=300)
def list_planning_items():  # noqa: E501
    service_account_token = id_token.fetch_id_token(Request(), config.PLANNING_ENGINE_FUNCTION_URL)
    function_url = config.PLANNING_ENGINE_FUNCTION_URL

    # Provide the token in the request to the receiving function
    function_headers = {'Authorization': f'bearer {service_account_token}'}

    response = requests.get(function_url, headers=function_headers)
    planning_result = json.loads(response.content)['result']

    workitems_query = db_client.query(kind='WorkItem')
    workitems = list(workitems_query.fetch())

    # !NOTE: The CarInfo entity might become an Engineer entity later!
    engineer_query = db_client.query(kind='CarInfo')
    engineers = list(engineer_query.fetch())

    engineers_by_id = {engineer.key.id_or_name: engineer for engineer in engineers}
    workitems_by_id = {workitem.key.id_or_name: workitem for workitem in workitems}

    result = []

    for item in planning_result:
        engineer = engineers_by_id[item['engineer']]
        workitem = workitems_by_id[item['workitem']]
        result.append(create_planning_item(engineer, workitem))

    response = PlanningItemsList(
        items=result,
        links=HALSelfRef(f'{request.url_root}plannings')
    )

    return make_response(jsonify(response), 200, {'Cache-Control': 'private, max-age=300'})


def create_planning_item(engineer, workitem_entity):
    workitem = WorkItem.from_dict({
        **HALSelfRef(
            path=f'{request.url_root}workitems/{workitem_entity.key.id_or_name}'
        ),
        **workitem_entity
    })

    workitem.id = workitem_entity.key.id_or_name

    return PlanningItem.from_dict(HALEmbedded(
        engineer=create_engineer(engineer),
        workitem=workitem
    ))
