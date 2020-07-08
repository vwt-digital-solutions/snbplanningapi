from node import Node, NodeType

from datetime import datetime
import dateutil.parser


class DataModel:
    """ This class serves as a general data model for the planning engine.
    Its main responsibility is keeping track of any input paramaters for the VRP solver.
    For now that includes a list of cars and their start/end locations,
    locations to be visited, the distance matrix between them, their capacity etc.
    """

    engineers: []
    work_items: []
    car_locations: []
    availabilities: {}

    preplanned_work_items = []
    work_items_to_plan = []

    preplanned_engineers = []
    engineers_to_plan = []
    unplannable_engineers = []

    distance_matrix = []

    _nodes = None

    def __init__(self, engineers: [], work_items: [], car_locations: [], availabilities: {}):
        self.engineers = engineers
        self.work_items = work_items
        self.car_locations = car_locations
        self.availabilities = availabilities

        self.prioritize_work_items()
        self.filter_engineers()

    def set_priority_for_workitem(self, work_item):
        if 'dgs' in work_item and work_item['dgs']:
            priority = 5
        elif 'task_type' in work_item and 'Premium' in work_item['task_type']:
            priority = 4
        elif 'category' in work_item and work_item['category'] == 'Storing':
            priority = 3
        elif 'category' in work_item and work_item['category'] == 'Schade':
            priority = 2
        else:
            priority = 1

        work_item['priority'] = priority

        return work_item

    def convert_to_date_or_none(self, date_to_convert):
        if isinstance(date_to_convert, datetime):
            return date_to_convert
        if isinstance(date_to_convert, str):
            try:
                return dateutil.parser.isoparse(date_to_convert)
            except ValueError:
                # Invalid date string
                return None
            except OverflowError:
                # Date is bigger than largest int
                return None
        return None

    def prioritize_work_items(self):
        """ The algorithm can run into some issues when there are is a disproportionate amount of workitems
         compared to the number of engineers. This function will add a priority value to every workitem,
         sort them by priority, and only return the most urgent workitems.
        """
        self.work_items = [self.set_priority_for_workitem(work_item) for work_item in self.work_items]
        work_items_to_plan = [work_item for work_item in self.work_items if work_item['status'] == 'Te Plannen']

        engineer_ids = [engineer['id'] for engineer in self.engineers]

        self.preplanned_work_items = [{
            'engineer': work_item['employee_number'],
            'workitem': work_item['id'],
        } for work_item in self.work_items if work_item['status'] == 'Niet Gereed'
                                              and work_item['employee_number'] in engineer_ids]

        work_items_storing = [work_item for work_item in work_items_to_plan if
                              work_item.get('category', None) == 'Schade']
        work_items_schade = [work_item for work_item in work_items_to_plan if
                             work_item.get('category', None) == 'Storing']
        other_work_items = [work_item for work_item in work_items_to_plan if
                            work_item.get('category', None) != 'Storing' and
                            work_item.get('category', None) != 'Schade']

        engineers_schade = [engineer for engineer in self.engineers if engineer.get('role', None) == 'Lasser']
        engineers_storing = [engineer for engineer in self.engineers if engineer.get('role', None) == 'Metende']

        work_items_schade = sorted(work_items_schade,
                                   key=lambda i: (-i['priority'],
                                                  self.convert_to_date_or_none(
                                                      i['resolve_before_timestamp']) is None,
                                                  self.convert_to_date_or_none(i['resolve_before_timestamp'])
                                                  ))
        work_items_storing = sorted(work_items_storing,
                                    key=lambda i: (-i['priority'],
                                                   self.convert_to_date_or_none(i['start_timestamp']) is None,
                                                   self.convert_to_date_or_none(i['start_timestamp'])))

        self.work_items_to_plan = work_items_schade[:len(engineers_schade) * 2] + \
            work_items_storing[:len(engineers_storing) * 2] + \
            other_work_items

    def filter_engineers(self):
        def engineer_is_plannable(engineer):
            if 'geometry' not in engineer or engineer['geometry'] is None:
                return False
            if 'role' not in 'role' not in engineer or engineer['role'] not in ['Metende', 'Lasser']:
                return False
            # TODO: Normally, we'd filter out any engineer that does not have a defined availability.
            #  Right now, availabilities are somewhat broken, so we leave this out and instead assume
            #  every engineer is available at all times.
            #
            # if not self.availabilities.get(engineer['id'], False):
            #     return False

            return True

        self.unplannable_engineers = [engineer for engineer in self.engineers if not engineer_is_plannable(engineer)]

        preplanned_engineer_ids = [planning_item.get('engineer', None) for
                                   planning_item in self.preplanned_work_items]
        self.preplanned_engineers = [engineer for engineer in self.engineers if engineer['id']
                                     in preplanned_engineer_ids]

        self.engineers_to_plan = [engineer for engineer in self.engineers
                                  if engineer not in self.preplanned_engineers and
                                  engineer not in self.unplannable_engineers]

    # Properties

    @property
    def nodes(self) -> [Node]:
        if not self._nodes or \
                len(self._nodes) != self.number_of_engineers + self.number_of_workitems:
            self._nodes = \
                [Node(NodeType.engineer, engineer['id'], engineer) for engineer in self.engineers_to_plan] + \
                [Node(NodeType.location, work_item['id'], work_item) for work_item in self.work_items_to_plan]
        return self._nodes

    @property
    def number_of_nodes(self) -> int:
        return len(self.nodes)

    @property
    def number_of_workitems(self) -> int:
        return len(self.work_items_to_plan)

    @property
    def number_of_engineers(self) -> int:
        return len(self.engineers_to_plan)

    @property
    def start_positions(self) -> [int]:
        return list(range(0, self.number_of_engineers))

    @property
    def end_positions(self) -> [int]:
        return list(range(0, self.number_of_engineers))

    @property
    def demands(self):
        """ Returns the cost for a car to visit a node.
            By setting a capacity for each car, we can assure a maximum number of nodes visited each day.
            Right now, each location visited costs 1.
            Each car has a capacity of 1 (Since the current planning is for mornings only.)
        """
        return [1 if node.type == NodeType.location else 0 for node in self.nodes]

    @property
    def vehicle_capacities(self):
        """
        Returns the capacity for each car i.e. the total number of jobs they can do each day.
        """
        return [1] * self.number_of_engineers
