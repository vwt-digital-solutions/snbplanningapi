import config
import logging
from jwkaas import JWKaas

from flask import g

my_jwkaas = None
my_e2e_jwkaas = None
my_b2b_jwkaas = None

if hasattr(config, 'OAUTH_JWKS_URL'):
    my_jwkaas = JWKaas(config.OAUTH_EXPECTED_AUDIENCE,
                       config.OAUTH_EXPECTED_ISSUER,
                       jwks_url=config.OAUTH_JWKS_URL)

if hasattr(config, 'OAUTH_B2B_JWKS_URL'):
    my_b2b_jwkaas = JWKaas(config.OAUTH_B2B_EXPECTED_AUDIENCE,
                           config.OAUTH_B2B_EXPECTED_ISSUER,
                           jwks_url=config.OAUTH_B2B_JWKS_URL)

if hasattr(config, 'OAUTH_E2E_JWKS_URL'):
    my_e2e_jwkaas = JWKaas(config.OAUTH_E2E_EXPECTED_AUDIENCE,
                           config.OAUTH_E2E_EXPECTED_ISSUER,
                           jwks_url=config.OAUTH_E2E_JWKS_URL)


def refine_token_info(token_info):
    if token_info and 'scopes' in token_info:
        if 'snbplanningapi.editor' in token_info['scopes']:
            token_info['scopes'].append('snbplanningapi.planner')
    return token_info


def info_from_OAuth2AzureAD(token):
    """
    Validate and decode token.
    Returned value will be passed in 'token_info' parameter of your operation function, if there is one.
    'sub' or 'uid' will be set in 'user' parameter of your operation function, if there is one.
    'scope' or 'scopes' will be passed to scope validation function.

    :param token Token provided by Authorization header
    :type token: str
    :return: Decoded token information or None if token is invalid
    :rtype: dict | None
    """
    result = my_jwkaas.get_connexion_token_info(token)

    # Check if b2b token is configured
    if result is None and my_b2b_jwkaas is not None:
        token_info = my_b2b_jwkaas.get_connexion_token_info(token)
        if token_info is not None and 'appid' in token_info and \
                token_info['appid'] == config.OAUTH_B2B_APPID:
            logging.warning('Approved B2B access token for appid [%s]', token_info['appid'])
            result = {'scopes': ['snbplanningapi.read', 'snbplanningapi.planner'], 'sub': 'b2b', 'upn': 'b2b-technical-user'}

    # Check if e2e test token is configured
    if result is None and my_e2e_jwkaas is not None:
        token_info = my_e2e_jwkaas.get_connexion_token_info(token)
        if token_info is not None and 'appid' in token_info and \
                token_info['appid'] == config.OAUTH_E2E_APPID:
            logging.warning('Approved e2e access token for appid [%s]', token_info['appid'])
            result = {'scopes': ['snbplanningapi.read', 'snbplanningapi.editor'], 'sub': 'e2e', 'upn': 'e2e-technical-user'}

    if result is not None:
        g.user = result.get('upn', '')

    return refine_token_info(result)
