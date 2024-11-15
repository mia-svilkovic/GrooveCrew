from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
import re

class UserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError('Email address is required')
        if not username:
            raise ValueError('Username is required')
            
        email = self.normalize_email(email)
        user = self.model(
            email=email,
            username=username,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(email, username, password, **extra_fields)

class User(AbstractUser):
    # Custom user fields
    email = models.EmailField(
        "Email address",
        max_length=128,
        unique=True,
        help_text="Required. User's email address for authentication."
    )
    username = models.CharField(
        "Username",
        max_length=32,
        unique=True,
        help_text="Required. 32 characters or fewer."
    )
    first_name = models.CharField(
        "First Name",
        max_length=64,
        help_text="User's first name."
    )
    last_name = models.CharField(
        "Last name",
        max_length=64,
        help_text="User's last name."
    )
    
    # Boolean flags
    is_active = models.BooleanField(
        "Active",
        default=True,
        help_text="Designates whether this user account is active."
    )

    is_staff = models.BooleanField(
        "Staff",
        default=False,
        help_text="Designates whether the user can access admin site."
    )
    is_superuser = models.BooleanField(
        "Superuser",
        default=False,
        help_text="Designates whether the user is a superuser."
    )

    # Authentication settings
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    objects = UserManager()

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.username})"

    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser
    
    def clean(self):
        super().clean()
        if self.password:
            if len(self.password) < 8:
                raise ValidationError('Password must be at least 8 characters long')
            if not re.search(r'[A-Z]', self.password):
                raise ValidationError('Password must contain at least one uppercase letter')
            if not re.search(r'[a-z]', self.password):
                raise ValidationError('Password must contain at least one lowercase letter')
            if not re.search(r'\d', self.password):
                raise ValidationError('Password must contain at least one number')

    def email_clean(self):
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', self.email):
            raise ValidationError('Invalid email format')

class GoldmineCondition(models.Model):
    name = models.CharField(max_length=32)
    abbreviation = models.CharField(max_length=8)
    description = models.CharField(max_length=256)

    def __str__(self):
        return f"{self.name} ({self.abbreviation})"
    
    class Meta:
        verbose_name = "Goldmine Condition"
        verbose_name_plural = "Goldmine Conditions"

class Record(models.Model):
    release_mark = models.CharField(max_length=128)
    artist = models.CharField(max_length=128)
    album_name = models.CharField(max_length=128)
    release_year = models.IntegerField()
    genre = models.CharField(max_length=64)
    location = models.CharField(max_length=64)
    available_for_trade = models.BooleanField(default=False)
    additional_description = models.CharField(max_length=256, blank=True)
    record_condition = models.ForeignKey(GoldmineCondition, on_delete=models.PROTECT, related_name='record_conditions')
    sleeve_condition = models.ForeignKey(GoldmineCondition, on_delete=models.PROTECT, related_name='sleeve_conditions')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.artist} - {self.album_name}"
    
    class Meta:
        verbose_name = "Record"
        verbose_name_plural = "Records"
