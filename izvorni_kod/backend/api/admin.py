from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    # properties to display in the admin list
    list_display = ('email', 'username', 'first_name', 'last_name', 'is_staff', 'is_active')
    
    # Fields to use for editing an individual user's profile
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'username')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'is_superuser', 'groups', 'user_permissions')}),
    )
    # Fields to display when creating a new user through the admin
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'username', 'password1', 'password2', 'is_staff', 'is_active')}
        ),
    )

    # Fields to search by in the admin list view
    search_fields = ('email', 'first_name', 'last_name', 'username')
    ordering = ('email',)

# Register CustomUser with the specified admin configuration
admin.site.register(CustomUser, CustomUserAdmin)
