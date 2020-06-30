import json

import config
from cache import cache

import requests
from flask import jsonify, request, make_response

from google.auth.transport.requests import Request
from google.oauth2 import id_token
from google.cloud import datastore

from openapi_server.controllers.engineers_controller import create_engineer
from openapi_server.controllers.workitems_controller import create_workitem
from openapi_server.controllers.util import HALSelfRef, HALEmbedded

from openapi_server.models import PlanningItem, PlanningItemsList, WorkItem, Error

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

    res = requests.get(function_url, headers=function_headers)

    if 200 <= res.status_code < 300:
        res = json.loads(res.content)

        workitems_query = db_client.query(kind='WorkItem')
        workitems = list(workitems_query.fetch())

        engineer_query = db_client.query(kind='Engineer')
        engineers = list(engineer_query.fetch())

        engineers_by_id = {engineer.key.id_or_name: engineer for engineer in engineers}
        workitems_by_id = {workitem.key.id_or_name: workitem for workitem in workitems}

        planning = []
        for planning_item in res['result']:
            planning.append(create_planning_item(
                engineers_by_id,
                workitems_by_id,
                planning_item
            ))

        unplanned_engineers = []
        for engineer_item in res['unplanned_engineers']:
            unplanned_engineers.append(create_engineer(
                engineers_by_id[engineer_item]
            ))

        unplanned_workitems = []
        for work_item in res['unplanned_workitems']:
            unplanned_workitems.append(create_workitem(
                workitems_by_id[work_item]
            ))

        response = PlanningItemsList(
            items=planning,
            unplanned_engineers=unplanned_engineers,
            unplanned_workitems=unplanned_workitems,
            links=HALSelfRef(f'{request.url_root}plannings')
        )

        return make_response(jsonify(response), 200, {'Cache-Control': 'private, max-age=300'})
    else:
        response = Error(500, 'Er is een fout opgetreden bij het genereren van de planning')
        return make_response(response, 500)


def create_planning_item(engineers_by_id, workitems_by_id, planning_item):
    engineer = engineers_by_id[planning_item['engineer']]
    workitem_entity = workitems_by_id[planning_item['workitem']]

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
