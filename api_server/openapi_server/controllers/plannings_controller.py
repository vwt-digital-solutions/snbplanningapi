from flask import jsonify, request, make_response
from google.cloud import datastore

from cache import cache

from openapi_server.controllers.util import HALSelfRef, HALEmbedded
from openapi_server.controllers.engineers_controller import create_engineer
from openapi_server.models import PlanningItem, PlanningItemsList, WorkItem

db_client = datastore.Client()

"""
Controller functions
"""


@cache.memoize(timeout=300)
def list_planning_items():  # noqa: E501
    workitems_query = db_client.query(kind='WorkItem')
    workitems = list(workitems_query.fetch())

    # !NOTE: The CarInfo entity might become an Engineer entity later!
    engineer_query = db_client.query(kind='CarInfo')
    engineers = list(engineer_query.fetch())

    result = []
    for data in zip(engineers, workitems):
        engineer, workitem = data
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
