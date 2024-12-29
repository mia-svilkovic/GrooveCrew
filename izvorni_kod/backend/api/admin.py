from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import (
    Exchange, ExchangeOfferedRecord, Genre,
    GoldmineConditionCover, GoldmineConditionRecord,
    Photo, Record, User, Wishlist
)

@admin.register(User)
class UserAdmin(UserAdmin):
    """fieldsets and add_fieldsets need to be adjusted so admin knows how to
    display them."""

    # Display / editing in the admin (for existing users)
    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    # Fields shown when creating a new user in the admin
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'first_name', 'last_name', 'password1', 'password2'),
        }),
    )

    list_display = ('email', 'username', 'first_name', 'last_name', 'is_staff')
    search_fields = ('email', 'username', 'first_name', 'last_name')
    ordering = ('email',)


admin.site.register(Record)
admin.site.register(Genre)
admin.site.register(GoldmineConditionCover)
admin.site.register(GoldmineConditionRecord)
admin.site.register(Photo)
admin.site.register(Exchange)
admin.site.register(ExchangeOfferedRecord)
admin.site.register(Wishlist)
