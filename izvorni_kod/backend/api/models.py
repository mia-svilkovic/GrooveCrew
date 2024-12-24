from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    email = models.EmailField(
        unique=True,
        null=False,
        blank=False)

    username = models.CharField(
        max_length=150,
        unique=True,
        null=False,
        blank=False)

    first_name = models.CharField(
        max_length=150,
        null=False,
        blank=False)

    last_name = models.CharField(
        max_length=150,
        null=False,
        blank=False)

    # Use email as the primary login field
    USERNAME_FIELD = 'email'

    # Fields that *must* be provided when creating a superuser via
    # `createsuperuser` USERNAME_FIELD + password must be provided by default
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    def __str__(self):
        return self.email


class Record(models.Model):    
    catalog_number = models.CharField(max_length=255)

    artist = models.CharField(max_length=255)

    album_name = models.CharField(max_length=255)

    release_year = models.IntegerField()

    genre = models.ForeignKey(
        'Genre',
        on_delete=models.SET_NULL,
        null=True,
        related_name='records')

    location = models.CharField(max_length=255)

    available_for_exchange = models.BooleanField(default=True)

    additional_description = models.TextField(blank=True, null=True)

    record_condition = models.ForeignKey(
        'GoldmineConditionRecord',
        on_delete=models.SET_NULL,
        related_name='records',
        null=True)

    cover_condition = models.ForeignKey(
        'GoldmineConditionCover',
        on_delete=models.SET_NULL,
        related_name='records',
        null=True)

    user = models.ForeignKey(
        'CustomUser',
        on_delete=models.CASCADE,
        related_name='records')

    def __str__(self):
        return f'{self.artist} - {self.album_name}'


class Genre(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name
    

class GoldmineConditionRecord(models.Model):
    name = models.CharField(max_length=100, unique=True)

    abbreviation = models.CharField(max_length=10, unique=True)

    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class GoldmineConditionCover(models.Model):
    name = models.CharField(max_length=100, unique=True)

    abbreviation = models.CharField(max_length=10, unique=True)

    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class Photo(models.Model):
    image = models.ImageField(upload_to='record_photos/')

    record = models.ForeignKey(
        'Record',
        on_delete=models.CASCADE,
        related_name='photos')

    def __str__(self):
        return f'Photo for {self.record.album_name}'


class Exchange(models.Model):
    class ExchangeStatus(models.TextChoices):
        PENDING = 'pending', 'Pending'
        ACCEPTED = 'accepted', 'Accepted'
        REJECTED = 'rejected', 'Rejected'

    creation_datetime = models.DateTimeField(auto_now_add=True)

    last_modification_datetime = models.DateTimeField(auto_now=True)

    exchange_status = models.CharField(
        max_length=10,
        choices=ExchangeStatus.choices,
        default=ExchangeStatus.PENDING)
    
    initiator_user = models.ForeignKey(
        'CustomUser', 
        on_delete=models.CASCADE,
        related_name='initiated_exchanges'
    )

    receiver_user = models.ForeignKey(
        'CustomUser',
        on_delete=models.CASCADE,
        related_name='received_exchanges')

    user_to_review = models.ForeignKey(
        'CustomUser',
        on_delete=models.CASCADE,
        related_name='exchanges_to_review')

    requested_record = models.ForeignKey(
        'Record',
        on_delete=models.CASCADE,
        related_name='requesting_exchanges')

    def __str__(self):
        return f'Exchange between {self.initiator_user} and {self.receiver_user}'


class ExchangeOfferedRecord(models.Model):
    class RecordStatus(models.TextChoices):
        PENDING = 'pending', 'Pending'
        ACCEPTED = 'accepted', 'Accepted'
        REJECTED = 'rejected', 'Rejected'

    exchange = models.ForeignKey(
        'Exchange',
        on_delete=models.CASCADE,
        related_name='offered_records')

    offered_record = models.ForeignKey(
        'Record',
        on_delete=models.CASCADE,
        related_name='exchanges_where_offered')

    record_status = models.CharField(
        max_length=50,
        choices=RecordStatus.choices,
        default=RecordStatus.PENDING)

    def __str__(self):
        return f'Offered {self.offered_record} in exchange {self.exchange.id}'


class Wishlist(models.Model):
    record_catalog_number = models.CharField(max_length=255)

    user = models.ForeignKey(
        'CustomUser',
        on_delete=models.CASCADE,
        related_name='wishlist')

    def __str__(self):
        return f'{self.user} wishes for {self.record_catalog_number}'
