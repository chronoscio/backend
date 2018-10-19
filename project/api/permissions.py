import jwt
import json
import re

from django.http import JsonResponse
from django.conf import settings
from rest_framework import permissions
from functools import wraps
from six.moves.urllib import request as req
from cryptography.x509 import load_pem_x509_certificate
from cryptography.hazmat.backends import default_backend


class IsStaffOrSpecificUser(permissions.BasePermission):
    """
    Permission to detect whether to user in question is staff or the target user
    Example:
        John (regular user) should be able to access John's account
        Alice (staff) should be able to access John's account
        Jane (regular user) should not be able to access John's account
    """

    def has_permission(self, request, view):
        # allow user to list all users if logged in user is staff
        return view.action == "retrieve" or request.user.is_staff

    def has_object_permission(self, request, view, obj):
        # allow all users to view specific user information
        return True


def get_token_auth_header(request):
    """
    Obtains the Access Token from the Authorization Header
    """
    auth = request.META.get("HTTP_AUTHORIZATION", None)
    parts = auth.split()
    token = parts[1]

    return token


def requires_scope(required_scope):
    """
    Determines if the required scope is present in the access token
    Args:
        required_scope (str): The scope required to access the resource
    """

    def require_scope(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            token = get_token_auth_header(args[0])
            jsonurl = req.urlopen(
                "https://" + settings.AUTH0_DOMAIN + "/.well-known/jwks.json"
            )
            jwks = json.loads(jsonurl.read())
            body = re.sub("(.{64})", "\\1\n", jwks["keys"][0]["x5c"][0], 0, re.DOTALL)
            cert = (
                "-----BEGIN CERTIFICATE-----\n" + body + "\n-----END CERTIFICATE-----"
            )
            certificate = load_pem_x509_certificate(
                cert.encode("utf-8"), default_backend()
            )
            public_key = certificate.public_key()
            decoded = jwt.decode(
                token,
                public_key,
                audience=settings.API_IDENTIFIER,
                algorithms=["RS256"],
            )

            if decoded.get("scope"):
                token_scopes = decoded["scope"].split()
                for token_scope in token_scopes:
                    if token_scope == required_scope:
                        return f(*args, **kwargs)
            response = JsonResponse(
                {"message": "You don't have access to this resource"}
            )
            response.status_code = 403
            return response

        return decorated

    return require_scope
