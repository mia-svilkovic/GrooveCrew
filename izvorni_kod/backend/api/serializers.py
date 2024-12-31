from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.db import transaction

from rest_framework import serializers

from api.models import (
    Genre, GoldmineConditionCover, GoldmineConditionRecord,
    Photo, Record, User, Wishlist
)


class RegisterSerializer(serializers.ModelSerializer):
    password1 = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        validators=[validate_password],
    )
    password2 = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
    )

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name', 'last_name', 'password1', 'password2', 'is_staff')
        read_only_fields = ('id', 'is_staff')
 
    def validate(self, data):
        """
        Check that the two password fields match.
        """
        if data['password1'] != data['password2']:
            raise serializers.ValidationError({'password': 'Passwords do not match.'})
        return data

    def create(self, validated_data):
        """
        Create a new user with the validated data.
        """
        password = validated_data.pop('password1')
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data, password = password)
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )

    def validate(self, data):
        """
        Check email and password against the authentication backend.
        """
        user = authenticate(email=data['email'], password=data['password'])
        if not user:
            raise serializers.ValidationError('Invalid credentials. Please try again.')
        if not user.is_active:
            raise serializers.ValidationError('This user account is inactive.')
        data['user'] = user
        return data


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name', 'last_name')
        read_only_fields = ('id', 'email', 'username', 'first_name', 'last_name')


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ('id', 'name')
        read_only_fields = ('id',)


class GoldmineConditionRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoldmineConditionRecord
        fields = ('id', 'name', 'abbreviation', 'description')
        read_only_fields = ('id',)


class GoldmineConditionCoverSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoldmineConditionCover
        fields = ('id', 'name', 'abbreviation', 'description')
        read_only_fields = ('id',)


class PhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = ('id', 'image', 'record')
        read_only_fields = ('id',)


class RecordSerializer(serializers.ModelSerializer):
    genre_id = serializers.PrimaryKeyRelatedField(
        queryset=Genre.objects.all(),
        source='genre',
        write_only=True
    )
    record_condition_id = serializers.PrimaryKeyRelatedField(
        queryset=GoldmineConditionRecord.objects.all(),
        source='record_condition',
        write_only=True
    )
    cover_condition_id = serializers.PrimaryKeyRelatedField(
        queryset=GoldmineConditionCover.objects.all(),
        source='cover_condition',
        write_only=True
    )

    genre = GenreSerializer(read_only=True)
    record_condition = GoldmineConditionRecordSerializer(read_only=True)
    cover_condition = GoldmineConditionCoverSerializer(read_only=True)
    user = UserSerializer(read_only=True)

    # Support multiple photos
    add_photos = serializers.ListField(
        child=serializers.ImageField(),
        required=False,
        write_only=True
    )
    photos = PhotoSerializer(many=True, read_only=True)

    class Meta:
        model = Record
        fields = (
            'id', 
            'catalog_number', 
            'artist', 
            'album_name', 
            'release_year', 
            'genre',
            'genre_id', # For creating via ID 
            'location', 
            'available_for_exchange',
            'additional_description', 
            'record_condition',
            'record_condition_id',  # For creating via ID
            'cover_condition',
            'cover_condition_id',   # For creating via ID
            'user',
            'photos',
            'add_photos'   # Photos uploaded when adding new record
        )
        read_only_fields = ('id', 'user', 'genre', 'record_condition', 'cover_condition', 'photos')

    def create(self, validated_data):
        """
        Create a record and handle associated photos.
        """
        # Extract photos from validated data
        photos = validated_data.pop('add_photos', [])

        try:
            with transaction.atomic():
                # Create the record
                record = Record.objects.create(**validated_data)

                # Validate and create associated photos
                Photo.objects.bulk_create([
                    Photo(record=record, image=photo)
                    for photo in photos
                ])
        except Exception as e:
            raise serializers.ValidationError({
                'error': f'Failed to create record and associated photos: {str(e)}'
            })
       
        return record
    

class WishlistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wishlist
        fields = ('id', 'record_catalog_number')
        read_only_fields = ('id',)
        constraints = [
            serializers.UniqueTogetherValidator(
                queryset=Wishlist.objects.all(),
                fields=('user', 'record_catalog_number'),
                message='This record is already in your wishlist.'
            )
        ]
