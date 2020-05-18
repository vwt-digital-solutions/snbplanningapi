from ortools.constraint_solver import pywrapcp
from constraints.constraint import Constraint
from data.data_model import DataModel

penalty = 40000


class PenaltyConstraint(Constraint):
    def apply(self, manager:  pywrapcp.RoutingModel, routing: pywrapcp.RoutingModel, data_model: DataModel):

        for node in range(1, data_model.number_of_nodes):
            routing.AddDisjunction([manager.NodeToIndex(node)], penalty)

        return routing


# Allow to drop nodes.
