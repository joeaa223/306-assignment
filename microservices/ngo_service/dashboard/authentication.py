"""
Custom JWT Authentication for microservices.

In a microservices architecture, each service has its own isolated database.
The default SimpleJWT authentication tries to look up the user in the LOCAL
database, which fails because users only exist in the User Service's database.

This custom authenticator validates the JWT token's signature and expiry,
then creates a lightweight user object from the token claims WITHOUT
querying the local database.
"""
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth.models import User


class MicroserviceJWTAuthentication(JWTAuthentication):
    """
    Custom JWT auth that doesn't require the user to exist in the local DB.
    It trusts the token claims (user_id) after verifying the signature.
    """

    def get_user(self, validated_token):
        """
        Override: Instead of querying the local DB, create a simple
        user object from the JWT claims.
        """
        user_id = validated_token.get('user_id')
        if user_id is None:
            from rest_framework_simplejwt.exceptions import InvalidToken
            raise InvalidToken('Token contained no recognizable user identification')

        # Try to find user locally first (for admin access)
        try:
            user = User.objects.get(id=user_id)
            return user
        except User.DoesNotExist:
            pass

        # Create a minimal user object without saving to DB
        user = User(id=user_id, username=f'user_{user_id}')
        user.is_active = True
        user.pk = user_id
        return user
