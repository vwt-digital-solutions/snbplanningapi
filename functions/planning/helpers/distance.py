from contrib import distance
from .node import Node, NodeType

INFINITY = 9999999999


def calculate_distance_matrix(nodes: [Node]):
    distance_matrix = [
        [get_distance(x, y) for y in nodes]
        for x in nodes
    ]
    return distance_matrix


def get_distance(from_node: Node, to_node: Node):

    # Distance from one place to another is always 0
    if from_node.type == to_node.type and from_node.id == to_node.id:
        return 0

    # Distance from engineer to engineer is always infinity
    if from_node.type == to_node.type == NodeType.car:
        return INFINITY

    return distance.calculate_distance(from_node.entity, to_node.entity)
