from contrib import distance
from contrib.distance import get_coordinates_from_entity
from node import Node, NodeType

import numpy as np

# Radius of the earth in km (GRS 80-Ellipsoid)
EARTH_RADIUS = 6371.007176
# Value to be used when distance can not be calculated.
INFINITY = 9999999999

""" This module contains helper functions for calculating distance
The contrib.distance function used in the API uses geopy which is notoriously slow.
This is not an issue when doing 1 calculation, but a distance matrix scales very quickly.

Because of this, we use numpy and vectorization to 1. avoid using expensive loops
and 2. delegate the calculation of distance to numpy's internal C functions.

This module uses a haversine distance calculation which is not 100% accurate, but accurate enough in our context.
https://gis.stackexchange.com/questions/296608/what-kind-of-margin-of-error-can-i-expect-in-figuring-distance
"""


def np_distance_on_sphere(coordinate_array):
    """
    Compute a distance matrix of the coordinates using a spherical metric.
    :param coordinate_array: numpy.ndarray with shape (n,2); latitude is in 1st col, longitude in 2nd.
    :returns distance_mat: numpy.ndarray with shape (n, n) containing distance in km between coords.
    """

    # Unpacking coordinates
    latitudes = coordinate_array[:, 0]
    longitudes = coordinate_array[:, 1]

    # Convert latitude and longitude to spherical coordinates in radians.
    degrees_to_radians = np.pi / 180.0
    phi_values = (90.0 - latitudes) * degrees_to_radians
    theta_values = longitudes * degrees_to_radians

    # Expand phi_values and theta_values into grids
    theta_1, theta_2 = np.meshgrid(theta_values, theta_values)
    theta_diff_mat = theta_1 - theta_2

    phi_1, phi_2 = np.meshgrid(phi_values, phi_values)

    # Compute spherical distance from spherical coordinates
    angle = (np.sin(phi_1) * np.sin(phi_2) * np.cos(theta_diff_mat) +
             np.cos(phi_1) * np.cos(phi_2))
    arc = np.arccos(angle)

    # Multiply by earth's radius to obtain distance in km
    return arc * EARTH_RADIUS


def get_coordinates_or_np_nan(entity):
    """ Gets coordinates from an entity. If an exception is raised,
    it means that there are no coordinates for this entity.
    In order to be able to apply numpy functions, we'll need to set them to nan
    """
    try:
        return get_coordinates_from_entity(entity)
    except KeyError:
        return np.nan, np.nan


def calculate_distance_matrix(nodes: [Node]):
    """
    This function calculates a distance matrix for a list of nodes.
    """
    coordinates_array = np.array([get_coordinates_or_np_nan(node.entity) for node in nodes])

    distance_matrix = np_distance_on_sphere(coordinates_array)
    distance_matrix = np.nan_to_num(distance_matrix, nan=INFINITY)

    return distance_matrix


def get_distance(from_node: Node, to_node: Node):
    # Distance from and to the same place is always 0
    if from_node.type == to_node.type and from_node.id == to_node.id:
        return 0

    # Distance from engineer to engineer is always infinity
    if from_node.type == to_node.type == NodeType.car:
        return INFINITY

    return distance.calculate_distance(from_node.entity, to_node.entity)
