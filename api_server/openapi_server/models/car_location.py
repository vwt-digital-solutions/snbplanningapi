# coding: utf-8
# flake8: noqa

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from openapi_server.models.base_model_ import Model
from openapi_server.models.geometry import Geometry
from openapi_server import util

from openapi_server.models.geometry import Geometry  # noqa: E501

class CarLocation(Model):
    """NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).

    Do not edit the class manually.
    """

    def __init__(self, geometry=None, type=None, properties=None):  # noqa: E501
        """CarLocation - a model defined in OpenAPI

        :param geometry: The geometry of this CarLocation.  # noqa: E501
        :type geometry: Geometry
        :param type: The type of this CarLocation.  # noqa: E501
        :type type: str
        :param properties: The properties of this CarLocation.  # noqa: E501
        :type properties: object
        """
        self.openapi_types = {
            'geometry': Geometry,
            'type': str,
            'properties': object
        }

        self.attribute_map = {
            'geometry': 'geometry',
            'type': 'type',
            'properties': 'properties'
        }

        self._geometry = geometry
        self._type = type
        self._properties = properties

    @classmethod
    def from_dict(cls, dikt) -> 'CarLocation':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The CarLocation of this CarLocation.  # noqa: E501
        :rtype: CarLocation
        """
        return util.deserialize_model(dikt, cls)

    @property
    def geometry(self):
        """Gets the geometry of this CarLocation.


        :return: The geometry of this CarLocation.
        :rtype: Geometry
        """
        return self._geometry

    @geometry.setter
    def geometry(self, geometry):
        """Sets the geometry of this CarLocation.


        :param geometry: The geometry of this CarLocation.
        :type geometry: Geometry
        """
        if geometry is None:
            raise ValueError("Invalid value for `geometry`, must not be `None`")  # noqa: E501

        self._geometry = geometry

    @property
    def type(self):
        """Gets the type of this CarLocation.


        :return: The type of this CarLocation.
        :rtype: str
        """
        return self._type

    @type.setter
    def type(self, type):
        """Sets the type of this CarLocation.


        :param type: The type of this CarLocation.
        :type type: str
        """
        if type is None:
            raise ValueError("Invalid value for `type`, must not be `None`")  # noqa: E501

        self._type = type

    @property
    def properties(self):
        """Gets the properties of this CarLocation.


        :return: The properties of this CarLocation.
        :rtype: object
        """
        return self._properties

    @properties.setter
    def properties(self, properties):
        """Sets the properties of this CarLocation.


        :param properties: The properties of this CarLocation.
        :type properties: object
        """
        if properties is None:
            raise ValueError("Invalid value for `properties`, must not be `None`")  # noqa: E501

        self._properties = properties
