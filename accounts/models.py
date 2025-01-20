from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
# from .models import Organizer

class CustomUser(AbstractUser):
    is_participant = models.BooleanField(default=False)
    is_organizer = models.BooleanField(default=False)

    # def __str__(self):
        # return f"{self.is_participant} {self.is_organizer}"

class Participant(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.EmailField(unique=True)
    amount = models.FloatField(default=0.0)
    profile_image = models.ImageField(upload_to='participants/images/',blank=True,null=True)
    organization = models.ForeignKey('Organizer', on_delete=models.CASCADE, related_name='participants', null=True, blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def get_interested_events(self):
        return self.events.filter(participation__status='pending')

class Organizer(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    organization_name = models.CharField(max_length=100, unique=True)
    location = models.CharField(max_length=255)  # Full address
    description = models.TextField(max_length=1000)
    amount = models.FloatField(default=0.0)
    organization_image = models.ImageField(upload_to='organizers/images/', blank=True, null=True)
    website = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.organization_name

    def clean(self):
        # Validate uniqueness of organization name
        if Organizer.objects.exclude(pk=self.pk).filter(organization_name=self.organization_name).exists():
            raise ValidationError("An organization with this name already exists.")