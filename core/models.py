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


class VolunteerEvent(models.Model):
    title          = models.CharField(max_length=200)
    description    = models.TextField()
    date           = models.DateField()
    start_time     = models.TimeField()
    end_time       = models.TimeField()
    location       = models.CharField(max_length=300)
    max_volunteers = models.PositiveIntegerField(default=10)
    what_to_bring  = models.TextField(blank=True)
    food_type      = models.CharField(max_length=200, blank=True)
    is_active      = models.BooleanField(default=True)
    created_by     = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_events')
    created_at     = models.DateTimeField(auto_now_add=True)

    @property
    def spots_taken(self):
        return self.signups.count()

    @property
    def spots_left(self):
        return max(0, self.max_volunteers - self.spots_taken)

    @property
    def is_full(self):
        return self.spots_taken >= self.max_volunteers

    @property
    def capacity_percent(self):
        if self.max_volunteers == 0:
            return 100
        return min(100, int((self.spots_taken / self.max_volunteers) * 100))

    def __str__(self):
        return f"{self.title} - {self.date}"

    class Meta:
        ordering = ['date', 'start_time']
        verbose_name = 'Volunteer Event'


class VolunteerSignup(models.Model):
    event      = models.ForeignKey(VolunteerEvent, on_delete=models.CASCADE, related_name='signups')
    first_name = models.CharField(max_length=100)
    last_name  = models.CharField(max_length=100)
    email      = models.EmailField()
    phone      = models.CharField(max_length=20, blank=True)
    birthdate  = models.DateField()
    school     = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def age(self):
        today = date.today()
        b = self.birthdate
        return today.year - b.year - ((today.month, today.day) < (b.month, b.day))

    def __str__(self):
        return f"{self.first_name} {self.last_name} -> {self.event.title}"

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Volunteer Signup'
        unique_together = [['event', 'email']]


class BusinessSignup(models.Model):
    BUSINESS_TYPES = [
        ('restaurant', 'Restaurant'),
        ('cafe',       'Cafe / Coffee Shop'),
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
        return f"{self.business_name}"

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
        return f"{self.title}"

    class Meta:
        ordering = ['-published_date']
        verbose_name = 'Podcast Episode'

    def get_youtube_embed(self):
        url = self.youtube_url
        if not url:
            return ''
        if 'watch?v=' in url:
            vid = url.split('watch?v=')[-1].split('&')[0]
            return f"https://www.youtube.com/embed/{vid}"
        if 'youtu.be/' in url:
            vid = url.split('youtu.be/')[-1].split('?')[0]
            return f"https://www.youtube.com/embed/{vid}"
        if 'embed/' in url:
            return url
        return url


class Testimonial(models.Model):
    name       = models.CharField(max_length=200)
    role       = models.CharField(max_length=200)
    quote      = models.TextField()
    is_active  = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name}"

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
        return f"${self.amount} via {self.method}"

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Donation Record'
