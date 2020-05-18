from abc import abstractmethod, ABC

from ortools.constraint_solver import pywrapcp
from functions.planning.data.data_model import DataModel


class Constraint(ABC):
    @abstractmethod
    def apply(self, manager:  pywrapcp.RoutingModel, model: pywrapcp.RoutingModel, data_model: DataModel):
        pass
