from django.contrib.auth import get_user_model, authenticate
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import render
import json
from .models import VinylRecord, Photograph, GoldmineCondition
from django.core.exceptions import ObjectDoesNotExist


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

        # Kreiraj korisnika
        user = User.objects.create_user(email=email, password=password, first_name=first_name, last_name=last_name, username=username)
        
        # JWT token
        refresh = RefreshToken.for_user(user)
        return JsonResponse({
            'message': 'User registered successfully',
            'refresh': str(refresh),
            'access': str(refresh.access_token)
        }, status=201)
        
    return JsonResponse({'error': 'Invalid request method'}, status=400)


@csrf_exempt
def userLogin(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email')
        password = data.get('password')

        user = authenticate(request, email=email, password=password)
        if user is not None:

            # JWT token
            refresh = RefreshToken.for_user(user)
            return JsonResponse({
                'message': 'Login successful',
                'refresh': str(refresh),
                'access': str(refresh.access_token)
            }, status=200)
        else:
            return JsonResponse({'error': 'Invalid credentials'}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=400)


def frontend_view(request):
    return render(request, 'index.html')


@csrf_exempt
def add_vinyl_record(request):

    if request.method == 'POST':

        try:
            # Try to authenticate the user using the JWT token in the header
            user, auth = JWTAuthentication().authenticate(request)
        except AuthenticationFailed:
            # If authentication fails, return a 401 Unauthorized response
            return JsonResponse({"error": "Authentication failed. Please log in."}, status=401)

        # Extract form data
        data = request.POST
        user_id = request.user.id  # Assuming the user is logged in

        # Get form data
        photo = data.get("photo")  # assuming this is the binary content
        artist = data.get("artist")
        album_name = data.get("album_name")
        release_year = data.get("release_year")
        release_code = data.get("release_code")
        genre = data.get("genre")
        location = data.get("location")
        goldmine_standard = data.get("goldmine_standard")  # trebala bi bit kratica
        additional_description = data.get("additional_description")


        
        # Assuming goldmine_standard is an abbreviation or some unique field
        record_condition = GoldmineCondition.objects.get(abbreviation=goldmine_standard)
        
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
            cover_condition=record_condition,  # If it's the same as the record condition, otherwise pass a separate condition
            user=user
        )

        # Create Photograph if there is any photo data (binary)
        if photo:
            photograph = Photograph.objects.create(
                binary_content=photo,
                vinyl_record=vinyl_record
            )  

        # Return success response (you can also return the vinyl record details if needed)
        return JsonResponse({"success": True})
    return JsonResponse({"error": "Invalid method"}, status=400)

def get_records(request):
    items = list(VinylRecord.objects.values())
    return JsonResponse(items, safe=False)