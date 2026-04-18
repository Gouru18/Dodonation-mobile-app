from django.contrib import admin
from .models import Meeting

@admin.register(Meeting)
class MeetingAdmin(admin.ModelAdmin):
    list_display = ['get_donation_title', 'get_donor', 'get_ngo', 'scheduled_time', 'status']
    list_filter = ['status', 'scheduled_time']
    search_fields = ['claim_request__donation__title']
    readonly_fields = ['created_at', 'updated_at']
    fields = [
        'claim_request',
        'scheduled_time',
        'meeting_link',
        'meeting_latitude',
        'meeting_longitude',
        'meeting_address',
        'status',
        'created_at',
        'updated_at',
    ]

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'claim_request':
            current_claim_id = getattr(getattr(request, '_obj_', None), 'claim_request_id', None)
            kwargs['queryset'] = (
                self.model.claim_request.field.remote_field.model.objects.filter(
                    status='accepted',
                    meeting__isnull=True,
                ) | self.model.claim_request.field.remote_field.model.objects.filter(pk=current_claim_id)
            )
            kwargs['help_text'] = 'Meeting location should be added only after a donor accepts a claim request.'
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_form(self, request, obj=None, **kwargs):
        request._obj_ = obj
        return super().get_form(request, obj, **kwargs)
    
    def get_donation_title(self, obj):
        return obj.claim_request.donation.title
    get_donation_title.short_description = 'Donation'
    
    def get_donor(self, obj):
        return obj.claim_request.donation.donor.email
    get_donor.short_description = 'Donor'
    
    def get_ngo(self, obj):
        return obj.claim_request.receiver.email
    get_ngo.short_description = 'NGO'
