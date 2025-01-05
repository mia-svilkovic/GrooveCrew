from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.functions import Lower

class User(AbstractUser):
    email = models.EmailField(
        unique=True,
        null=False,
        blank=False
    )

    username = models.CharField(
        max_length=150,
        unique=True,
        null=False,
        blank=False
    )

    first_name = models.CharField(
        max_length=150,
        null=False,
        blank=False
    )

    last_name = models.CharField(
        max_length=150,
        null=False,
        blank=False
    )

    # Use email as the primary login field
    USERNAME_FIELD = 'email'

    # Fields that *must* be provided when creating a superuser via
    # `createsuperuser` USERNAME_FIELD + password must be provided by default
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users" 

    def __str__(self):
        return f'{self.username} ({self.email})'


class Record(models.Model):    
    catalog_number = models.CharField(max_length=255)

    artist = models.CharField(max_length=255)

    album_name = models.CharField(max_length=255)

    release_year = models.IntegerField()

    genre = models.ForeignKey(
        'Genre',
        on_delete=models.SET_NULL,
        null=True,
        related_name='records'
    )

    location = models.CharField(max_length=255)

    available_for_exchange = models.BooleanField(default=True)

    additional_description = models.TextField(blank=True)

    record_condition = models.ForeignKey(
        'GoldmineConditionRecord',
        on_delete=models.SET_NULL,
        related_name='records',
        null=True,
        blank=True
    )

    cover_condition = models.ForeignKey(
        'GoldmineConditionCover',
        on_delete=models.SET_NULL,
        related_name='records',
        null=True,
        blank=True
    )

    user = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
        related_name='records'
    )
    
    class Meta:
        verbose_name = "Record"
        verbose_name_plural = "Records"

    def __str__(self):
        return f'{self.artist} - {self.album_name} ({self.catalog_number})'


class Genre(models.Model):
    name = models.CharField(max_length=50)

    class Meta:
        verbose_name = "Genre"
        verbose_name_plural = "Genres"
        constraints = [
            models.UniqueConstraint(
                Lower('name'),
                name='unique_genre_case_insensitive',
                violation_error_message='A genre with this name already exists (case insensitive).'
            )
        ]

    def __str__(self):
        return self.name
    

class GoldmineConditionRecord(models.Model):
    name = models.CharField(max_length=100)

    abbreviation = models.CharField(max_length=10)

    description = models.TextField(blank=True)

    class Meta:
        verbose_name = "Goldmine Condition (Record)"
        verbose_name_plural = "Goldmine Conditions (Record)"
        constraints = [
            models.UniqueConstraint(
                Lower('name'),
                name='unique_record_condition_name_case_insensitive',
                violation_error_message='A record condition with this name already exists (case insensitive).'
            ),
            models.UniqueConstraint(
                Lower('abbreviation'),
                name='unique_record_condition_abbreviation_case_insensitive',
                violation_error_message='A record condition with this abbreviation already exists (case insensitive).'
            ),
        ]

    def __str__(self):
        return f'{self.name} ({self.abbreviation})'


class GoldmineConditionCover(models.Model):
    name = models.CharField(max_length=100)

    abbreviation = models.CharField(max_length=10)

    description = models.TextField(blank=True)

    class Meta:
        verbose_name = "Goldmine Condition (Cover)"
        verbose_name_plural = "Goldmine Conditions (Cover)"
        constraints = [
            models.UniqueConstraint(
                Lower('name'),
                name='unique_cover_condition_name_case_insensitive',
                violation_error_message='A cover condition with this name already exists (case insensitive).'
            ),
            models.UniqueConstraint(
                Lower('abbreviation'),
                name='unique_cover_condition_abbreviation_case_insensitive',
                violation_error_message='A cover condition with this abbreviation already exists (case insensitive).'
            ),
        ]

    def __str__(self):
        return f'{self.name} ({self.abbreviation})'


class Photo(models.Model):
    image = models.ImageField(upload_to='record_photos/')

    record = models.ForeignKey(
        'Record',
        on_delete=models.CASCADE,
        related_name='photos'
    )
    
    class Meta:
        verbose_name = "Photo"
        verbose_name_plural = "Photos"

    def __str__(self):
        return f'Photo #{self.pk} for {self.record.artist} - {self.record.album_name}'


class Wishlist(models.Model):
    record_catalog_number = models.CharField(max_length=255)

    user = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
        related_name='wishlist'
    )
    
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['record_catalog_number', 'user'],
                name='unique_record_catalog_number_per_user',
                violation_error_message='This record catalog number is already added to the user\'s wishlist.'
            )
        ]
        
    def __str__(self):
        return f'Wishlist Item (ID: {self.pk}): {self.user} - {self.record_catalog_number}'
            

class Exchange(models.Model):
    creation_datetime = models.DateTimeField(auto_now_add=True)
    last_modification_datetime = models.DateTimeField(auto_now=True)
    completed_datetime = models.DateTimeField(null=True, blank=True)
    
    initiator_user = models.ForeignKey(
        'User', 
        on_delete=models.CASCADE,
        related_name='initiated_exchanges'
    )

    receiver_user = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
        related_name='received_exchanges'
    )

    next_user_to_review = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
        related_name='exchanges_to_review'
    )

    requested_record = models.ForeignKey(
        'Record',
        on_delete=models.CASCADE,
        related_name='requesting_exchanges'
    )

    completed = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = "Exchange"
        verbose_name_plural = "Exchanges"
        constraints = [
            models.UniqueConstraint(
                fields=['initiator_user', 'receiver_user', 'requested_record'],
                name='unique_exchange_per_record_per_user'
            ),
        ]

    def __str__(self):
        return f'Exchange ({self.status}) between {self.initiator_user} and {self.receiver_user}'


class ExchangeOfferedRecord(models.Model):
    exchange = models.ForeignKey(
        'Exchange',
        on_delete=models.CASCADE,
        related_name='offered_records'
    )

    record = models.ForeignKey(
        'Record',
        on_delete=models.CASCADE,
        related_name='exchanges_where_offered'
    )
    
    class Meta:
        verbose_name = "Offered record"
        verbose_name_plural = "Offered records"
        constraints = [
            models.UniqueConstraint(
                fields=['exchange', 'record'],
                name='unique_record_per_exchange'
            ),
        ]

    def __str__(self):
        return f'Offered {self.record} in exchange {self.exchange.id}'


class ExchangeRecordRequestedByReceiver(models.Model):
    exchange = models.ForeignKey(
        'Exchange',
        on_delete=models.CASCADE,
        related_name='records_requested_by_receiver'
    )

    record = models.ForeignKey(
        'Record',
        on_delete=models.CASCADE,
        related_name='exchanges_where_requested_by_receiver'
    )

    class Meta:
        verbose_name = 'Record Requested by Receiver'
        verbose_name_plural = 'Records Requested by Receiver'
        constraints = [
            models.UniqueConstraint(
                fields=['exchange', 'record'],
                name='unique_record_requested_per_exchange'
            )
        ]

    def __str__(self):
        return f'Record "{self.record}" requested by receiver in exchange {self.exchange.id}'
