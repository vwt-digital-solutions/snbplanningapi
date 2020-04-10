# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from openapi_server.models.base_model_ import Model
from openapi_server.models.work_item import WorkItem
from openapi_server import util

from openapi_server.models.work_item import WorkItem  # noqa: E501

class WorkItems(Model):
    """NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).

    Do not edit the class manually.
    """

    def __init__(self, items=None):  # noqa: E501
        """WorkItems - a model defined in OpenAPI

        :param items: The items of this WorkItems.  # noqa: E501
        :type items: WorkItem
        """
        self.openapi_types = {
            'items': WorkItem
        }

        self.attribute_map = {
            'items': 'items'
        }

        self._items = items

    @classmethod
    def from_dict(cls, dikt) -> 'WorkItems':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The WorkItems of this WorkItems.  # noqa: E501
        :rtype: WorkItems
        """
        return util.deserialize_model(dikt, cls)

    @property
    def items(self):
        """Gets the items of this WorkItems.


        :return: The items of this WorkItems.
        :rtype: WorkItem
        """
        return self._items

    @items.setter
    def items(self, items):
        """Sets the items of this WorkItems.


        :param items: The items of this WorkItems.
        :type items: WorkItem
        """

        self._items = items
# flake8: noqa
