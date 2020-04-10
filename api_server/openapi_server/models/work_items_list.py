# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from openapi_server.models.base_model_ import Model
from openapi_server.models.work_item import WorkItem
from openapi_server import util

from openapi_server.models.work_item import WorkItem  # noqa: E501

class WorkItemsList(Model):
    """NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).

    Do not edit the class manually.
    """

    def __init__(self, items=None):  # noqa: E501
        """WorkItemsList - a model defined in OpenAPI

        :param items: The items of this WorkItemsList.  # noqa: E501
        :type items: List[WorkItem]
        """
        self.openapi_types = {
            'items': List[WorkItem]
        }

        self.attribute_map = {
            'items': 'items'
        }

        self._items = items

    @classmethod
    def from_dict(cls, dikt) -> 'WorkItemsList':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The WorkItemsList of this WorkItemsList.  # noqa: E501
        :rtype: WorkItemsList
        """
        return util.deserialize_model(dikt, cls)

    @property
    def items(self):
        """Gets the items of this WorkItemsList.


        :return: The items of this WorkItemsList.
        :rtype: List[WorkItem]
        """
        return self._items

    @items.setter
    def items(self, items):
        """Sets the items of this WorkItemsList.


        :param items: The items of this WorkItemsList.
        :type items: List[WorkItem]
        """

        self._items = items
# flake8: noqa
