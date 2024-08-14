from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Escola

class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('tipo_usuario', 'escola')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('tipo_usuario', 'escola')}),
    )

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Escola)
