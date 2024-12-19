from django.contrib.auth import get_user_model, authenticate
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import render
import json
from .models import VinylRecord, Photograph, GoldmineCondition
from .auth_util import validate_access_token
from .serializers import UserSerializer, RecordSerializer, GoldmineConditionSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view



User = get_user_model()

@csrf_exempt
def userRegister(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email')
        password = data.get('password')
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        username = data.get('username')

        if User.objects.filter(email=email).exists():
            return JsonResponse({'error': 'Email already registered'}, status=400)

        # Create user
        user = User.objects.create_user(email=email, password=password, first_name=first_name, last_name=last_name, username=username)
        
        # Generate JWT token
        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token

        # Set tokens as HttpOnly cookies
        response = JsonResponse({
            'message': 'register successful',
            'user': UserSerializer(user).data
        })
        
        response.set_cookie(
            'access', str(access_token),
            httponly=True,  # Prevent JavaScript access
            secure=False    
        )
        response.set_cookie(
            'refresh', str(refresh),
            httponly=True,
            secure=False
        )
        return response
        
    return JsonResponse({'error': 'Invalid request method'}, status=400)


@csrf_exempt
def userLogin(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email')
        password = data.get('password')
        
        user = authenticate(request, email=email, password=password)
        if user is not None:
            # Generate JWT token
            refresh = RefreshToken.for_user(user)
            access_token = refresh.access_token

            # Set tokens as HttpOnly cookies
            response = JsonResponse({'message': 'Login successful', 'user': UserSerializer(user).data})
            response.set_cookie(
                'access', str(access_token),
                httponly=True,  # Prevent JavaScript access
                secure=False,
                samesite='Lax'    
            )
            response.set_cookie(
                'refresh', str(refresh),
                httponly=True,
                secure=False,
                samesite='Lax'
            )
            return response
        else:
            return JsonResponse({'error': 'Invalid credentials'}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=400)


def frontend_view(request):
    return render(request, 'index.html')

#treba manualno dodati goldmine u bazu

@csrf_exempt
def add_vinyl_record(request, user_id):

    if request.method == 'POST':
       
        try:
            user, response = validate_access_token(request)
        except AuthenticationFailed as e:
            return JsonResponse({'error: ': str(e)}, status=401)
        
        # serializer = RecordSerializer(data=request.POST, context={'request': request})
        # if serializer.is_valid():
        #     serializer.save()
        #     return JsonResponse(serializer.data, status=201)
        # print(serializer.errors) 
        # return JsonResponse(serializer.errors, status=400)


        # Extract form data
        data = request.POST
        #user_id = user.id  # Assuming the user is logged in

        # Get form data
        photo = request.FILES.get('photo')  # assuming this is the binary content
        artist = data.get("artist")
        album_name = data.get("album_name")
        release_year = data.get("release_year")
        release_code = data.get("release_code")
        genre = data.get("genre")
        location = data.get("location")
        record_condition_gs = data.get("record_condition")  # trebala bi bit kratica
        cover_condition_gs = data.get("cover_condition")
        additional_description = data.get("additional_description")


        
        # Assuming goldmine_standard is an abbreviation or some unique field
        record_condition = GoldmineCondition.objects.get(id=record_condition_gs)
        cover_condition = GoldmineCondition.objects.get(id=cover_condition_gs)
        
        # Assuming `user_id` is passed, you can fetch the CustomUser instance
        user = User.objects.get(id=user_id)


        # Create VinylRecord instance
        vinyl_record = VinylRecord.objects.create(
            release_code=release_code,
            artist=artist,
            album_name=album_name,
            release_year=release_year,
            genre=genre,
            location=location,  # It needs to be in JSON Format
            available_for_exchange=True,  # Or you can handle this logic if it's a form field
            additional_description=additional_description,
            record_condition=record_condition,
            cover_condition=cover_condition,  # If it's the same as the record condition, otherwise pass a separate condition
            user=user
        )

        # Create Photograph if there is any photo data (binary)
        if photo:
            photograph = Photograph.objects.create(
                binary_content=photo.read(),
                vinyl_record=vinyl_record
            )  

        return JsonResponse({"success": True})
    return JsonResponse({"error": "Invalid method"}, status=400)

def get_records(request):
    items = list(VinylRecord.objects.values())
    return JsonResponse(items, safe=False)

@api_view(['GET'])
def get_user_vinyls(request, user_id):
    try:
        vinyl_records = VinylRecord.objects.filter(user_id=user_id)
        
        serializer = RecordSerializer(vinyl_records, many=True)
        return Response(serializer.data)
    
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )

def test_token(request):
    try:
        user, response = validate_access_token(request)
        return response
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=401)
