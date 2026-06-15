from django.db import models
from django.contrib.auth.models import User
from datetime import date


class StaffProfile(models.Model):
    ROLE_CHOICES = [
        ('owner',     'Owner'),
        ('admin',     'Admin'),
        ('moderator', 'Moderator'),
    ]
    user       = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role       = models.CharField(max_length=20, choices=ROLE_CHOICES, default='moderator')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_staff')
    created_at = models.DateTimeField(auto_now_add=True)

    def is_owner(self):     return self.role == 'owner'
    def is_admin(self):     return self.role in ('owner', 'admin')
    def is_moderator(self): return self.role in ('owner', 'admin', 'moderator')

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"

    class Meta:
        verbose_name = 'Staff Profile'


class VolunteerSignup(models.Model):
    first_name      = models.CharField(max_length=100)
    last_name       = models.CharField(max_length=100)
    email           = models.EmailField()
    phone           = models.CharField(max_length=20, blank=True)
    birthdate       = models.DateField()
    school          = models.CharField(max_length=200, blank=True)
    avail_days      = models.CharField(max_length=300, blank=True)
    avail_start     = models.CharField(max_length=10, blank=True)
    avail_end       = models.CharField(max_length=10, blank=True)
    future_dates    = models.TextField(blank=True, default='[]')
    created_at      = models.DateTimeField(auto_now_add=True)

    @property
    def age(self):
        today = date.today()
        b = self.birthdate
        return today.year - b.year - ((today.month, today.day) < (b.month, b.day))

    def __str__(self):
        return f"{self.first_name} {self.last_name} (age {self.age})"

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Volunteer Signup'


class BusinessSignup(models.Model):
    BUSINESS_TYPES = [
        ('restaurant', 'Restaurant'),
        ('cafe',       'Café / Coffee Shop'),
        ('bakery',     'Bakery'),
        ('catering',   'Catering Company'),
        ('grocery',    'Grocery / Market'),
        ('other',      'Other'),
    ]
    business_name  = models.CharField(max_length=200)
    contact_name   = models.CharField(max_length=200)
    email          = models.EmailField()
    phone          = models.CharField(max_length=20)
    business_type  = models.CharField(max_length=50, choices=BUSINESS_TYPES, default='restaurant')
    street_address = models.CharField(max_length=300)
    city           = models.CharField(max_length=100)
    state          = models.CharField(max_length=100)
    zip_code       = models.CharField(max_length=20)
    frequency      = models.CharField(max_length=200, blank=True)
    food_types     = models.TextField(blank=True)
    message        = models.TextField(blank=True)
    created_at     = models.DateTimeField(auto_now_add=True)

    @property
    def full_address(self):
        return f"{self.street_address}, {self.city}, {self.state} {self.zip_code}"

    def __str__(self):
        return f"{self.business_name} — {self.contact_name}"

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Business Partner Signup'


class PodcastEpisode(models.Model):
    EPISODE_TYPES = [
        ('video',   'Video Interview'),
        ('written', 'Written Interview'),
        ('audio',   'Audio / Podcast'),
    ]
    title          = models.CharField(max_length=300)
    guest_name     = models.CharField(max_length=200)
    guest_title    = models.CharField(max_length=300, blank=True)
    episode_type   = models.CharField(max_length=20, choices=EPISODE_TYPES, default='video')
    description    = models.TextField()
    content        = models.TextField(blank=True)
    youtube_url    = models.URLField(blank=True)
    spotify_url    = models.URLField(blank=True)
    thumbnail      = models.ImageField(upload_to='podcast/', blank=True, null=True)
    published_date = models.DateField()
    is_featured    = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.title} — {self.guest_name}"

    class Meta:
        ordering = ['-published_date']
        verbose_name = 'Podcast Episode'

    def get_youtube_embed(self):
        if 'watch?v=' in self.youtube_url:
            vid = self.youtube_url.split('watch?v=')[-1].split('&')[0]
            return f"https://www.youtube.com/embed/{vid}"
        if 'youtu.be/' in self.youtube_url:
            vid = self.youtube_url.split('youtu.be/')[-1].split('?')[0]
            return f"https://www.youtube.com/embed/{vid}"
        return self.youtube_url


class Testimonial(models.Model):
    name       = models.CharField(max_length=200)
    role       = models.CharField(max_length=200)
    quote      = models.TextField()
    is_active  = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} — {self.role}"

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Testimonial'


class DonationRecord(models.Model):
    METHOD_CHOICES = [
        ('stripe', 'Stripe'),
        ('zelle',  'Zelle'),
        ('check',  'Check'),
        ('other',  'Other'),
    ]
    donor_name  = models.CharField(max_length=200, blank=True)
    donor_email = models.EmailField(blank=True)
    amount      = models.DecimalField(max_digits=10, decimal_places=2)
    method      = models.CharField(max_length=20, choices=METHOD_CHOICES)
    note        = models.TextField(blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"${self.amount} via {self.method} from {self.donor_name or 'Anonymous'}"

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Donation Record'
