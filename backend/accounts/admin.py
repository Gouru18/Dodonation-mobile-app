from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import User, OTPCode

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    actions = ['activate_accounts', 'suspend_accounts']
    fieldsets = BaseUserAdmin.fieldsets + (
        (
            'Custom Fields',
            {
                'fields': (
                    'role',
                    'phone',
                    'is_phone_verified',
                    'is_email_verified',
                    'ngo_organization_name',
                    'ngo_registration_number',
                    'ngo_permit_status',
                    'ngo_permit_file_link',
                )
            },
        ),
    )
    list_display = ['username', 'email', 'role', 'is_active', 'ngo_permit_status']
    list_filter = ['role', 'is_active', 'is_email_verified']
    readonly_fields = [
        'ngo_organization_name',
        'ngo_registration_number',
        'ngo_permit_status',
        'ngo_permit_file_link',
    ]

    @admin.action(description="Activate selected accounts")
    def activate_accounts(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f"{updated} account(s) activated.")

    @admin.action(description="Suspend selected accounts")
    def suspend_accounts(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f"{updated} account(s) suspended.")

    def ngo_organization_name(self, obj):
        ngo_profile = getattr(obj, 'ngo_profile', None)
        return getattr(ngo_profile, 'organization_name', '-')
    ngo_organization_name.short_description = 'NGO organization'

    def ngo_registration_number(self, obj):
        ngo_profile = getattr(obj, 'ngo_profile', None)
        return getattr(ngo_profile, 'registration_number', '-') or '-'
    ngo_registration_number.short_description = 'Registration number'

    def ngo_permit_status(self, obj):
        ngo_profile = getattr(obj, 'ngo_profile', None)
        permit = getattr(ngo_profile, 'permit_application', None) if ngo_profile else None
        return getattr(permit, 'status', '-') or '-'
    ngo_permit_status.short_description = 'Permit status'

    def ngo_permit_file_link(self, obj):
        ngo_profile = getattr(obj, 'ngo_profile', None)
        permit = getattr(ngo_profile, 'permit_application', None) if ngo_profile else None
        permit_file = getattr(permit, 'permit_file', None)
        if permit_file and getattr(permit_file, 'url', None):
            return format_html('<a href="{}" target="_blank">Open uploaded permit</a>', permit_file.url)
        return 'No permit uploaded'
    ngo_permit_file_link.short_description = 'Uploaded permit'


@admin.register(OTPCode)
class OTPCodeAdmin(admin.ModelAdmin):
    list_display = ['user', 'code', 'created_at', 'is_used', 'expires_at']
    list_filter = ['is_used', 'created_at']
    search_fields = ['user__email']
    readonly_fields = ['created_at', 'expires_at']
