from contrib.distance import calculate_travel_times
from data.data_model import DataModel
from node import NodeType

from google.cloud import datastore

db_client = datastore.Client()


def print_solution(data_model: DataModel, manager, routing, solution):
    """Prints solution on console."""
    total_distance = 0
    total_load = 0
    for vehicle_id in range(data_model.number_of_engineers):
        index = routing.Start(vehicle_id)
        plan_output = 'Route for engineer {}:\n'.format(data_model.nodes[vehicle_id].entity['id'])
        route_distance = 0
        route_load = 0
        while not routing.IsEnd(index):
            node_index = manager.IndexToNode(index)
            route_load += data_model.demands[node_index]
            plan_output += ' {0} Load({1}) -> '.format(data_model.nodes[node_index].entity['id'], route_load)
            previous_index = index
            index = solution.Value(routing.NextVar(index))
            route_distance += routing.GetArcCostForVehicle(
                previous_index, index, vehicle_id)
        plan_output += ' {0} Load({1})\n'.format(manager.IndexToNode(index),
                                                 route_load)
        plan_output += 'Distance of the route: {} km\n'.format(route_distance)
        plan_output += 'Load of the route: {}\n'.format(route_load)
        print(plan_output)
        total_distance += route_distance
        total_load += route_load
    print('Total distance of all routes: {} km'.format(total_distance))
    print('Total load of all routes: {}'.format(total_load))


def process_solution(data_model: DataModel, manager, routing, solution, calculate_distance, verbose=False):
    if verbose:
        print_solution(data_model, manager, routing, solution)
    planned_workitems = []
    travel_times = []

    # Construct a set here, so that we can build unplanned work_items in O(n) time instead of O(n^2)
    planned_workitems_set = set()
    unplanned_engineers = data_model.unplanned_engineers

    for vehicle_id in range(data_model.number_of_engineers):
        engineer = data_model.engineers[vehicle_id].entity

        index = routing.Start(vehicle_id)

        route_distance = 0

        engineer_is_planned = False
        while not routing.IsEnd(index):
            from_index = manager.IndexToNode(index)
            index = solution.Value(routing.NextVar(index))
            to_index = manager.IndexToNode(index)

            distance = routing.GetArcCostForVehicle(from_index, to_index, vehicle_id)
            route_distance += distance

            from_node = data_model.nodes[from_index]
            to_node = data_model.nodes[to_index]

            if calculate_distance:
                try:
                    travel_time = calculate_travel_times(to_node.entity, [from_node.entity])[0]
                except KeyError:
                    # TODO: This error occurs when either of the two nodes don't have a valid geometry.
                    #  We should try to avoid working with unknown locations, since it can throw off the planning.
                    travel_time = {
                        'distance': 'NaN',
                        'travel_time': 'NaN'
                     }

                travel_times.append({
                    'engineer': engineer['id'],
                    'euclidean_distance': distance,
                    'from': from_node.entity['id'],
                    'to': to_node.entity['id'],
                    'distance': travel_time['distance'],
                    'travel_time': travel_time['travel_time']
                })

            if to_node.type == NodeType.location:
                planned_workitems_set.add(to_node.entity['id'])
                engineer_is_planned = True
                planned_workitems.append({
                    'engineer': engineer['id'],
                    'workitem': to_node.entity['id'],
                })

        if not engineer_is_planned:
            unplanned_engineers.append(engineer['id'])

    unplanned_workitems = [work_item.entity['id'] for work_item in
                           data_model.all_work_items
                           if work_item.entity['id'] not in planned_workitems_set]

    return planned_workitems, unplanned_engineers, unplanned_workitems, {'travel_times': travel_times}
