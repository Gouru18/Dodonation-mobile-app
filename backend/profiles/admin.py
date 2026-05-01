from django.contrib import admin
from django.utils.html import format_html
from accounts.models import User
from core.email_utils import send_ngo_status_email
from .models import DonorProfile, NGOProfile, NGOPermitApplication

@admin.register(DonorProfile)
class DonorProfileAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'user_email']
    search_fields = ['full_name', 'user__email']

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'user':
            kwargs['queryset'] = User.objects.filter(
                role='donor',
                donor_profile__isnull=True,
            ) | User.objects.filter(pk=getattr(getattr(request, '_obj_', None), 'user_id', None))
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_form(self, request, obj=None, **kwargs):
        request._obj_ = obj
        return super().get_form(request, obj, **kwargs)
    
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'Email'


@admin.register(NGOProfile)
class NGOProfileAdmin(admin.ModelAdmin):
    list_display = ['organization_name', 'user_email', 'registration_number']
    search_fields = ['organization_name', 'user__email']

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'user':
            kwargs['queryset'] = User.objects.filter(
                role='ngo',
                ngo_profile__isnull=True,
            ) | User.objects.filter(pk=getattr(getattr(request, '_obj_', None), 'user_id', None))
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_form(self, request, obj=None, **kwargs):
        request._obj_ = obj
        return super().get_form(request, obj, **kwargs)
    
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'Email'


@admin.register(NGOPermitApplication)
class NGOPermitApplicationAdmin(admin.ModelAdmin):
    list_display = ['ngo_name', 'status', 'submitted_at', 'reviewed_by', 'permit_file_link']
    list_filter = ['status', 'submitted_at']
    search_fields = ['ngo__organization_name']
    readonly_fields = ['submitted_at', 'reviewed_at', 'permit_file_link']
    
    def ngo_name(self, obj):
        return obj.ngo.organization_name
    ngo_name.short_description = 'NGO'

    def permit_file_link(self, obj):
        if obj.permit_file and getattr(obj.permit_file, 'url', None):
            return format_html('<a href="{}" target="_blank">Open uploaded permit</a>', obj.permit_file.url)
        return 'No file uploaded'
    permit_file_link.short_description = 'Permit file'

    def save_model(self, request, obj, form, change):
        previous_status = None
        if change and obj.pk:
            try:
                previous_status = NGOPermitApplication.objects.get(pk=obj.pk).status
            except NGOPermitApplication.DoesNotExist:
                previous_status = None

        super().save_model(request, obj, form, change)

        if change and previous_status != obj.status and obj.status in {'approved', 'rejected'}:
            if obj.status == 'approved' and not obj.ngo.user.is_active:
                obj.ngo.user.is_active = True
                obj.ngo.user.save(update_fields=['is_active'])

            send_ngo_status_email(
                obj.ngo.user.email,
                obj.status,
                obj.ngo.organization_name,
                obj.rejection_reason,
            )
