from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from .models import CustomUser

class UserAdmin(BaseUserAdmin):
    list_display = ('nickname', 'userID', 'oauthID', 'score', 'is_staff', 'is_superuser')
    list_filter = ('is_staff', 'is_superuser')
    fieldsets = (
        (None, {'fields': ('nickname', 'password')}),
        ('Personal info', {'fields': ('userID', 'oauthID', 'score', 'image')}),
        ('Permissions', {'fields': ('is_staff', 'is_superuser', 'is_active')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('nickname', 'password1', 'password2', 'userID', 'oauthID', 'score', 'image', 'is_staff', 'is_superuser'),
        }),
    )
    search_fields = ('nickname', 'userID', 'oauthID')
    ordering = ('nickname',)
    filter_horizontal = ()

admin.site.register(CustomUser, UserAdmin)
admin.site.unregister(Group)
