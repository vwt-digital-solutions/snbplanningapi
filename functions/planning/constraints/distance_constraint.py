from ortools.constraint_solver import pywrapcp
from constraints.constraint import Constraint
from data.data_model import DataModel


class DistanceConstraint(Constraint):
    def apply(self, manager:  pywrapcp.RoutingModel, routing: pywrapcp.RoutingModel, data_model: DataModel):
        def distance_callback(from_index, to_index):
            """Returns the distance between the two nodes."""
            # Convert from routing variable Index to distance matrix NodeIndex.
            from_node = manager.IndexToNode(from_index)
            to_node = manager.IndexToNode(to_index)
            return data_model.distance_matrix[from_node][to_node]

        transit_callback_index = routing.RegisterTransitCallback(distance_callback)
        routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

        dimension_name = 'Distance'
        routing.AddDimension(
            transit_callback_index,
            0,  # no slack
            3000,  # vehicle maximum travel distance
            True,  # start cumul to zero
            dimension_name)
        distance_dimension = routing.GetDimensionOrDie(dimension_name)
        distance_dimension.SetGlobalSpanCostCoefficient(100)

        for i in range(data_model.number_of_cars):
            routing.AddVariableMinimizedByFinalizer(
                distance_dimension.CumulVar(routing.Start(i)))
            routing.AddVariableMinimizedByFinalizer(
                distance_dimension.CumulVar(routing.End(i)))

        return routing
