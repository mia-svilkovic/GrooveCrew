from django.contrib.auth import get_user_model, authenticate
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import render
import json
from .models import VinylRecord, Photograph, GoldmineCondition, Wishlist
from .auth_util import validate_access_token
from .serializers import UserSerializer, RecordSerializer, GoldmineConditionSerializer, WishlistSerializer
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
    
@api_view(['POST'])
def add_to_wishlist(request, release_mark, user_id):
    try:
        wishlist_data = {
            'user_id': user_id,
            'release_mark': release_mark
        }
        
        serializer = WishlistSerializer(data=wishlist_data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Successfully added to wishlist',
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def remove_from_wishlist(request, release_mark, user_id):
    try:
        wishlist_item = Wishlist.objects.filter(
            user_id=user_id,
            release_mark=release_mark
        ).first()
        
        if wishlist_item:
            wishlist_item.delete()
            return Response({
                'message': 'Successfully removed from wishlist'
            }, status=status.HTTP_200_OK)
        
        return Response({
            'error': 'Item not found in wishlist'
        }, status=status.HTTP_404_NOT_FOUND)
    
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['GET'])
def get_user_wishlist(request, user_id):
    print("heree")
    try:
        wishlist_items = Wishlist.objects.filter(user_id=user_id)
        
        release_marks = [item.release_mark for item in wishlist_items]
        
        return Response({
            'release_marks': release_marks
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)