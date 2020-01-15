# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401
from openapi_server.models.base_model_ import Model
from openapi_server import util

from openapi_server.models.car import Car  # noqa: E501


class Cars(Model):
    """NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).

    Do not edit the class manually.
    """

    def __init__(self, type=None, features=None):  # noqa: E501
        """Cars - a model defined in OpenAPI

        :param type: The type of this Cars.  # noqa: E501
        :type type: str
        :param features: The features of this Cars.  # noqa: E501
        :type features: List[Car]
        """
        self.openapi_types = {
            'type': str,
            'features': List[Car]
        }

        self.attribute_map = {
            'type': 'type',
            'features': 'features'
        }

        self._type = type
        self._features = features

    @classmethod
    def from_dict(cls, dikt) -> 'Cars':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The Cars of this Cars.  # noqa: E501
        :rtype: Cars
        """
        return util.deserialize_model(dikt, cls)

    @property
    def type(self):
        """Gets the type of this Cars.


        :return: The type of this Cars.
        :rtype: str
        """
        return self._type

    @type.setter
    def type(self, type):
        """Sets the type of this Cars.


        :param type: The type of this Cars.
        :type type: str
        """
        if type is None:
            raise ValueError("Invalid value for `type`, must not be `None`")  # noqa: E501

        self._type = type

    @property
    def features(self):
        """Gets the features of this Cars.


        :return: The features of this Cars.
        :rtype: List[Car]
        """
        return self._features

    @features.setter
    def features(self, features):
        """Sets the features of this Cars.


        :param features: The features of this Cars.
        :type features: List[Car]
        """
        if features is None:
            raise ValueError("Invalid value for `features`, must not be `None`")  # noqa: E501

        self._features = features
