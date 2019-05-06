import config
from jwkaas import JWKaas

my_jwkaas = None

if hasattr(config, 'OAUTH_JWKS_URL'):
    my_jwkaas = JWKaas(config.OAUTH_EXPECTED_AUDIENCE,
                       config.OAUTH_EXPECTED_ISSUER,
                       jwks_url=config.OAUTH_JWKS_URL)


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
    return refine_token_info(my_jwkaas.get_connexion_token_info(token))
