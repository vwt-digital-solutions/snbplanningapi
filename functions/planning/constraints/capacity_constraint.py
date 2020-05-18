from ortools.constraint_solver import pywrapcp
from functions.planning.constraints.constraint import Constraint
from functions.planning.data.data_model import DataModel


class CapacityConstraint(Constraint):
    def apply(self, manager:  pywrapcp.RoutingModel, routing: pywrapcp.RoutingModel, data_model: DataModel):
        def demand_callback(from_index):
            """Returns the demand of the node."""
            # Convert from routing variable Index to demands NodeIndex.
            from_node = manager.IndexToNode(from_index)
            return data_model.demands[from_node]

        demand_callback_index = routing.RegisterUnaryTransitCallback(
            demand_callback)
        routing.AddDimensionWithVehicleCapacity(
            demand_callback_index,
            0,  # null capacity slack
            data_model.vehicle_capacities,
            True,  # start cumul to zero
            'Capacity')

        return routing
