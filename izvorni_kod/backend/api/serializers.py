import time
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.db import transaction
from rest_framework import serializers
from .models import *
# TODO: UNCOMMENT THIS WHEN FRONTEND IS READY FOR OSM
# from geopy.geocoders import Nominatim
# from geopy.exc import GeocoderTimedOut, GeocoderServiceError


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
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'password1',
            'password2',
            'is_staff'
        )
        read_only_fields = ('id', 'is_staff')
 
    def validate(self, data):
        """
        Check that the two password fields match.
        """
        if data['password1'] != data['password2']:
            raise serializers.ValidationError({'error': 'Passwords do not match.'})
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
            raise serializers.ValidationError({
                "message": 'Invalid credentials. Please try again.'
            })
        if not user.is_active:
            raise serializers.ValidationError({
                "message": 'This user account is inactive.'
            })
        data['user'] = user
        return data


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_staff'
        )
        read_only_fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_staff'
        )


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


# TODO: DELETE THIS WHEN FRONTEND IS READY FOR OSM
class RecordSerializer(serializers.ModelSerializer):
    genre = GenreSerializer(read_only=True)
    genre_id = serializers.PrimaryKeyRelatedField(
        queryset=Genre.objects.all(),
        source='genre',
        write_only=True
    )

    record_condition = GoldmineConditionRecordSerializer(read_only=True)
    record_condition_id = serializers.PrimaryKeyRelatedField(
        queryset=GoldmineConditionRecord.objects.all(),
        source='record_condition',
        write_only=True
    )

    cover_condition = GoldmineConditionCoverSerializer(read_only=True)
    cover_condition_id = serializers.PrimaryKeyRelatedField(
        queryset=GoldmineConditionCover.objects.all(),
        source='cover_condition',
        write_only=True
    )

    user = UserSerializer(read_only=True)

    photos = PhotoSerializer(many=True, read_only=True)
    add_photos = serializers.ListField(
        child=serializers.ImageField(),
        required=False,
        write_only=True
    )

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
            'additional_description', 
            'record_condition',
            'record_condition_id',  # For creating via ID
            'cover_condition',
            'cover_condition_id',   # For creating via ID
            'user',
            'photos',
            'add_photos',   # Photos uploaded when adding new record
            'available_for_exchange',
        )
        read_only_fields = (
            'id',
            'user',
            'genre',
            'record_condition',
            'cover_condition',
            'photos',
            'available_for_exchange',
        )

    def validate(self, data):
        user = self.context.get('user')
        if not user:
            raise serializers.ValidationError({
                'error': "User must be provided when initializing the serializer."
            })
        return data

    def create(self, validated_data):
        """
        Create a record and handle associated photos.
        """

        # Ensure the user is set before creating the object.
        validated_data['user'] = self.context.get('user')

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
    
    def update(self, instance, validated_data):
        """
        Update a record, including location and photos.
        """
        photos = validated_data.pop('add_photos', [])

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if photos:
            Photo.objects.filter(record=instance).delete()
            Photo.objects.bulk_create([
                Photo(record=instance, image=photo)
                for photo in photos
            ])

        instance.save()

        return instance
    

# TODO: UNCOMMENTED THIS WHEN FRONTEND IS READY FOR OSM
# class LocationSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Location
#         fields = ('id', 'address', 'city', 'country', 'coordinates')
#         read_only_fields = ('id', 'address', 'city', 'country')

#     def create(self, validated_data):
#         """
#         Create a location with reverse geocoding.
#         """
#         coordinates = validated_data.get('coordinates')
#         if not coordinates:
#             raise serializers.ValidationError({"message": "Coordinates are required to create a location."})

#         try:
#             # Rate limiting (1 request per second)
#             time.sleep(1)   # Pause for 1 second between requests to comply with OpenStreetMap API limits

#             geolocator = Nominatim(user_agent="location_serializer")
#             location = geolocator.reverse((coordinates.y, coordinates.x), exactly_one=True)
#             address_data = location.raw['address'] if location else {}

#             validated_data['address'] = location.address if location else 'Unknown Address'
#             validated_data['city'] = address_data.get('city', 'Unknown City')
#             validated_data['country'] = address_data.get('country', 'Unknown Country')

#         except (GeocoderTimedOut, GeocoderServiceError) as e:
#             raise serializers.ValidationError({
#                 'message': f"Failed to fetch location details: {str(e)}"
#             })

#         return super().create(validated_data)


# class RecordSerializer(serializers.ModelSerializer):
#     genre = GenreSerializer(read_only=True)
#     genre_id = serializers.PrimaryKeyRelatedField(
#         queryset=Genre.objects.all(),
#         source='genre',
#         write_only=True
#     )

#     record_condition = GoldmineConditionRecordSerializer(read_only=True)
#     record_condition_id = serializers.PrimaryKeyRelatedField(
#         queryset=GoldmineConditionRecord.objects.all(),
#         source='record_condition',
#         write_only=True
#     )

#     cover_condition = GoldmineConditionCoverSerializer(read_only=True)
#     cover_condition_id = serializers.PrimaryKeyRelatedField(
#         queryset=GoldmineConditionCover.objects.all(),
#         source='cover_condition',
#         write_only=True
#     )

#     user = UserSerializer(read_only=True)

#     photos = PhotoSerializer(many=True, read_only=True)
#     add_photos = serializers.ListField(
#         child=serializers.ImageField(),
#         required=False,
#         write_only=True
#     )

#     location = LocationSerializer()

#     class Meta:
#         model = Record
#         fields = (
#             'id', 
#             'catalog_number', 
#             'artist', 
#             'album_name', 
#             'release_year', 
#             'genre',
#             'genre_id', # For creating via ID 
#             'location', 
#             'available_for_exchange',
#             'additional_description', 
#             'record_condition',
#             'record_condition_id',  # For creating via ID
#             'cover_condition',
#             'cover_condition_id',   # For creating via ID
#             'user',
#             'photos',
#             'add_photos'   # Photos uploaded when adding new record
#         )
#         read_only_fields = (
#             'id',
#             'user',
#             'genre',
#             'record_condition',
#             'cover_condition',
#             'photos'
#         )

#     def validate(self, data):
#         user = self.context.get('user')
#         if not user:
#             raise serializers.ValidationError({
#                 'error': "User must be provided when initializing the serializer."
#             })
#         return data

#     @transaction.atomic
#     def create(self, validated_data):
#         """
#         Create a record and handle associated photos.
#         """

#         # Ensure the user is set before creating the object.
#         validated_data['user'] = self.context.get('user')

#         # Extract photos from validated data
#         photos = validated_data.pop('add_photos', [])
#         location_data = validated_data.pop('location', None)

#         try:
#             # Create or fetch the location
#             if location_data and location_data.get('coordinates'):
#                 location_serializer = LocationSerializer(data=location_data)
#                 location_serializer.is_valid(raise_exception=True)
#                 location = location_serializer.save()
#                 validated_data['location'] = location

#             # Create the record
#             record = Record.objects.create(**validated_data)

#             # Validate and create associated photos
#             Photo.objects.bulk_create([
#                 Photo(record=record, image=photo)
#                 for photo in photos
#             ])
#         except Exception as e:
#             raise serializers.ValidationError({
#                 'error': f'Failed to create record and associated photos: {str(e)}'
#             })
        
#         return record
    
#     @transaction.atomic
#     def update(self, instance, validated_data):
#         """
#         Update a record, including location and photos.
#         """
#         location_data = validated_data.pop('location', None)
#         photos = validated_data.pop('add_photos', [])

#         for attr, value in validated_data.items():
#             setattr(instance, attr, value)

#         if location_data:
#             location_serializer = LocationSerializer(data=location_data)
#             location_serializer.is_valid(raise_exception=True)
#             location = location_serializer.save()
#             instance.location = location

#         if photos:
#             Photo.objects.filter(record=instance).delete()
#             Photo.objects.bulk_create([
#                 Photo(record=instance, image=photo)
#                 for photo in photos
#             ])

#         instance.save()

#         return instance


class WishlistSerializer(serializers.ModelSerializer):
    matching_records = serializers.SerializerMethodField()

    class Meta:
        model = Wishlist
        fields = ('id', 'record_catalog_number', 'matching_records')
        read_only_fields = ('id', 'matching_records')

    def get_matching_records(self, obj):
        """
        Fetch records with the same catalog_number as the wishlist entry.
        """
        records = Record.objects.filter(catalog_number=obj.record_catalog_number)
        return RecordSerializer(records, many=True).data

    def validate(self, data):
        user = self.context.get('user')
        if not user:
            raise serializers.ValidationError({
                'error': "User must be provided when initializing the serializer."
            })
        
        if Wishlist.objects.filter(
            record_catalog_number=data['record_catalog_number'],
            user=user
        ).exists():
            raise serializers.ValidationError(
                {"message": "This record catalog number is already added to the user's wishlist."}
            )

        return data

    def create(self, validated_data):
        """
        Ensure the user is set before creating the object.
        """
        validated_data['user'] = self.context.get('user')
        return super().create(validated_data)
 

class ExchangeOfferedRecordSerializer(serializers.ModelSerializer):
    record_id = serializers.PrimaryKeyRelatedField(
        queryset=Record.objects.all(),
        source='record',
        write_only=True
    )
    record = RecordSerializer(read_only=True)

    class Meta:
        model = ExchangeOfferedRecord
        fields = ('id', 'record_id', 'record')
        read_only_fields = ('id', 'record')


class ExchangeRecordRequestedByReceiverSerializer(serializers.ModelSerializer):
    record_id = serializers.PrimaryKeyRelatedField(
        queryset=Record.objects.all(),
        source='record',
        write_only=True
    )
    record = RecordSerializer(read_only=True)

    class Meta:
        model = ExchangeRecordRequestedByReceiver
        fields = ('id', 'record_id', 'record')
        read_only_fields = ('id', 'record')


class ExchangeSerializer(serializers.ModelSerializer):
    initiator_user = UserSerializer(read_only=True)
    receiver_user = UserSerializer(read_only=True)
    next_user_to_review = UserSerializer(read_only=True)
    
    requested_record = RecordSerializer(read_only=True)
    
    offered_records = ExchangeOfferedRecordSerializer(many=True, read_only=True)
    records_requested_by_receiver = ExchangeRecordRequestedByReceiverSerializer(
        many=True, 
        read_only=True
    )

    class Meta:
        model = Exchange
        fields = (
            'id',
            'initiator_user',
            'receiver_user',
            'next_user_to_review',
            'requested_record',
            'completed',
            'creation_datetime',
            'last_modification_datetime',
            'completed_datetime',
            'offered_records',
            'records_requested_by_receiver'
        )
        read_only_fields = fields


class ExchangeCreateSerializer(serializers.ModelSerializer):
    initiator_user = UserSerializer(read_only=True)
    receiver_user = UserSerializer(read_only=True)

    requested_record = RecordSerializer(read_only=True)
    requested_record_id = serializers.PrimaryKeyRelatedField(
        queryset=Record.objects.all(),
        source='requested_record',
        write_only=True
    )

    offered_records = ExchangeOfferedRecordSerializer(many=True, required=True)

    class Meta:
        model = Exchange
        fields = (
            'id',
            'initiator_user',
            'receiver_user',
            'requested_record',
            'requested_record_id',
            'offered_records',
            'creation_datetime'
        )
        read_only_fields = (
            'id',
            'initiator_user',
            'receiver_user',
            'requested_record',
            'creation_datetime'
        )

    def validate(self, data):
        requested_record = data.get('requested_record')

        # Verify the availability of the requested record
        if not requested_record.available_for_exchange:
            raise serializers.ValidationError({
                'message': "The requested record is not available for exchange."
            })
        
        # Ensure at least one record is offered
        offered_records = data.get('offered_records', [])
        if not offered_records:
            raise serializers.ValidationError({
                'message': "At least one record must be offered in the exchange."
            })
        
        return data
    
    @transaction.atomic
    def create(self, validated_data):
        initiator_user = self.context.get('user')
        offered_records = validated_data.pop('offered_records', [])
        requested_record = validated_data.pop('requested_record')
        receiver_user = requested_record.user

        exchange = Exchange.objects.create(
            initiator_user=initiator_user,
            receiver_user=receiver_user,
            next_user_to_review=receiver_user,
            requested_record=requested_record
        )

        # Add offered records
        ExchangeOfferedRecord.objects.bulk_create([
            ExchangeOfferedRecord(exchange=exchange, **record_data)
            for record_data in offered_records
        ])

        return exchange


class ExchangeUpdateSerializer(serializers.ModelSerializer):
    initiator_user = UserSerializer(read_only=True)
    receiver_user = UserSerializer(read_only=True)

    offered_records = ExchangeOfferedRecordSerializer(many=True, required=False)
    records_requested_by_receiver = ExchangeRecordRequestedByReceiverSerializer(
        many=True, 
        required=False
    )

    class Meta:
        model = Exchange
        fields = (
            'id',
            'initiator_user',
            'receiver_user',
            'completed',
            'next_user_to_review',
            'creation_datetime',
            'last_modification_datetime',
            'offered_records',
            'records_requested_by_receiver'
        )
        read_only_fields = (
            'id',
            'initiator_user',
            'receiver_user',
            'completed',
            'next_user_to_review',
            'creation_datetime',
            'last_modification_datetime'
        )

    def validate(self, data):
        user = self.context.get('user')
        instance = self.instance

        if not instance:
            raise serializers.ValidationError({
                'message': "Update requires an existing exchange instance."
            })
        
        # At least one record must be offered
        offered_records = data.get('offered_records', instance.offered_records.all())
        if not offered_records:
            raise serializers.ValidationError({
                "message": "At least one record must be offered in the exchange."
            })

        return data
    
    @transaction.atomic
    def update(self, instance, validated_data):
        user = self.context.get('user')
        offered_records = validated_data.pop('offered_records', [])
        records_requested_by_receiver = validated_data.pop('records_requested_by_receiver', [])

        if user == instance.receiver_user:
            self._handle_receiver_update(
                instance, 
                offered_records, 
                records_requested_by_receiver
            )
        elif user == instance.initiator_user:
            self._handle_initiator_update(
                instance, 
                offered_records, 
                records_requested_by_receiver
            )

        instance.save()
        return instance

    def _handle_receiver_update(self, instance, offered_records, records_requested_by_receiver):
        existing_offered_record_ids = set(
            instance.offered_records.values_list('record_id', flat=True)
        )

        new_offered_record_ids = set(
            record_data['record'].id for record_data in offered_records
        )

        if not new_offered_record_ids.issubset(existing_offered_record_ids):
            raise serializers.ValidationError({
                "message": "Receiver cannot add new records to the offer, only remove existing ones."
            })
        
        ExchangeOfferedRecord.objects.filter(exchange=instance).exclude(
            record_id__in=new_offered_record_ids
        ).delete()

        ExchangeRecordRequestedByReceiver.objects.filter(exchange=instance).delete()
        ExchangeRecordRequestedByReceiver.objects.bulk_create([
            ExchangeRecordRequestedByReceiver(exchange=instance, **record_data)
            for record_data in records_requested_by_receiver
        ])

    def _handle_initiator_update(self, instance, offered_records, records_requested_by_receiver):
        valid_requested_record_ids = set(
            instance.records_requested_by_receiver.values_list('record_id', flat=True)
        )

        received_requested_record_ids = set(
            record_data['record'].id for record_data in records_requested_by_receiver
        )

        if not received_requested_record_ids.issubset(valid_requested_record_ids):
            raise serializers.ValidationError({
                "message": "Some of the requested records are not part of the receiver's original requests."
            })
        
        ExchangeOfferedRecord.objects.filter(exchange=instance).delete()
        ExchangeOfferedRecord.objects.bulk_create([
            ExchangeOfferedRecord(exchange=instance, **record_data)
            for record_data in offered_records
        ])

        ExchangeRecordRequestedByReceiver.objects.filter(exchange=instance).delete()
        ExchangeRecordRequestedByReceiver.objects.bulk_create([
            ExchangeRecordRequestedByReceiver(exchange=instance, **record_data)
            for record_data in records_requested_by_receiver
        ])
