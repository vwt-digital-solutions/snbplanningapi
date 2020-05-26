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
        car_info = data_model.car_info_dict_by_token[car_node.entity.key.id_or_name]
        driver_skill = car_info.get('driver_skill', '')

        if 'category' not in location_node.entity:
            return True

        if location_node.entity['category'] == 'Storing':
            if driver_skill == 'Metende':
                return True
            if driver_skill == 'Lasser':
                return False
        else:
            if driver_skill == 'Lasser':
                return True
            if driver_skill == 'Metende':
                return False
        return True
