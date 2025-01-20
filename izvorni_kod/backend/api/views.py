from django.conf import settings
from django.contrib.auth import login, logout
from django.http import Http404, HttpResponseRedirect
from django.middleware.csrf import get_token
from django.shortcuts import get_object_or_404

from rest_framework import generics, permissions, status
from rest_framework.exceptions import ValidationError, PermissionDenied
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView

from google.oauth2 import id_token
from google.auth.transport import requests

from .models import *
from .serializers import *


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    refresh.payload.update({
        'id': user.id,
        'email': user.email,
        'username': user.username,
        'first_name': user.first_name,
        'last_name': user.last_name,
    })

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
                httponly=settings.SESSION_COOKIE_HTTPONLY,
                samesite=settings.SESSION_COOKIE_SAMESITE,
                max_age=settings.SESSION_COOKIE_AGE,
            )

            # Set CSRF token
            response.set_cookie(
                key='csrftoken',
                value=csrf_token,
                httponly=settings.CSRF_COOKIE_HTTPONLY,
                samesite=settings.CSRF_COOKIE_SAMESITE,
                secure=True,
            )

            return response

        return Response(response_data, status=status.HTTP_200_OK)

class GoogleLoginView(APIView):
    """
    Authenticate users via Google ID Token and return JWT tokens.
    """

    def post(self, request, *args, **kwargs):
        id_token_str = request.data.get('id_token')

        if not id_token_str:
            return Response({'message': 'ID token is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Verificiraj ID Token koristeći Google javni ključ
            id_info = id_token.verify_oauth2_token(
                id_token_str,
                requests.Request(),
                settings.GOOGLE_CLIENT_ID
            )

            email = id_info.get('email')
            first_name = id_info.get('given_name')
            last_name = id_info.get('family_name')

            if not email:
                return Response({'message': 'Email not found in ID token'}, status=status.HTTP_400_BAD_REQUEST)

            # Dohvati ili kreiraj korisnika
            user, created = User.objects.get_or_create(email=email, defaults={
                'username': email.split('@')[0],
                'first_name': first_name,
                'last_name': last_name,
            })

            if created:
                user.set_unusable_password()
                user.save()

            tokens = get_tokens_for_user(user)

            user_data = {
                'id': user.id,
                'email': user.email,
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
            }

            return Response({
                'message': 'Google Login successful!',
                'user': user_data,
                'tokens': tokens
            }, status=status.HTTP_200_OK)

        except ValueError as e:
            return Response({'message': 'Invalid ID token', 'details': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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
                    {'message': 'Refresh token is required for logout.'},
                    status=status.HTTP_400_BAD_REQUEST)

            token = RefreshToken(refresh_token)
            token.blacklist()   # Blacklist the refresh token

            return Response({'message': 'Successfully logged out.'}, status=status.HTTP_200_OK)
        
        except ValidationError as e:
            return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)


def custom_admin_logout(request):
    """
    Custom Logout View for Superusers.
    Ensures session is destroyed and redirects appropriately.
    """
    logout(request)
    return HttpResponseRedirect(f"{settings.SITE_URL}")  # Redirect to admin login page


class RecordCreateView(generics.CreateAPIView):
    """
    API endpoint for adding a new record along with associated photos.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = RecordSerializer

    def get_serializer_context(self):
        """
        Pass the current user to the serializer.
        """
        context = super().get_serializer_context()
        context['user'] = self.request.user
        return context


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

    def get_serializer_context(self):
        """
        Pass the current user to the serializer.
        """
        context = super().get_serializer_context()
        context['user'] = self.request.user
        return context

    def perform_update(self, serializer):
        """
        Ensure that only the record owner can update the record.
        """
        record = self.get_object()
        if record.user != self.request.user:
            raise PermissionDenied({
                "message": "You do not have permission to update this record." 
            })
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
            raise PermissionDenied({
                "message": "You do not have permission to delete this record."
            })
        instance.delete()


class LocationListView(generics.ListCreateAPIView):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    permission_classes = [permissions.IsAuthenticated]


class LocationDetailView(generics.RetrieveAPIView):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    permission_classes = [permissions.IsAuthenticated]


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

    def get_serializer_context(self):
        """
        Pass the current user to the serializer.
        """
        context = super().get_serializer_context()
        context['user'] = self.request.user
        return context


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
            raise PermissionDenied({
                "message": "You do not have permission to delete this wishlist entry." 
            })
        instance.delete()
    

class ExchangeListView(generics.ListAPIView):
    """
    API endpoint for listing all exchanges.
    """
    serializer_class = ExchangeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Return only exchanges where the user is the initiator or receiver.
        """
        user = self.request.user
        return Exchange.objects.filter(
            models.Q(initiator_user=user) | models.Q(receiver_user=user)
        )


class ExchangeRetrieveView(generics.RetrieveAPIView):
    """
    API endpoint for retrieving a single exchange.
    """
    queryset = Exchange.objects.all()
    serializer_class = ExchangeSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'

    def get_object(self):
        """
        Ensure only the initiator or receiver can access the exchange details.
        """
        exchange = super().get_object()
        user = self.request.user

        if user not in [exchange.initiator_user, exchange.receiver_user]:
            raise PermissionDenied({
                "message": "You do not have permission to view this exchange."
            })

        return exchange


class ExchangeCreateView(generics.CreateAPIView):
    """
    API endpoint for creating a new exchange.
    """
    queryset = Exchange.objects.all()
    serializer_class = ExchangeCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['user'] = self.request.user
        return context


class ExchangeUpdateView(generics.UpdateAPIView):
    """
    API endpoint for updating an exchange.
    """
    queryset = Exchange.objects.all()
    serializer_class = ExchangeUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['user'] = self.request.user
        return context
    
    def perform_update(self, serializer):
        exchange = self.get_object()
        user = self.request.user

        if user not in [exchange.initiator_user, exchange.receiver_user]:
            raise PermissionDenied({
                "message": "You are not authorized to modify this exchange." 
            })

        if user != exchange.next_user_to_review:
            raise PermissionDenied({
                "message": "It's not your turn to review and modify this exchange."
            })
            
        serializer.save()
    

class ExchangeDeleteView(generics.DestroyAPIView):
    """
    API endpoint for deleting or canceling an exchange.
    - If the exchange is completed, it cannot be deleted.
    - If the exchange is still ongoing, treat deletion as cancellation.
    """
    queryset = Exchange.objects.all()
    serializer_class = ExchangeSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'

    def perform_destroy(self, instance):
        """
        Ensure only the initiator or receiver can cancel/delete the exchange.
        Completed exchanges cannot be deleted.
        """
        user = self.request.user

        # Check if the user has the right permissions
        if user not in [instance.initiator_user, instance.receiver_user]:
            raise PermissionDenied({
                "message": "You do not have permission to delete this exchange."
            })

        # Check if the exchange has already been completed
        if instance.completed:
            raise ValidationError({
                "message": "You cannot delete a completed exchange."
            })
            
        instance.delete()


class ExchangeSwitchReviewerView(APIView):
    """
    API endpoint for explicitly switching the reviewer of an exchange.
    """
    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def post(self, request, id):
        exchange = get_object_or_404(Exchange, id=id)
        user = request.user

        # Verify user permessions
        if user != exchange.next_user_to_review:
            return Response(
                {"message": "You are not the next user to review this exchange."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # If the user is the initiator
        if user == exchange.initiator_user:
            if exchange.records_requested_by_receiver.exists():
                return Response(
                    {"message": "You cannot switch reviewers until all requested records by the receiver are resolved."},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # If the user is the receiver
        if user == exchange.receiver_user:
            if not exchange.records_requested_by_receiver.exists():
                return Response(
                    {"message": "You cannot switch reviewers because you have not requested any additional records."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
        # All checks passed – switch the reviewer
        exchange.switch_reviewer()

        return Response(
            {"message": "The reviewer has been successfully switched to the next user."},
            status=status.HTTP_200_OK
        )


class ExchangeFinalizeView(APIView):
    """
    API endpoint for finalizing an exchange.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, id):
        exchange = get_object_or_404(Exchange, id=id)
        user = self.request.user

        if user not in [exchange.initiator_user, exchange.receiver_user]:
            return Response(
                {"message": "You are not authorized to modify this exchange."},
                status=status.HTTP_403_FORBIDDEN
            )

        # Check if the current user is the receiver_user
        if request.user != exchange.receiver_user:
            return Response(
                {"message": "Only the receiver can finalize the exchange."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            exchange.finalize()
        except Exception as e:
            return Response(
                {"message": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            {"message": "Exchange finalized successfully."},
            status=status.HTTP_200_OK
        )
