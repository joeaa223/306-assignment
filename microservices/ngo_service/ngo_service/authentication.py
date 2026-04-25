"""
Custom JWT Authentication for microservices that don't own user data.

In a microservices architecture, the User database only lives in the User Service.
Other services (Registration, NGO) need to validate JWT tokens WITHOUT looking up
the user in their local database. This class does exactly that:
  1. Validates the JWT signature (using the shared SECRET_KEY)
  2. Extracts the user_id from the token payload
  3. Returns a lightweight user object instead of querying the local DB
"""
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken


class MicroserviceUser:
    """
    A lightweight user object that doesn't require a database lookup.
    It only carries the user_id extracted from the JWT token.
    """
    def __init__(self, user_id):
        self.id = user_id
        self.pk = user_id
        self.is_authenticated = True


class MicroserviceJWTAuthentication(JWTAuthentication):
    """
    Custom JWT auth that validates the token signature but skips
    the local database user lookup. Perfect for downstream services
    in a microservices architecture.
    """
    def get_user(self, validated_token):
        try:
            user_id = validated_token.get('user_id')
            if user_id is None:
                raise InvalidToken('Token contained no user_id')
            return MicroserviceUser(user_id)
        except Exception:
            raise InvalidToken('Token is invalid or expired')
