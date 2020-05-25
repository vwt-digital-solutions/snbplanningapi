from enum import Enum

from google.cloud.datastore import Entity


class NodeType(Enum):
    location = 'Location',
    car = 'Car'


class Node:
    type: NodeType
    id: str
    entity: Entity

    def __init__(self, type: NodeType, id: str, entity: Entity):
        self.type = type
        self.id = id
        self.entity = entity
