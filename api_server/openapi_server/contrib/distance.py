from geopy import distance


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
        from_coordinates = from_entity['geometry']['coordinates']
        from_coordinates = (from_coordinates[1], from_coordinates[0])
    except KeyError:
        return return_default('from_entity does not contain a valid geometry object')

    try:
        to_coordinates = to_entity['geometry']['coordinates']
        to_coordinates = (to_coordinates[1], to_coordinates[0])
    except KeyError:
        return return_default('to_entity does not contain a valid geometry object')

    return round(distance.distance(from_coordinates, to_coordinates).km, 2)
