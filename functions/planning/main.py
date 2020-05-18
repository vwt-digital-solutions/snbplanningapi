from __future__ import print_function

import logging

from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp

from data import data_provider
from data.data_model import DataModel

from constraints import PenaltyConstraint, CapacityConstraint, DistanceConstraint


from helpers.distance import calculate_distance_matrix
from process_solution import print_solution, process_solution


def create_data_model() -> DataModel:
    data_model = DataModel()
    data_model.cars = data_provider.get_cars()
    data_model.work_items = data_provider.get_work_items()

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
    logging.debug('Creating datamodel')
    data_model = create_data_model()

    logging.debug('Creating manager')
    manager = pywrapcp.RoutingIndexManager(len(data_model.nodes),
                                           data_model.number_of_cars,
                                           data_model.start_positions,
                                           data_model.end_positions)

    routing = pywrapcp.RoutingModel(manager)

    logging.debug('Applying constraints')
    routing = DistanceConstraint().apply(manager, routing, data_model)
    routing = CapacityConstraint().apply(manager, routing, data_model)
    routing = PenaltyConstraint().apply(manager, routing, data_model)

    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)
    search_parameters.time_limit.seconds = 60

    logging.debug('Calculating solution')
    solution = routing.SolveWithParameters(search_parameters)
    if solution:
        print_solution(data_model, manager, routing, solution)

        return process_solution(data_model, manager, routing, solution)
    else:
        logging.debug('No solution found')
        return []


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
    return generate_planning()


if __name__ == '__main__':
    generate_planning()
