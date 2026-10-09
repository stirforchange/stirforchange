# This goes inside models.py — StaffProfile model
"""
from django.contrib.auth.models import User

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
        return f"{self.user.username} ({self.role})"
"""
