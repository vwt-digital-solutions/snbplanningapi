from __future__ import absolute_import

from flask import json
import adal
import config
from openapi_server.test import BaseTestCase


def get_token():
    """
    Create a token for testing
    :return:
    """
    oauth_expected_authenticator = config.OAUTH_E2E_AUTHORITY_URI
    client_id = config.OAUTH_E2E_APPID
    client_secret = config.OAUTH_E2E_CLIENT_SECRET
    resource = config.OAUTH_E2E_EXPECTED_AUDIENCE

    # get an Azure access token using the adal library
    context = adal.AuthenticationContext(oauth_expected_authenticator)
    token_response = context.acquire_token_with_client_credentials(
        resource, client_id, client_secret)

    access_token = token_response.get('accessToken')
    return access_token


class TestDefaultController(BaseTestCase):
    """DefaultController integration test stubs"""

    def test_car_distances_list(self):
        """Test case for car_distances_list

        Get car distances from a point or workitem
        """
        query_string = [('cars', 'cars_example'),
                        ('offset', 168),
                        ('sort', 'travel_time'),
                        ('limit', 3)]
        headers = {
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + get_token(),
        }
        response = self.client.open(
            '/workitem/{0}/distances'.format('work_item_example'),
            method='GET',
            headers=headers,
            query_string=query_string)
        self.assert404(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_car_locations_list(self):
        """Test case for car_locations_list

        Get car locations
        """
        query_string = [('offset', 168)]
        headers = {
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + get_token(),
        }
        response = self.client.open(
            '/locations/cars',
            method='GET',
            headers=headers,
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_engineers_list(self):
        """Test case for cars_list

        Get car info
        """
        query_string = [('offset', 168)]
        headers = {
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + get_token(),
        }
        response = self.client.open(
            '/engineers',
            method='GET',
            headers=headers,
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_cars_post(self):
        """Test case for cars_post

        Post car info
        """
        body = {
            "id": "123456789",
            "administration": "Klantteam Noord",
            "driver_skill": "Metende",
            "token": "some-token-value"
        }
        headers = {
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + get_token(),
        }
        response = self.client.open(
            '/engineers',
            method='POST',
            headers=headers,
            data=json.dumps(body),
            content_type='application/json')
        self.assertStatus(response, 201,
                          'Response body is : ' + response.data.decode('utf-8'))

    def test_list_tokens(self):
        """Test case for list_tokens

        Get a list of tokens
        """
        query_string = [('assigned', False)]
        headers = {
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + get_token(),
        }
        response = self.client.open(
            '/tokens',
            method='GET',
            headers=headers,
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_list_work_items(self):
        """Test case for list_work_items

        Get a list of work items
        """
        query_string = [('active', False)]
        headers = {
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + get_token(),
        }
        response = self.client.open(
            '/workitems',
            method='GET',
            headers=headers,
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))
