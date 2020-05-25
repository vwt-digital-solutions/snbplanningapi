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
        plan_output = 'Route for vehicle {}:\n'.format(data_model.nodes[vehicle_id].entity.key)
        route_distance = 0
        route_load = 0
        while not routing.IsEnd(index):
            node_index = manager.IndexToNode(index)
            route_load += data_model.demands[node_index]
            plan_output += ' {0} Load({1}) -> '.format(data_model.nodes[node_index].entity.key, route_load)
            previous_index = index
            index = solution.Value(routing.NextVar(index))
            route_distance += routing.GetArcCostForVehicle(
                previous_index, index, vehicle_id)
        plan_output += ' {0} Load({1})\n'.format(manager.IndexToNode(index),
                                                 route_load)
        plan_output += 'Distance of the route: {}m\n'.format(route_distance)
        plan_output += 'Load of the route: {}\n'.format(route_load)
        print(plan_output)
        total_distance += route_distance
        total_load += route_load
    print('Total distance of all routes: {}m'.format(total_distance))
    print('Total load of all routes: {}'.format(total_load))


def process_solution(data_model: DataModel, manager, routing, solution):
    query = db_client.query(kind='CarInfo')
    car_info_list = query.fetch()
    car_info_dict_by_token = {e['token']: e for e in car_info_list}

    entities = []

    for vehicle_id in range(data_model.number_of_cars):
        car_location = data_model.nodes[vehicle_id].entity
        car_info = car_info_dict_by_token[car_location.key.id_or_name]

        index = routing.Start(vehicle_id)

        route_distance = 0
        route_load = 0

        while not routing.IsEnd(index):
            node_index = manager.IndexToNode(index)
            previous_index = index
            index = solution.Value(routing.NextVar(index))

            route_load += data_model.demands[node_index]
            route_distance += routing.GetArcCostForVehicle(previous_index, index, vehicle_id)

            if not data_model.nodes[node_index].type == NodeType.location:
                continue

            entities.append({
                        'engineer': car_info.key.id_or_name,
                        'workitem': data_model.nodes[node_index].entity.key.id_or_name
                      })

    return entities
