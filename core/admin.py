from django.contrib import admin
from .models import VolunteerEvent, VolunteerSignup, BusinessSignup, PodcastEpisode, Testimonial, DonationRecord, StaffProfile


@admin.register(StaffProfile)
class StaffProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'created_at']


@admin.register(VolunteerEvent)
class VolunteerEventAdmin(admin.ModelAdmin):
    list_display = ['title', 'date', 'start_time', 'location', 'max_volunteers', 'is_active']


@admin.register(VolunteerSignup)
class VolunteerAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'email', 'event', 'created_at']
    list_filter  = ['event', 'created_at']


@admin.register(BusinessSignup)
class BusinessAdmin(admin.ModelAdmin):
    list_display = ['business_name', 'contact_name', 'email', 'city', 'created_at']


@admin.register(PodcastEpisode)
class PodcastAdmin(admin.ModelAdmin):
    list_display = ['title', 'guest_name', 'episode_type', 'published_date', 'is_featured']


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ['name', 'role', 'is_active', 'created_at']


@admin.register(DonationRecord)
class DonationAdmin(admin.ModelAdmin):
    list_display = ['donor_name', 'amount', 'method', 'created_at']
