from rest_framework import serializers
from .models import CustomUser, VinylRecord, GoldmineCondition

class UserSerializer(serializers.ModelSerializer):
    password_confirm = serializers.CharField(write_only=True)
    class Meta:
        model = CustomUser
        fields = ('id', 'email', 'username', 'first_name', 'last_name', 'password', 'password_confirm', 'is_active', 'is_staff', 'is_superuser')
        extra_kwargs = {
            'password': {'write_only': True},
            'is_superuser': {'read_only': True},
            'is_staff': {'read_only': True},
            'is_active': {'read_only': True}
        }

    def validate(self, data):
        if data.get('password') != data.get('password_confirm'):
            raise serializers.ValidationError("Passwords don't match")
        
        if CustomUser.objects.filter(email=data.get('email')).exists():
            raise serializers.ValidationError("Email already exists")
            
        if CustomUser.objects.filter(username=data.get('username')).exists():
            raise serializers.ValidationError("Username already exists")
            
        return data

    def create(self, validated_data):
        password = validated_data.pop('password')
        validated_data.pop('password_confirm', None)
        user = CustomUser(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        validated_data.pop('password_confirm', None)
        
        if password:
            instance.set_password(password)
            
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
            
        instance.save()
        return instance
    
class GoldmineConditionSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoldmineCondition
        fields = ('id', 'name', 'abbreviation', 'description')


class RecordSerializer(serializers.ModelSerializer):
    record_condition_detail = GoldmineConditionSerializer(source='record_condition', read_only=True)
    cover_condition_detail = GoldmineConditionSerializer(source='cover_condition', read_only=True)
    user_detail = UserSerializer(source='user', read_only=True)

    class Meta:
        model = VinylRecord
        fields = [
            'id', 
            'release_code', 
            'artist', 
            'album_name', 
            'release_year', 
            'genre', 
            #'location', 
            'available_for_exchange',
            'additional_description', 
            'record_condition',
            'record_condition_detail', 
            'cover_condition',
            'cover_condition_detail',
            'user_detail'
        ]
        read_only_fields = ['id', 'user_detail', 'record_condition_detail', 'sleeve_condition_detail']

    def create(self, validated_data):
       user = self.context['request'].user
       record = VinylRecord.objects.create(user=user, **validated_data)
       return record