import time

import config
import google
import requests
from flask import jsonify, request, make_response
from google.cloud import datastore

from cache import cache

from openapi_server.controllers.util import HALSelfRef, HALEmbedded
from openapi_server.controllers.engineers_controller import create_engineer
from openapi_server.models import PlanningItem, PlanningItemsList, WorkItem

db_client = datastore.Client()


def generate_jwt(sa_keyfile, sa_email, audience, expiry_length=260):
    """Generates a signed JSON Web Token using a Google API Service Account."""
    now = int(time.time())

    # build payload
    payload = {
        'iat': now,
        # expires after 'expiry_length' seconds.
        "exp": now + expiry_length,
        # iss must match 'issuer' in the security configuration in your
        # swagger spec (e.g. service account email). It can be any string.
        'iss': sa_email,
        # aud must be either your Endpoints service name, or match the value
        # specified as the 'x-google-audience' in the OpenAPI document.
        'aud':  audience,
        # sub and email should match the service account's email address
        'sub': sa_email,
        'email': sa_email
    }

    # sign with keyfile
    signer = google.auth.crypt.RSASigner.from_service_account_file(sa_keyfile)
    jwt = google.auth.jwt.encode(signer, payload)

    return jwt


"""
Controller functions
"""


@cache.memoize(timeout=300)
def list_planning_items():  # noqa: E501

    signed_jwt = generate_jwt(
        sa_email=config.PLANNING_ENGINE_SERVICE_ACCOUNT_EMAIL,
        sa_keyfile=config.PLANNING_ENGINE_SERVICE_ACCOUNT_KEY,
        audience=config.PLANNING_ENGINE_FUNCTION_URL
    )

    """Makes an authorized request to the endpoint"""
    headers = {
        'Authorization': 'Bearer {}'.format(signed_jwt.decode('utf-8')),
        'content-type': 'application/json'
    }

    response = requests.get(config.PLANNING_ENGINE_FUNCTION_URL, headers=headers)

    workitems_query = db_client.query(kind='WorkItem')
    workitems = list(workitems_query.fetch())

    # !NOTE: The CarInfo entity might become an Engineer entity later!
    engineer_query = db_client.query(kind='CarInfo')
    engineers = list(engineer_query.fetch())

    engineers_by_id = {engineer.key.id_or_name: engineer for engineer in engineers}
    workitems_by_id = {workitem.key.id_or_name: workitem for workitem in workitems}

    result = []

    for item in response.data.result:
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
