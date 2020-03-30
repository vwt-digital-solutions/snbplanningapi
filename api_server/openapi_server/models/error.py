# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from openapi_server.models.base_model_ import Model
from openapi_server import util


class Error(Model):
    """NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).

    Do not edit the class manually.
    """

    def __init__(self, status=None, detail=None):  # noqa: E501
        """Error - a model defined in OpenAPI

        :param status: The status of this Error.  # noqa: E501
        :type status: str
        :param detail: The detail of this Error.  # noqa: E501
        :type detail: str
        """
        self.openapi_types = {
            'status': str,
            'detail': str
        }

        self.attribute_map = {
            'status': 'status',
            'detail': 'detail'
        }

        self._status = status
        self._detail = detail

    @classmethod
    def from_dict(cls, dikt) -> 'Error':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The Error of this Error.  # noqa: E501
        :rtype: Error
        """
        return util.deserialize_model(dikt, cls)

    @property
    def status(self):
        """Gets the status of this Error.


        :return: The status of this Error.
        :rtype: str
        """
        return self._status

    @status.setter
    def status(self, status):
        """Sets the status of this Error.


        :param status: The status of this Error.
        :type status: str
        """

        self._status = status

    @property
    def detail(self):
        """Gets the detail of this Error.


        :return: The detail of this Error.
        :rtype: str
        """
        return self._detail

    @detail.setter
    def detail(self, detail):
        """Sets the detail of this Error.


        :param detail: The detail of this Error.
        :type detail: str
        """

        self._detail = detail