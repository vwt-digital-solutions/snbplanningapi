# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from openapi_server.models.base_model_ import Model
from openapi_server.models.engineer import Engineer
from openapi_server import util

from openapi_server.models.engineer import Engineer  # noqa: E501

class EngineersList(Model):
    """NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).

    Do not edit the class manually.
    """

    def __init__(self, links=None, items=None):  # noqa: E501
        """EngineersList - a model defined in OpenAPI

        :param links: The links of this EngineersList.  # noqa: E501
        :type links: object
        :param items: The items of this EngineersList.  # noqa: E501
        :type items: List[Engineer]
        """
        self.openapi_types = {
            'links': object,
            'items': List[Engineer]
        }

        self.attribute_map = {
            'links': '_links',
            'items': 'items'
        }

        self._links = links
        self._items = items

    @classmethod
    def from_dict(cls, dikt) -> 'EngineersList':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The EngineersList of this EngineersList.  # noqa: E501
        :rtype: EngineersList
        """
        return util.deserialize_model(dikt, cls)

    @property
    def links(self):
        """Gets the links of this EngineersList.


        :return: The links of this EngineersList.
        :rtype: object
        """
        return self._links

    @links.setter
    def links(self, links):
        """Sets the links of this EngineersList.


        :param links: The links of this EngineersList.
        :type links: object
        """

        self._links = links

    @property
    def items(self):
        """Gets the items of this EngineersList.


        :return: The items of this EngineersList.
        :rtype: List[Engineer]
        """
        return self._items

    @items.setter
    def items(self, items):
        """Sets the items of this EngineersList.


        :param items: The items of this EngineersList.
        :type items: List[Engineer]
        """
        if items is None:
            raise ValueError("Invalid value for `items`, must not be `None`")  # noqa: E501

        self._items = items
# flake8: noqa
