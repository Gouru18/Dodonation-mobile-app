from django.contrib import admin
from accounts.models import User
from .models import Donation, ClaimRequest

@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = ['title', 'donor_email', 'category', 'status', 'created_at']
    list_filter = ['status', 'category', 'created_at']
    search_fields = ['title', 'donor__email']
    readonly_fields = ['created_at', 'updated_at']

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'donor':
            kwargs['queryset'] = User.objects.filter(role='donor')
        if db_field.name == 'receiver':
            kwargs['queryset'] = User.objects.filter(role='ngo')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
    def donor_email(self, obj):
        return obj.donor.email
    donor_email.short_description = 'Donor Email'


@admin.register(ClaimRequest)
class ClaimRequestAdmin(admin.ModelAdmin):
    list_display = ['donation_title', 'receiver_email', 'status', 'date_requested']
    list_filter = ['status', 'date_requested']
    search_fields = ['donation__title', 'receiver__email']
    readonly_fields = ['date_requested', 'date_responded']
    
    def donation_title(self, obj):
        return obj.donation.title
    donation_title.short_description = 'Donation'
    
    def receiver_email(self, obj):
        return obj.receiver.email
    receiver_email.short_description = 'Receiver Email'
