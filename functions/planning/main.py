from __future__ import print_function

from datetime import datetime

from constraints.is_allowed_to_visit_constraint import IsAllowedToVisitConstraint
from flask import json
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp

from data import data_provider
from data.data_model import DataModel

from constraints import PenaltyConstraint, CapacityConstraint, DistanceConstraint

from helpers.distance import calculate_distance_matrix
from process_solution import process_solution


def create_data_model(engineers=None, car_locations=None, work_items=None, availabilities=None) -> DataModel:
    work_items = data_provider.get_work_items(work_items)
    engineers = data_provider.get_engineers(engineers)
    availabilities = data_provider.get_availabilities(availabilities)
    car_locations = []

    data_model = DataModel(engineers=engineers, work_items=work_items,
                           car_locations=car_locations, availabilities=availabilities)
    print(data_model.number_of_engineers, ' engineers')
    print(data_model.number_of_workitems, ' workitems')

    print('Calculating distance matrix')
    data_model.distance_matrix = calculate_distance_matrix(data_model.nodes)

    return data_model


def generate_planning(timeout, verbose, calculate_distance,
                      engineers=None, car_locations=None, work_items=None, availabilities=None):
    """
    The main planning function. This function does the following:
        - Create a datamodel for the routing manager to reference.
        - Create a routing manager.
        - Add constraints based on business rules.
        - Calculate an optimal solution withing a given timeframe.
        - Log the solution.
        - Returns a list of engineers and workitems.
    :return:
    """
    print("Timeout set to", timeout)
    print('Creating datamodel')
    data_model = create_data_model(engineers, car_locations, work_items, availabilities)

    print('Creating manager')
    manager = pywrapcp.RoutingIndexManager(data_model.number_of_nodes,
                                           data_model.number_of_engineers,
                                           data_model.start_positions,
                                           data_model.end_positions)

    routing = pywrapcp.RoutingModel(manager)

    print('Applying constraints')
    routing = DistanceConstraint().apply(manager, routing, data_model)
    routing = CapacityConstraint().apply(manager, routing, data_model)
    routing = PenaltyConstraint().apply(manager, routing, data_model)
    routing = IsAllowedToVisitConstraint().apply(manager, routing, data_model)

    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.local_search_metaheuristic = routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
    search_parameters.time_limit.seconds = timeout

    datetime.now().strftime("%H:%M:%S")
    print("date and time: ", datetime.now().strftime("%H:%M:%S"))

    def record_solution():
        print("date and time: ", datetime.now().strftime("%H:%M:%S"))
        print(routing.CostVar().Max())

    routing.AddAtSolutionCallback(record_solution)

    print('Calculating solutions')
    solution = routing.SolveWithParameters(search_parameters)
    # solution = routing.SolveFromAssignmentWithParameters(
    #    initial_solution, search_parameters)
    print(solution.ObjectiveValue())
    print('Solution calculated')
    if solution:
        print('Processing solution')
        planning = process_solution(data_model, manager, routing, solution, calculate_distance)
        return planning
    else:
        print('No solution found')

        return [], [engineer['id'] for engineer in data_model.engineers], \
               [work_item['id'] for work_item in data_model.work_items], {}


def perform_request(request):
    """HTTP Cloud Function.
    Args:
        request (flask.Request): The request object.
        <http://flask.pocoo.org/docs/1.0/api/#flask.Request>
    Returns:
        The response text, or any set of values that can be turned into a
        Response object using `make_response`
        <http://flask.pocoo.org/docs/1.0/api/#flask.Flask.make_response>.
    """

    request_json = request.get_json(silent=True)

    if not request_json:
        request_json = {}

    timeout = request_json.get('timeout', 60)
    verbose = request_json.get('verbose', False)
    calculate_distance = request_json.get('calculate_distances', False)
    engineers = request_json.get('engineers', None)
    car_locations = request_json.get('car_locations', None)
    work_items = request_json.get('work_items', None)
    availabilities = request_json.get('availabilities', None)

    result, unplanned_engineers, unplanned_work_items, metadata = generate_planning(timeout,
                                                                                    verbose,
                                                                                    calculate_distance,
                                                                                    engineers=engineers,
                                                                                    car_locations=car_locations,
                                                                                    work_items=work_items,
                                                                                    availabilities=availabilities)

    return json.dumps({
        'result': result,
        'unplanned_engineers': unplanned_engineers,
        'unplanned_workitems': unplanned_work_items,
        'metadata': metadata
    })


if __name__ == '__main__':
    generate_planning(20, True, False)

    """
    with open('tests/data/engineers.json') as json_file:
        engineers = json.load(json_file)

    with open('tests/data/workitems.json') as json_file:
        work_items = json.load(json_file)

    with open('tests/data/carlocations.json') as json_file:
        car_locations = json.load(json_file)

    generate_planning(20, True, False, work_items=work_items, car_locations=car_locations, engineers=engineers)
    """
