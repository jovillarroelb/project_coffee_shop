import json
from flask import request
from functools import wraps
from jose import jwt
from urllib.request import urlopen

# # A.- Starter Code
# AUTH0_DOMAIN = "udacity-fsnd.auth0.com"
# ALGORITHMS = ["RS256"]
# API_AUDIENCE = "dev"

# B.- Personal Project Specific:
AUTH0_DOMAIN = "jovillarroelb.us.auth0.com"
ALGORITHMS = ["RS256"]
API_AUDIENCE = "coffeeshop"

## AuthError Exception
"""
AuthError Exception
A standardized way to communicate auth failure modes
"""


class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


## Auth Header

"""
@TODO implement get_token_auth_header() method
    it should attempt to get the header from the request
        it should raise an AuthError if no header is present
    it should attempt to split bearer and the token
        it should raise an AuthError if the header is malformed
    return the token part of the header
"""


def get_token_auth_header():
    """
    Description: It obtains the header for the token.
    """

    auth_hdr = request.headers.get("Authorization", None)

    # If there is no header returned
    if not auth_hdr:
        raise AuthError(
            {
                "code": "authorization_header_missing",
                "description": "Authorization header is expected.",
            },
            401,
        )

    # Split the header into its sub-parts:
    # Using ".split()" separates the "Bearer" string from the actual token.
    parts = auth_hdr.split()

    # The header has the correct number of sub-elements (ie. for BEARER tokens there are 2 parts)
    if len(parts) == 2:
        if parts[0].lower() != "bearer":
            raise AuthError(
                {
                    "code": "invalid_header",
                    "description": 'Authorization type needs to be "BEARER"',
                },
                401,
            )

        token = parts[1]

        return token

    # The header doesn't have the correct number of sub-elements (just 1 sub-part or more than 2).
    else:
        if len(parts) == 1:
            raise AuthError(
                {
                    "code": "invalid_header",
                    "description": "There is no token in the header",
                },
                401,
            )
        if len(parts) > 2:
            raise AuthError(
                {
                    "code": "invalid_header",
                    "description": "Authorization must satisfy BEARER token format",
                },
                401,
            )


"""
@TODO implement check_permissions(permission, payload) method
    @INPUTS
        permission: string permission (i.e. 'post:drink')
        payload: decoded jwt payload

    it should raise an AuthError if permissions are not included in the payload
        !!NOTE check your RBAC settings in Auth0
    it should raise an AuthError if the requested permission string is not in 
    the payload permissions array 
        return true otherwise
"""


def check_permissions(permission, payload):
    if "permissions" not in payload:
        raise AuthError(
            {
                "code": "invalid",
                "description": "No permissions in JWT",
            },
            400,
        )

    if permission not in payload["permissions"]:
        raise AuthError(
            {
                "code": "unauthorized",
                "description": "Permission not found",
            },
            401,
        )
    return True


"""
@TODO implement verify_decode_jwt(token) method
    @INPUTS
        token: a json web token (string)

    it should be an Auth0 token with key id (kid)
    it should verify the token using Auth0 /.well-known/jwks.json
    it should decode the payload from the token
    it should validate the claims
    return the decoded payload

    !!NOTE urlopen has a common certificate error described here: https://stackoverflow.com/questions/50236117/scraping-ssl-certificate-verify-failed-error-for-http-en-wikipedia-org
"""


def verify_decode_jwt(token):
    # Get public key from Auth0
    jsonurl = urlopen(f"https://{AUTH0_DOMAIN}/.well-known/jwks.json")
    jwks = json.loads(jsonurl.read())

    # Get the data in the header
    unverified_header = jwt.get_unverified_header(token)

    # CHeck if the Auth0 token have a key id
    if "kid" not in unverified_header:
        raise AuthError(
            {
                "code": "invalid_header",
                "description": "Authorization malformed",
            },
            401,
        )

    rsa_key = {}

    for key in jwks["keys"]:
        if key["kid"] == unverified_header["kid"]:
            rsa_key = {
                "kty": key["kty"],
                "kid": key["kid"],
                "use": key["use"],
                "n": key["n"],
                "e": key["e"],
            }
    if rsa_key:
        try:
            # Validate the token using the rsa_key
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=ALGORITHMS,
                audience=API_AUDIENCE,
                # issuer="https://" + AUTH0_DOMAIN + "/",
                issuer=f"https://{AUTH0_DOMAIN}/",
            )
            return payload

        except jwt.ExpiredSignatureError:

            raise AuthError(
                {
                    "code": "token_expired",
                    "description": "Token expired.",
                },
                401,
            )

        except jwt.JWTClaimsError:

            raise AuthError(
                {
                    "code": "invalid_claims",
                    "description": "Incorrect claims. Please, check the audience and issuer.",
                },
                401,
            )

        except Exception:

            raise AuthError(
                {
                    "code": "invalid_header",
                    "description": "Unable to parse authentication token.",
                },
                400,
            )

    raise AuthError(
        {
            "code": "invalid_header",
            "description": "Unable to find the appropriate key.",
        },
        400,
    )


"""
@TODO implement @requires_auth(permission) decorator method
    @INPUTS
        permission: string permission (i.e. 'post:drink')

    it should use the get_token_auth_header method to get the token
    it should use the verify_decode_jwt method to decode the jwt
    it should use the check_permissions method validate claims and check the requested permission
    return the decorator which passes the decoded payload to the decorated method
"""


def requires_auth(permission=""):
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            token = get_token_auth_header()
            payload = verify_decode_jwt(token)
            check_permissions(permission, payload)
            return f(payload, *args, **kwargs)

        return wrapper

    return requires_auth_decorator
