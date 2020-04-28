from google.cloud import datastore
import logging


class DBProcessor(object):
    def __init__(self):
        self.client = datastore.Client()
        pass

    def process(self, payload):
        batch = self.client.batch()
        batch.begin()

        for car_information in payload['fleet_drivers']:
            entity = self.get_car_info_for_license(car_information.get('Kenteken'))

            logging.debug('Populate CarInfo {} - {}'.format(entity.key, entity))

            entity.update({
                'driver_name': '{0} {1} {2}'.format(car_information.get('Voorletter', ''),
                                                    car_information.get('Tussenvg', ''),
                                                    car_information.get('Achternaam', ''), ),
                'driver_employee_number': car_information.get('Registratienr', ''),
                'license_plate': car_information.get('Kenteken', ''),
                'division': car_information.get('Afdeling', ''),
            })

            batch.put(entity)

        batch.commit()

    def get_car_info_for_license(self, license):
        car_info = None
        token = None

        # First, we check if a CarInfo for that license already exists.
        query = self.client.query(kind='CarInfo')
        query.add_filter('license_plate', '=', license)
        car_information_list = list(query.fetch())
        if len(car_information_list) > 0:
            car_info = car_information_list[0]

        # Then, we check for CarLocations with the specified license.
        query = self.client.query(kind='CarLocation')
        query.add_filter('license', '=', license)
        car_locations = list(query.fetch())

        # If no CarInfo was found for the specified license, but we did find a CarLocation,
        # we try to cross-reference a CarInfo from the CarLocation token.
        if len(car_locations) > 0 and car_info is None:
            token = car_locations[0].key.id_or_name
            query = self.client.query(kind='CarInfo')
            query.add_filter('token', '=', token)

            car_information_list = list(query.fetch())
            if len(car_information_list) > 0:
                car_info = datastore.Entity(self.client.key('CarInfo'))

        # If we still haven't found a CarInfo, we create a new one.
        if car_info is None:
            car_info = datastore.Entity(self.client.key('CarInfo'))

        # It's possible that we found a CarInfo that should be linked to CarLocation, but still isn't.
        # If this is the case, we create that relationship now.
        if token:
            car_info['token'] = token

        return car_info
