from node import NodeType
from ortools.constraint_solver import pywrapcp
from constraints.constraint import Constraint
from data.data_model import DataModel

default_penalty = 1000


class PenaltyConstraint(Constraint):
    def apply(self, manager:  pywrapcp.RoutingIndexManager, routing: pywrapcp.RoutingModel, data_model: DataModel):
        for node_index in range(0, data_model.number_of_nodes):
            penalty = default_penalty

            node = data_model.nodes[node_index]

            if node.type == NodeType.location:
                penalty = node.entity['priority'] * default_penalty

            routing.AddDisjunction([manager.NodeToIndex(node_index)], penalty)

        return routing
