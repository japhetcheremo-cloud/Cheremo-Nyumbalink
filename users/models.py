from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    ROLE_TENANT = 'tenant'
    ROLE_LANDLORD = 'landlord'
    ROLE_AGENT = 'agent'
    ROLE_ADMIN = 'admin'
    
    ROLE_CHOICES = [
        (ROLE_TENANT, 'Tenant'),
        (ROLE_LANDLORD, 'Landlord'),
        (ROLE_AGENT, 'Property Agent'),
        (ROLE_ADMIN, 'Administrator'),
    ]
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_TENANT)
    phone = models.CharField(max_length=20, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    
    # Track document uploads for Landlord/Agent verification
    verification_document = models.FileField(upload_to='verification_docs/', blank=True, null=True)
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

