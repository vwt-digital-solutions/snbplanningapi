import logging
import datetime
import pytz

from flask import jsonify
from flask import make_response
from google.cloud import datastore


def list_work_items():  # noqa: E501
    """Get a list of work items

    Get a list of work items # noqa: E501


    :rtype: array of work items
    """
    db_client = datastore.Client()
    query = db_client.query(kind='WorkItem')
    result = [res for res in query.fetch() if
              res['StartDatumTijd'] < datetime.datetime.now(pytz.utc) < res['EindDatumTijd']]
    return jsonify(result)


def list_all_work_items():  # noqa: E501
    """Get a list of work items

    Get a list of work items # noqa: E501


    :rtype: array of work items
    """
    db_client = datastore.Client()
    query = db_client.query(kind='WorkItem')
    result = [res for res in query.fetch()]
    return jsonify(result)
