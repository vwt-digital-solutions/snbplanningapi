from ortools.constraint_solver import pywrapcp

from constraints.constraint import Constraint
from data.data_model import DataModel
from node import Node


class IsAllowedToVisitConstraint(Constraint):
    def apply(self, manager:  pywrapcp.RoutingIndexManager, routing: pywrapcp.RoutingModel, data_model: DataModel):
        nodes = data_model.nodes
        cars = data_model.cars

        for index in range(0, data_model.number_of_nodes):
            if index < data_model.number_of_cars:
                routing.SetAllowedVehiclesForIndex([index], index)
            else:
                allowed_vehicles = [ind for ind, node in enumerate(cars) if self.can_visit(data_model, nodes[index], cars[ind])]
                routing.SetAllowedVehiclesForIndex(allowed_vehicles, index)

        return routing

    def can_visit(self, data_model: DataModel, location_node: Node, car_node: Node):
        engineer = data_model.engineers_dict_by_token[car_node.entity['id']]
        role = engineer.get('role', '')

        return True

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
