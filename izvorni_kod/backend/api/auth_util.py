from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import AuthenticationFailed
from django.http import JsonResponse

def validate_access_token(request):
    """
    Validates the access token from cookies.
    Returns the user if the token is valid, otherwise attempts to refresh using the refresh token.
    """
    # Get tokens from cookies
    access_token = request.COOKIES.get('access')
    refresh_token = request.COOKIES.get('refresh')
    
    if not access_token:
        raise AuthenticationFailed("please log in first.")

    # Set up the JWT authentication
    jwt_authenticator = JWTAuthentication()
    try:
        # Try to validate the access token
        validated_token = jwt_authenticator.get_validated_token(access_token)
        user = jwt_authenticator.get_user(validated_token)
        return user  # Return the user if token is valid

    except AuthenticationFailed:
        # If access token is expired, attempt to use the refresh token
        if refresh_token:
            try:
                # Generate a new access token from the refresh token
                new_access_token = RefreshToken(refresh_token).access_token

                # Set the new access token as a cookie in the response
                response = JsonResponse("Session refreshed.")
                response.set_cookie(
                    'access', str(new_access_token),
                    httponly=True, secure=False  
                )

                # Revalidate using the new access token
                validated_token = jwt_authenticator.get_validated_token(new_access_token)
                user = jwt_authenticator.get_user(validated_token)
                return user, response  # Return both user and response to set the new cookie

            except Exception:
                # If refresh token is invalid or expired
                raise AuthenticationFailed("Session expired. Please log in again.")

        else:
            # No refresh token, cannot reauthenticate
            raise AuthenticationFailed("No valid access or refresh token provided. Please log in again.")
