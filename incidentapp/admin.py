from django.contrib import admin
from .models import IncidentModel,CustomUser
from django.contrib.auth.admin import UserAdmin


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('email', 'first_name', 'last_name', 'phone_number', 'city', 'state', 'country', 'is_staff')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'phone_number', 'address', 'pincode', 'city', 'state', 'country')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'user_permissions', 'groups')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'phone_number', 'address', 'pincode', 'city', 'state', 'country', 'password1', 'password2'),
        }),
    )
    search_fields = ('email',)
    ordering = ('email',)

admin.site.register(CustomUser, CustomUserAdmin)

class IncidentAdmin(admin.ModelAdmin):
    list_display = ('incident_id', 'user', 'incident_type', 'reporter_name', 'reported_date', 'priority', 'status')
    search_fields = ('incident_id', 'reporter_name', 'incident_details')
    list_filter = ('priority', 'status','incident_type')
    readonly_fields = ('incident_id', 'reported_date')

admin.site.register(IncidentModel,IncidentAdmin)