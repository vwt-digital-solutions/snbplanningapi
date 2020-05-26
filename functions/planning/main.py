from __future__ import print_function

import config
from constraints.is_allowed_to_visit_constraint import IsAllowedToVisitConstraint
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp

from data import data_provider
from data.data_model import DataModel

from constraints import PenaltyConstraint, CapacityConstraint, DistanceConstraint


from helpers.distance import calculate_distance_matrix
from process_solution import process_solution, print_solution


def create_data_model() -> DataModel:
    data_model = DataModel()
    print('getting Cars')
    data_model.cars = data_provider.get_cars()
    print('getting Workitems')
    data_model.work_items = data_provider.get_work_items()
    print('getting CarInfo')
    data_model.car_info_list = data_provider.get_car_info()
    data_model.car_info_dict_by_token = {e['token']: e for e in data_model.car_info_list}

    print(data_model.number_of_cars, ' cars')
    print(data_model.number_of_workitems, ' workitems')

    print('Calculating distance matrix')
    data_model.distance_matrix = calculate_distance_matrix(data_model.nodes)

    return data_model


def generate_planning():
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
    try:

        print('Debug is set to: ', config.PLANNING_ENGINE_DEBUG)
        if config.PLANNING_ENGINE_DEBUG:
            print('Will use only a subset of workitems and employees.')
    except AttributeError:
        print('Debug not set')
        print('Will use the full set of workitems and employees.')

    print('Creating datamodel')
    data_model = create_data_model()

    print('Creating manager')
    manager = pywrapcp.RoutingIndexManager(len(data_model.nodes),
                                           data_model.number_of_cars,
                                           data_model.start_positions,
                                           data_model.end_positions)

    routing = pywrapcp.RoutingModel(manager)

    print('Applying constraints')
    routing = DistanceConstraint().apply(manager, routing, data_model)
    routing = CapacityConstraint().apply(manager, routing, data_model)
    routing = PenaltyConstraint().apply(manager, routing, data_model)
    routing = IsAllowedToVisitConstraint().apply(manager, routing, data_model)

    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)
    search_parameters.time_limit.seconds = 20

    print('Calculating solutions')
    solution = routing.SolveWithParameters(search_parameters)
    print('Solution calculated')
    if solution:
        print('Processing solution')
        print_solution(data_model, manager, routing, solution)
        value = process_solution(data_model, manager, routing, solution)
    else:
        print('No solution found')
        value = 'No response'

    return value


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

    return {
        'result': generate_planning()
    }


if __name__ == '__main__':
    generate_planning()
