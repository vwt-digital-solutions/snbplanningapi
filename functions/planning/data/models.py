from node import Node


class TravelTime:
    engineer: str
    from_node: Node
    to_node: Node
    euclidean_distance: int
    travel_time: int
    distance: float

    def __init__(self, engineer: str, from_node: Node, to_node: Node,
                 euclidean_distance: int, distance: float, travel_time: int):
        self.engineer = engineer
        self.from_node = from_node
        self.to_node = to_node
        self.euclidean_distance = euclidean_distance
        self.travel_time = travel_time
        self.distance = distance


class PlanningItem:
    engineer: str
    workitem: str

    def __init__(self, engineer, workitem):
        self.engineer = engineer
        self.workitem = workitem


class MetaData:
    travel_times: [TravelTime]

    def __init__(self, travel_times=[]):
        self.travel_times = travel_times


class Planning:
    result: [PlanningItem]
    unplanned_engineers: [str]
    unplanned_workitems: [str]
    metadata: MetaData

    def __init__(self, result: [PlanningItem], unplanned_engineers: [str],
                 unplanned_workitems: [str], metadata: MetaData):
        self.result = result
        self.unplanned_engineers = unplanned_engineers
        self.unplanned_workitems = unplanned_workitems
        self.metadata = metadata
