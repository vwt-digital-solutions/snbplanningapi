from contrib.distance import calculate_travel_times
from google.cloud import datastore
from data.data_model import DataModel
from node import NodeType

db_client = datastore.Client()


def print_solution(data_model: DataModel, manager, routing, solution):
    """Prints solution on console."""
    total_distance = 0
    total_load = 0
    for vehicle_id in range(data_model.number_of_cars):
        index = routing.Start(vehicle_id)
        plan_output = 'Route for vehicle {}:\n'.format(data_model.nodes[vehicle_id].entity['id'])
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


def process_solution(data_model: DataModel, manager, routing, solution, calculate_distance):
    car_info_dict_by_token = data_model.car_info_dict_by_token

    entities = []

    travel_times = []

    for vehicle_id in range(data_model.number_of_cars):
        car_location = data_model.nodes[vehicle_id].entity
        car_info = car_info_dict_by_token[car_location['id']]

        index = routing.Start(vehicle_id)

        route_distance = 0

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
                    travel_time = {
                        'distance': 'NaN',
                        'travel_time': 'NaN'
                     }

                travel_times.append({
                    'engineer': car_info['id'],
                    'euclidean_distance': distance,
                    'from': from_node.entity['id'],
                    'to': to_node.entity['id'],
                    'distance': travel_time['distance'],
                    'travel_time': travel_time['travel_time']
                })

            if to_node.type == NodeType.location:
                entities.append({
                    'engineer': car_info['id'],
                    'workitem': to_node.entity['id'],
                })

    return entities, {'travel_times': travel_times}
