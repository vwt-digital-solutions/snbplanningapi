from functions.planning.node import Node, NodeType


class DataModel:
    """ This class serves as a general data model for the planning engine.
    Its main responsibility is keeping track of any input paramaters for the VRP solver.
    For now that includes a list of cars and their start/end locations,
    locations to be visited, the distance matrix between them, their capacity etc.
    """
    cars = []
    work_items = []

    distance_matrix = []

    @property
    def nodes(self) -> [Node]:
        return self.cars + self.work_items

    @property
    def number_of_nodes(self) -> int:
        return len(self.nodes)

    @property
    def number_of_workitems(self) -> int:
        return len(self.work_items)

    @property
    def number_of_cars(self) -> int:
        return len(self.cars)

    @property
    def start_positions(self) -> [int]:
        return list(range(0, self.number_of_cars))

    @property
    def end_positions(self) -> [int]:
        return list(range(0, self.number_of_cars))

    @property
    def demands(self):
        """ Returns the cost for a car to visit a node.
            By setting a capacity for each car, we can assure a maximum number of nodes visited each day.
            Right now, each location visited costs 1.
            Each car has a capacity of 2 (1 in the morning, 1 in the afternoon)
        """
        return [0 if node.type == NodeType.car else 1 for node in self.nodes]

    @property
    def vehicle_capacities(self):
        """
        Returns the capacity for each car i.e. the total number of jobs they can do each day.
        """
        return [2] * self.number_of_cars
