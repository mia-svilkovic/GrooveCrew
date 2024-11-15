from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate

from .models import Record, GoldmineCondition
from .serializers import UserSerializer, RecordSerializer, GoldmineConditionSerializer

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
   try:
       serializer = UserSerializer(data=request.data)
       if serializer.is_valid():
           user = serializer.save()
           refresh = RefreshToken.for_user(user)
           return Response({
               'user': UserSerializer(user).data,
               'refresh': str(refresh),
               'access': str(refresh.access_token),
           }, status=status.HTTP_201_CREATED)
       return Response({
           'errors': serializer.errors
       }, status=status.HTTP_400_BAD_REQUEST)
   except Exception as e:
       return Response({
           'error': str(e)
       }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
   try:
       email = request.data.get('email')
       password = request.data.get('password')

       if not email or not password:
           return Response({
               'error': 'Please provide both email and password'
           }, status=status.HTTP_400_BAD_REQUEST)

       user = authenticate(email=email, password=password)

       if not user:
           return Response({
               'error': 'Invalid credentials'
           }, status=status.HTTP_401_UNAUTHORIZED)

       if not user.is_active:
           return Response({
               'error': 'Account is not active'
           }, status=status.HTTP_403_FORBIDDEN)

       refresh = RefreshToken.for_user(user)
       return Response({
           'user': UserSerializer(user).data,
           'refresh': str(refresh),
           'access': str(refresh.access_token),
       })
   except Exception as e:
       return Response({
           'error': str(e)
       }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
   
@api_view(['GET'])
@permission_classes([AllowAny])
def record_list(request):
    records = Record.objects.all()
    serializer = RecordSerializer(records, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def record_create(request):
   serializer = RecordSerializer(data=request.data, context={'request': request})
   if serializer.is_valid():
       serializer.save()
       return Response(serializer.data, status=status.HTTP_201_CREATED)
   return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([AllowAny])
def goldmine_condition_list(request):
    goldmine_conditions = GoldmineCondition.objects.all()
    serializer = GoldmineConditionSerializer(goldmine_conditions, many=True)
    return Response(serializer.data)