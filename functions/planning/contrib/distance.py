import googlemaps

from geopy import distance

import config


def get_coordinates_from_entity(entity):
    coordinates = entity['geometry']['coordinates']
    coordinates = (coordinates[1], coordinates[0])

    return coordinates


def calculate_distance(from_entity, to_entity, default_distance=40000, silence_exception=True):
    """
    Calculates the euclidean distance between two DataStore Entities. (Or other dictionaries.)
    Entities should have a dictionary called geometry, which should in turn contain an iterable coordinates,
    containing two coordinates in the order longitude, latitude.

    {
            ...
            'geometry' : {
                'coordinates' : (long,lat)
            }
    }


    :return The distance in km, rounded to two decimals.
    Will return the default distance when either of the entities is not formatted correctly,
    or when one of the coordinates is invalid.

    :raises Will raise a ValueException instead of returning the default distance if silence_exception is set to false.
    """

    def return_default(*args, **kwargs):
        if silence_exception:
            return default_distance
        else:
            raise ValueError(*args, **kwargs)

    try:
        from_coordinates = get_coordinates_from_entity(from_entity)
    except KeyError:
        return return_default('from_entity does not contain a valid geometry object')

    try:
        to_coordinates = get_coordinates_from_entity(to_entity)
    except KeyError:
        return return_default('to_entity does not contain a valid geometry object')

    return distance.distance(from_coordinates, to_coordinates).km


def calculate_travel_times(to_entity, from_entities):
    """
        Uses the Google Maps Distance Matrix API to determine travel times from each of the specified from_entity,
        to the to_entity.
        Entities should have a dictionary called geometry, which should in turn contain an iterable coordinates,
        containing two coordinates in the order longitude, latitude.

        {
                ...
                'geometry' : {
                    'coordinates' : (long,lat)
                }
        }


        :return The distance in km, rounded to two decimals.
        Will return the default distance when either of the entities is not formatted correctly,
        or when one of the coordinates is invalid.
        """

    if hasattr(config, 'DISTANCE_MATRIX_API_KEY'):
        gmaps = googlemaps.Client(config.DISTANCE_MATRIX_API_KEY)
    else:
        raise NotImplementedError('Distance matrix API key is missing')

    to_coordinate = get_coordinates_from_entity(to_entity)
    from_coordinates = [get_coordinates_from_entity(entity) for entity in from_entities]

    result = gmaps.distance_matrix(from_coordinates, to_coordinate)

    distances = []

    for index, value in enumerate(result['rows']):
        element = value['elements'][0]
        distances.append({
            'token': from_entities[index]['id'],
            'distance': round(element['distance']['value'] / 1000, 2),
            'travel_time': element['duration']['value']
        })

    return distances
