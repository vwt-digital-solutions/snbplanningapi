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

    def is_available(self, data_model: DataModel, location_node: Node, engineer):
        availability = data_model.availabilities.get(engineer['id'], None)

        # No availability found for engineer - Assume engineer is available.
        if availability is None:
            return True

        work_item_start_time = location_node.entity.get('start_timestamp', None)
        work_item_end_time = location_node.entity.get('end_timestamp', None)

        # Workitem does not have a start and end time. Assume workitem can be addressed at anytime of the day.
        # This means it doesn't really matter if an employee is available for them to be available.
        if not work_item_start_time or not work_item_end_time:
            return True

        shift_start_time = availability.get('shift_start_date', None)
        shift_end_time = availability.get('shift_end_date', None)
        if not shift_start_time or not shift_end_time:
            return True

        # Some older workitems have strings as timestamps instead of datetimes.
        # We could convert them to dates, but this is not really a robust implementation.
        # Instead, we must ensure work_items always have a datetime as their timestamps.
        # If this is not the case, skip them.
        try:
            if shift_start_time <= work_item_start_time and shift_end_time >= work_item_end_time:
                # Check for overlapping appointments.
                for appointment in availability.get('appointments', []):
                    appointment_start_time = appointment.get('start_date', None)
                    appointment_end_time = appointment.get('end_date', None)
                    if appointment_end_time >= work_item_start_time and \
                       work_item_end_time >= appointment_start_time:
                        return False
                return True
            else:
                return False
        except TypeError:
            return False

    def can_visit(self, data_model: DataModel, location_node: Node, engineer):
        role = engineer.get('role', '')

        if 'category' not in location_node.entity:
            return self.is_available(data_model, location_node, engineer)

        if location_node.entity['category'] == 'Storing':
            if role == 'Metende':
                return self.is_available(data_model, location_node, engineer)
            if role == 'Lasser':
                return False
        else:
            if role == 'Lasser':
                return self.is_available(data_model, location_node, engineer)
            if role == 'Metende':
                return False

        return False
