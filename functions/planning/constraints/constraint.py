from abc import abstractmethod, ABC

from ortools.constraint_solver import pywrapcp
from .data.data_model import DataModel


class Constraint(ABC):
    @abstractmethod
    def apply(self, manager:  pywrapcp.RoutingModel, model: pywrapcp.RoutingModel, data_model: DataModel):
        pass
