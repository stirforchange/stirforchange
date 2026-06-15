from django.contrib import admin
from django.contrib.auth.models import User
from .models import VolunteerSignup, BusinessSignup, PodcastEpisode, Testimonial, DonationRecord, StaffProfile


@admin.register(StaffProfile)
class StaffProfileAdmin(admin.ModelAdmin):
    list_display  = ['user', 'role', 'created_by', 'created_at']
    list_filter   = ['role']
    readonly_fields = ['created_at', 'created_by']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        try:
            if request.user.profile.is_owner():
                return qs
        except Exception:
            pass
        return qs.none()

    def has_add_permission(self, request):
        try: return request.user.profile.is_owner()
        except: return False

    def has_delete_permission(self, request, obj=None):
        try: return request.user.profile.is_owner()
        except: return False


@admin.register(VolunteerSignup)
class VolunteerAdmin(admin.ModelAdmin):
    list_display  = ['first_name', 'last_name', 'email', 'age', 'avail_days', 'avail_start', 'avail_end', 'created_at']
    list_filter   = ['created_at']
    search_fields = ['first_name', 'last_name', 'email', 'school']
    readonly_fields = ['created_at']

    def has_add_permission(self, request):
        try: return request.user.profile.is_admin()
        except: return False

    def has_change_permission(self, request, obj=None):
        try: return request.user.profile.is_admin()
        except: return False

    def has_delete_permission(self, request, obj=None):
        try: return request.user.profile.is_owner()
        except: return False


@admin.register(BusinessSignup)
class BusinessAdmin(admin.ModelAdmin):
    list_display  = ['business_name', 'contact_name', 'email', 'business_type', 'city', 'state', 'created_at']
    list_filter   = ['business_type', 'state', 'created_at']
    search_fields = ['business_name', 'contact_name', 'email', 'city']
    readonly_fields = ['created_at']

    def has_add_permission(self, request):
        try: return request.user.profile.is_admin()
        except: return False

    def has_change_permission(self, request, obj=None):
        try: return request.user.profile.is_admin()
        except: return False

    def has_delete_permission(self, request, obj=None):
        try: return request.user.profile.is_owner()
        except: return False


@admin.register(PodcastEpisode)
class PodcastAdmin(admin.ModelAdmin):
    list_display  = ['title', 'guest_name', 'episode_type', 'published_date', 'is_featured']
    list_filter   = ['episode_type', 'is_featured']
    search_fields = ['title', 'guest_name']
    list_editable = ['is_featured']

    def has_module_perms(self, request, app_label=None):
        try: return request.user.profile.is_admin()
        except: return False


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display  = ['name', 'role', 'is_active', 'created_at']
    list_filter   = ['is_active']
    list_editable = ['is_active']

    def has_module_perms(self, request, app_label=None):
        try: return request.user.profile.is_admin()
        except: return False


@admin.register(DonationRecord)
class DonationAdmin(admin.ModelAdmin):
    list_display  = ['donor_name', 'donor_email', 'amount', 'method', 'created_at']
    list_filter   = ['method', 'created_at']
    search_fields = ['donor_name', 'donor_email']
    readonly_fields = ['created_at']

    def has_module_perms(self, request, app_label=None):
        try: return request.user.profile.is_admin()
        except: return False
