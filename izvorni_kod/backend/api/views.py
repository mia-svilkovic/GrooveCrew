from django.conf import settings
from django.contrib.auth import login, logout
from django.http import Http404, HttpResponseRedirect, JsonResponse
from django.middleware.csrf import get_token

from rest_framework import generics, permissions, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView

from .models import (
    Genre, GoldmineConditionCover, GoldmineConditionRecord,
    Record, User, Wishlist
)

from .serializers import (
    GenreSerializer, GoldmineConditionCoverSerializer,
    GoldmineConditionRecordSerializer, LoginSerializer,
    RecordSerializer, RegisterSerializer,
    UserSerializer, WishlistSerializer
)


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token)
    }


class RegisterView(generics.CreateAPIView):
    """
    User Registration View
    """
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer
    queryset = User.objects.all()

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        headers = self.get_success_headers(serializer.data)

        tokens = get_tokens_for_user(user)

        response_data = {
            'message': 'User registered successfully!',
            'user': serializer.data,
            'tokens': tokens
        }

        return Response(
            response_data,
            status=status.HTTP_201_CREATED,
            headers=headers)


class LoginView(APIView):
    """
    User Login View
    Handles user authentication and returns JWT tokens.
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']
        tokens = get_tokens_for_user(user)

        response_data = {
            'message': 'Login successful!',
            'user': UserSerializer(user).data,
            'tokens': tokens
        }

        # Handle Superuser Login with Session
        if user.is_staff:
            # Log the user into the session
            login(request, user) # Log the user into the current session

            # Ensure session is created and saved
            if not request.session.session_key:
                request.session.create()
            request.session.save()

            # Get CSRF token
            csrf_token = get_token(request)

            # Set sessionid cookie
            response = Response(response_data, status=status.HTTP_200_OK)
            response.set_cookie(
                key='sessionid',
                value=request.session.session_key,
                domain=None,    # Important for local development
                path='/',
                secure=settings.SESSION_COOKIE_SECURE,
                httponly=True,
                samesite='None',
                max_age=settings.SESSION_COOKIE_AGE,
            )

            return response

        return Response(response_data, status=status.HTTP_200_OK)

class LogoutView(APIView):
    """
    Handles JWT Token Blacklisting for logout.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if refresh_token is None:
                return Response(
                    {'error': 'Refresh token is required for logout.'},
                    status=status.HTTP_400_BAD_REQUEST)

            token = RefreshToken(refresh_token)
            token.blacklist()   # Blacklist the refresh token

            return Response({'message': 'Successfully logged out.'}, status=status.HTTP_200_OK)
        
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


def custom_admin_logout(request):
    """
    Custom Logout View for Superusers.
    Ensures session is destroyed and redirects appropriately.
    """
    logout(request)
    return HttpResponseRedirect('/admin/login/')  # Redirect to admin login page


def oauth_login_success(request):
    if request.user.socialaccount_set.exists():
        return JsonResponse({"message": "OAuth login successful"}, status=200)
    return JsonResponse({"error": "This endpoint is for OAuth logins only."}, status=400)


def oauth_logout_success(request):
    if request.user.socialaccount_set.exists():
        return JsonResponse({"message": "OAuth logout successful"}, status=200)
    return JsonResponse({"error": "This endpoint is for OAuth logouts only."}, status=400)


class RecordCreateView(generics.CreateAPIView):
    """
    API endpoint for adding a new record along with associated photos.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = RecordSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class RecordListView(generics.ListAPIView):
    """
    API endpoint for listing all records or filtering
    (filtering hasn't been implemented)
    """
    permission_classes = [permissions.AllowAny]
    serializer_class = RecordSerializer
    queryset = Record.objects.all()
    
    
class RecordDetailView(generics.RetrieveAPIView):
    """
    API endpoint for retrieving a single record by ID.
    """
    permission_classes = [permissions.AllowAny]
    serializer_class = RecordSerializer
    queryset = Record.objects.all()
    lookup_field = 'id'


class RecordUpdateView(generics.UpdateAPIView):
    """
    API endpoint for updating record details.
    Only the owner of the record can perform updates.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = RecordSerializer
    queryset = Record.objects.all()
    lookup_field = 'id'

    def perform_update(self, serializer):
        """
        Ensure that only the record owner can update the record.
        """
        record = self.get_object()
        if record.user != self.request.user:
            raise ValidationError("You do not have permission to update this record.")
        serializer.save()


class RecordDeleteView(generics.DestroyAPIView):
    """
    API endpoint for deleting a record.
    Only the owner of the record can delete it.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = RecordSerializer
    queryset = Record.objects.all()
    lookup_field = 'id'

    def perform_destroy(self, instance):
        """
        Ensure that only the record owner can delete the record.
        """
        if instance.user != self.request.user:
            raise ValidationError("You do not have permission to delete this record.")
        instance.delete()


class UserRecordListView(generics.ListAPIView):
    """
    API endpoint for listing all records of a specific user.
    """
    permission_classes = [permissions.AllowAny]
    serializer_class = RecordSerializer

    def get_queryset(self):
        user_id = self.kwargs.get('user_id')
        if not user_id or not str(user_id).isdigit():
            raise Http404('Invalid user_id. It must be an integer.')
        return Record.objects.filter(user_id=int(user_id))
    

class GenreListView(generics.ListAPIView):
    """
    API endpoint for listing all available genres.
    """
    permission_classes = [permissions.AllowAny]
    serializer_class = GenreSerializer
    queryset = Genre.objects.all()


class GoldmineConditionRecordListView(generics.ListAPIView):
    """
    API endpoint for listing all record Goldmine Condition.
    """
    permission_classes = [permissions.AllowAny]
    serializer_class = GoldmineConditionRecordSerializer
    queryset = GoldmineConditionRecord.objects.all()


class GoldmineConditionCoverListView(generics.ListAPIView):
    """
    API endpoint for listing all cover Goldmine Condition.
    """
    permission_classes = [permissions.AllowAny]
    serializer_class = GoldmineConditionCoverSerializer
    queryset = GoldmineConditionCover.objects.all()


class WishlistListView(generics.ListAPIView):
    """
    API endpoint for listing the authenticated user's wishlist items.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = WishlistSerializer

    def get_queryset(self):
        """
        Return wishlist items belonging to the authenticated user.
        """
        return Wishlist.objects.filter(user=self.request.user)


class WishlistCreateView(generics.CreateAPIView):
    """
    API endpoint for adding an item to the user's wishlist.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = WishlistSerializer

    def perform_create(self, serializer):
        """
        Ensure that the user is set to the currently authenticated user.
        """
        serializer.save(user=self.request.user)


class WishlistDeleteView(generics.DestroyAPIView):
    """
    API endpoint for removing an item from the user's wishlist.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = WishlistSerializer
    queryset = Wishlist.objects.all()
    lookup_field = 'id'

    def perform_destroy(self, instance):
        """
        Ensure the user can only delete their own wishlist items.
        """
        if instance.user != self.request.user:
            raise ValidationError("You do not have permission to delete this wishlist entry.")
        instance.delete()
