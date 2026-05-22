from django.contrib import admin
from .models import VolunteerSignup, BusinessSignup, PodcastEpisode, Testimonial, DonationRecord


@admin.register(VolunteerSignup)
class VolunteerAdmin(admin.ModelAdmin):
    list_display  = ['first_name', 'last_name', 'email', 'age', 'avail_days', 'avail_start', 'avail_end', 'created_at']
    list_filter   = ['created_at']
    search_fields = ['first_name', 'last_name', 'email', 'school']
    readonly_fields = ['created_at']


@admin.register(BusinessSignup)
class BusinessAdmin(admin.ModelAdmin):
    list_display  = ['business_name', 'contact_name', 'email', 'business_type', 'city', 'state', 'created_at']
    list_filter   = ['business_type', 'state', 'created_at']
    search_fields = ['business_name', 'contact_name', 'email', 'city']
    readonly_fields = ['created_at']


@admin.register(PodcastEpisode)
class PodcastAdmin(admin.ModelAdmin):
    list_display  = ['title', 'guest_name', 'episode_type', 'published_date', 'is_featured']
    list_filter   = ['episode_type', 'is_featured', 'published_date']
    search_fields = ['title', 'guest_name']
    list_editable = ['is_featured']


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display  = ['name', 'role', 'is_active', 'created_at']
    list_filter   = ['is_active']
    list_editable = ['is_active']


@admin.register(DonationRecord)
class DonationAdmin(admin.ModelAdmin):
    list_display  = ['donor_name', 'donor_email', 'amount', 'method', 'created_at']
    list_filter   = ['method', 'created_at']
    search_fields = ['donor_name', 'donor_email']
    readonly_fields = ['created_at']
