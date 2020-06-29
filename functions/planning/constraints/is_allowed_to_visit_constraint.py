from ortools.constraint_solver import pywrapcp

from constraints.constraint import Constraint
from data.data_model import DataModel
from node import Node


class IsAllowedToVisitConstraint(Constraint):
    def apply(self, manager:  pywrapcp.RoutingIndexManager, routing: pywrapcp.RoutingModel, data_model: DataModel):
        nodes = data_model.nodes
        engineers = data_model.engineers_to_plan

        for index in range(0, data_model.number_of_nodes):
            if index < data_model.number_of_engineers:
                routing.SetAllowedVehiclesForIndex([index], index)
            else:
                allowed_vehicles = [ind for ind, node in enumerate(engineers) if self.can_visit(data_model, nodes[index], engineers[ind])]
                routing.SetAllowedVehiclesForIndex(allowed_vehicles, index)

        return routing

    def can_visit(self, data_model: DataModel, location_node: Node, engineer):
        role = engineer.get('role', '')

        if 'category' not in location_node.entity:
            return True

        if location_node.entity['category'] == 'Storing':
            if role == 'Metende':
                return True
            if role == 'Lasser':
                return False
        else:
            if role == 'Lasser':
                return True
            if role == 'Metende':
                return False

        return False
