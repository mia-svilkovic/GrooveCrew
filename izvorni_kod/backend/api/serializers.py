from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.db import transaction
from django.utils import timezone

from rest_framework import serializers

from .models import *

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
        read_only_fields = (
            'id',
            'user',
            'genre',
            'record_condition',
            'cover_condition',
            'photos'
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
    

class WishlistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wishlist
        fields = ('id', 'record_catalog_number')
        read_only_fields = ('id',)

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

    requested_record = RecordSerializer(read_only=True)
    requested_record_id = serializers.PrimaryKeyRelatedField(
        queryset=Record.objects.all(),
        source='requested_record',
        write_only=True,
        required=False
    )

    offered_records = ExchangeOfferedRecordSerializer(many=True, required=False)
    records_requested_by_receiver = ExchangeOfferedRecordSerializer(many=True, required=False)

    class Meta:
        model=Exchange
        fields=(
            'id',
            'initiator_user',
            'receiver_user',
            'requested_record',
            'requested_record_id',
            'completed',
            'next_user_to_review',
            'creation_datetime',
            'last_modification_datetime',
            'offered_records',
            'records_requested_by_receiver'
        )
        read_only_fields = (
            'id', 'initiator_user', 'receiver_user', 'requested_record',
            'completed', 'next_user_to_review', 'creation_datetime',
            'last_modification_datetime'
        )

    def validate(self, data):
        """
        General validation of all exchange rules.
        """
        instance = getattr(self, 'instance', None)

        # If this is an update (an instance exists)
        if instance:
            # The next user to review
            next_user = data.get('next_user_to_review', instance.next_user_to_review)
            if next_user not in [instance.initiator_user, instance.receiver_user]:
                raise serializers.ValidationError({
                    "message": "The next user to review must be either the initiator or receiver."
                })

            # Validation of the requested record
            requested_record = data.get('requested_record', instance.requested_record)
            if requested_record.user != instance.receiver_user:
                raise serializers.ValidationError({
                    "message": "The requested record must belong to the receiver user."
                })
            if not requested_record.available_for_exchange:
                raise serializers.ValidationError({
                    "message": "The requested record is not available for exchange."
                })

            # At least one record must be offered
            offered_records = data.get('offered_records', instance.offered_records.all())
            if not offered_records:
                raise serializers.ValidationError({
                    "message": "At least one record must be offered in the exchange."
                })

            # Ensure every record in records_requested_by_receiver belongs to the initiator user
            records_requested_by_receiver = data.get('records_requested_by_receiver', [])
            for record_data in records_requested_by_receiver:
                record = record_data['record']
                if record.user != instance.initiator_user:
                    raise serializers.ValidationError({
                        "message": f"Record '{record}' does not belong to the initiator user and cannot be requested."
                    })

        # If this is creating a new instance
        else:
            requested_record = data.get('requested_record')
            if not requested_record:
                raise serializers.ValidationError({
                    "message": "A requested record must be specified."
                })

            # Verify the availability of the requested record
            if not requested_record.available_for_exchange:
                raise serializers.ValidationError({
                    "message": "The requested record is not available for exchange." 
                })

            # Ensure at least one record is offered
            offered_records = data.get('offered_records', [])
            if not offered_records:
                raise serializers.ValidationError({
                    "message": "At least one record must be offered in the exchange."
                })

            # Prevent specifying records_requested_by_receiver during creation
            if 'records_requested_by_receiver' in data and data['records_requested_by_receiver']:
                raise serializers.ValidationError({
                    "message": "You cannot specify 'records_requested_by_receiver' when creating a new exchange."
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
    
    @transaction.atomic
    def update(self, instance, validated_data):
        offered_records = validated_data.pop('offered_records', [])
        records_requested_by_receiver = validated_data.pop('records_requested_by_receiver', [])
        user = self.context.get('user')

        if user == instance.receiver_user:
            self._handle_receiver_update(instance, offered_records, records_requested_by_receiver)
        elif user == instance.initiator_user:
            self._handle_initiator_update(instance, offered_records, records_requested_by_receiver)

        instance.save()
        return instance

    def _handle_receiver_update(self, instance, offered_records, records_requested_by_receiver):        
        # Fetch the current records in the offer
        existing_offered_record_ids = set(
            instance.offered_records.values_list('record_id', flat=True)
        )

        # Fetch the IDs of records the receiver wants to keep
        new_offered_record_ids = set(
            record_data['record'].id for record_data in offered_records
        )

        # Ensure the receiver is not adding new records to the offer
        if not new_offered_record_ids.issubset(existing_offered_record_ids):
            raise serializers.ValidationError({
                "message": "Receiver cannot add new records to the offer, only remove existing ones."
            })

        # Update the offer records (remove any excluded records)
        ExchangeOfferedRecord.objects.filter(exchange=instance).exclude(
            record_id__in=new_offered_record_ids
        ).delete()

        # Receiver can update their requested records
        ExchangeRecordRequestedByReceiver.objects.filter(exchange=instance).delete()
        ExchangeRecordRequestedByReceiver.objects.bulk_create([
            ExchangeRecordRequestedByReceiver(exchange=instance, **record_data)
            for record_data in records_requested_by_receiver
        ])

    def _handle_initiator_update(self, instance, offered_records, records_requested_by_receiver):
        # Verify that all records in records_requested_by_receiver actually exist in the receiver's requests
        valid_requested_record_ids = set(
            instance.records_requested_by_receiver.values_list('record_id', flat=True)
        )

        received_requested_record_ids = set(
            record_data['record'].id for record_data in records_requested_by_receiver
        )

        invalid_requested_records = received_requested_record_ids - valid_requested_record_ids
        if invalid_requested_records:
            raise serializers.ValidationError({
                "message": "Some of the requested records are not part of the receiver's original requests."
            })

        # Initiator can update offered records
        ExchangeOfferedRecord.objects.filter(exchange=instance).delete()
        ExchangeOfferedRecord.objects.bulk_create([
            ExchangeOfferedRecord(exchange=instance, **record_data)
            for record_data in offered_records
        ])

        # Clear the receiver's requests
        ExchangeRecordRequestedByReceiver.objects.filter(exchange=instance).delete()
        ExchangeRecordRequestedByReceiver.objects.bulk_create([
            ExchangeRecordRequestedByReceiver(exchange=instance, **record_data)
            for record_data in records_requested_by_receiver
        ])
