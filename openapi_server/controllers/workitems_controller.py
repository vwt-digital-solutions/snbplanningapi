""" work items controller module. """
import pytz
import config
import datetime
from flask import jsonify
from google.cloud import datastore
from openapi_server.controllers.cars_controller import make_http_response


def list_work_items():
    """
    gets all (active) work items from the data store.

    :return: list of active work items.
    """
    now = datetime.datetime.now(pytz.utc)
    statuses = ["Te Plannen", "Gepland", "Niet Gereed"]
    query = datastore.Client().query(kind="WorkItem")
    response = [q for q in query.fetch() if q["start_timestamp"] < now < q["end_timestamp"]
                and q["status"] in statuses and(not hasattr(config, "TASK_TYPE_STARTSWITH")
                                                or q["task_type"].startswith(config.TASK_TYPE_STARTSWITH))]
    return make_http_response(response, 200, ("private", "max-age=300"))


def list_all_work_items():
    """
    gets all work items from the data store.

    :return: list of all work items.
    """
    statuses = ["Te Plannen", "Gepland", "Niet Gereed"]
    query = datastore.Client().query(kind='WorkItem')
    query.add_filter("task_type", ">=", config.TASK_TYPE_STARTSWITH)
    response = [q for q in query.fetch() if q["status"] in statuses]
    return make_http_response(response, 200, ("private", "max-age=300"))

