from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password, **extra_fields):
        
        if not email:
            raise ValueError("The Email field must be set")
        
        if not password:
            raise ValueError("The Password field must be set")
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=64, null=False, blank=False, default="name")
    last_name = models.CharField(max_length=64, null=False, blank=False, default="lastname")
    username = models.CharField(max_length=32, null=False, blank=False, default="username")
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'username']

    def __str__(self):
        return self.username
    
    class Meta:
      ordering = ['email']
      verbose_name = 'user'
      verbose_name_plural = 'users'

class GoldmineCondition(models.Model):
    name = models.CharField(max_length=32)
    abbreviation = models.CharField(max_length=8)
    description = models.CharField(max_length=256)

    def __str__(self):
        return self.name

class VinylRecord(models.Model):
    release_code = models.CharField(max_length=128)       
    artist = models.CharField(max_length=128)               
    album_name = models.CharField(max_length=128)          
    release_year = models.IntegerField()                    
    genre = models.CharField(max_length=64)                    
    location = models.JSONField()                            
    available_for_exchange = models.BooleanField()             
    additional_description = models.CharField(max_length=256)          
    
    # Foreign Keys
    record_condition = models.ForeignKey(GoldmineCondition, on_delete=models.CASCADE, related_name="record_condition")  
    cover_condition = models.ForeignKey(GoldmineCondition, on_delete=models.CASCADE, related_name="cover_condition")    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)                                          

    def __str__(self):
        return f"{self.release_code} - {self.album_name}"
    

class Photograph(models.Model):
    binary_content = models.BinaryField()                   
    vinyl_record = models.ForeignKey(VinylRecord, on_delete=models.CASCADE)   #Id of record

    def __str__(self):
        return f"Photo for record with id: {self.vinyl_record.id}"

