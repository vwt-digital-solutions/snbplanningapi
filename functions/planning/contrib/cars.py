import datetime

from google.cloud import datastore


def is_assigned(token, car_tokens, assigned=None):
    """Check if a token had an associated CarInfo or not.

    :param token: The token to check.
    :param assigned: When this value is set to True, check if the token is assigned,
    when set to false, check if the token is not assigned. If assigned is None, always return True
    :param car_tokens: This list of tokens to check against

    :rtype bool

    """
    if assigned is not None:
        return (assigned and token in car_tokens) or (not assigned and token not in car_tokens)

    return True


def get_car_locations(db_client: datastore.Client, assigned_to_engineer=True, offset=None):
    """
    Retrieve a list of carLocations from CarLocations

    :param db_client: The datastore Client.
    :param assigned_to_engineer: Determines wether to return locations linked to a car info object or not.
    :param offset: Maximum number of hours since the CarLocation was last updated.

    :rtype a list of CarLocation entities
    """

    query = db_client.query(kind='CarLocation')

    if offset is not None:
        offset_date = datetime.datetime.utcnow() - datetime.timedelta(hours=offset)
        offset_date = offset_date.isoformat()

        query.add_filter('when', '>=', offset_date)

    query_iter = query.fetch()

    # Filter query on CarInfo tokens
    if assigned_to_engineer:
        engineers_tokens = get_engineers_tokens(db_client)
        query_iter = [car_location for car_location in query_iter
                      if is_assigned(car_location.key.id_or_name, engineers_tokens, True)]
    else:
        query_iter = list(query_iter)

    return query_iter


def get_engineers_tokens(db_client: datastore.Client):
    """Retrieve a list of tokens from CarInfo

    :param db_client: The datastore Client.

    :rtype a list of strings

    """
    engineers_query = db_client.query(kind='Engineer')

    car_tokens = [engineer['token'] for
                  engineer in engineers_query.fetch()
                  if 'token' in engineer and engineer['token'] is not None and len(engineer['token']) > 0]

    return car_tokens
