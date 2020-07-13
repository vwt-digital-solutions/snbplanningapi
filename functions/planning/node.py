from enum import Enum

from google.cloud.datastore import Entity


class NodeType(Enum):
    location = 'Location',
    car = 'CarLocation'
    engineer = 'EngineerAddress'


class Node:
    type: NodeType
    id: str
    entity: Entity
    distance_matrix_index: int

    def __init__(self, type: NodeType, id: str, entity: Entity, distance_matrix_index: int):
        self.type = type
        self.id = id
        self.entity = entity
        self.distance_matrix_index = distance_matrix_index
