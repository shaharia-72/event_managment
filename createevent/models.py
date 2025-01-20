from django.db import models
from django.shortcuts import get_object_or_404
from django.utils.text import slugify
from django.utils.timezone import now
from django.views import View
from accounts.models import CustomUser  # Use the base user model
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class EventCategory(models.Model):
    """Event categories created by admin."""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)

    def save(self, *args, **kwargs):
        # Generate slug whenever 'name' changes or slug is blank
        if not self.slug or slugify(self.name) != self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Event(models.Model):
    """Model for Events created by any registered user."""
    VISIBILITY_CHOICES = [
        ('public', 'Public'),
        ('private', 'Private'),
    ]

    created_by = models.ForeignKey(
        CustomUser,  # Allow any user to create events
        on_delete=models.CASCADE,
        related_name="created_events"
    )
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to="events/images/", blank=True, null=True)
    category = models.ForeignKey(EventCategory, on_delete=models.SET_NULL, null=True, related_name="events")
    description = models.TextField()
    registration_start = models.DateTimeField()
    registration_end = models.DateTimeField()
    event_date = models.DateTimeField()
    ticket_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    max_participants = models.PositiveIntegerField()
    visibility = models.CharField(max_length=10, choices=VISIBILITY_CHOICES, default='public')

    participants = models.ManyToManyField(CustomUser, through="ParticipantEvent", related_name="joined_events")

    def clean(self):
        """Validate date constraints."""
        if self.registration_start >= self.registration_end:
            raise ValidationError("Registration start must be before registration end.")
        if self.registration_end >= self.event_date:
            raise ValidationError("Registration end must be before the event date.")

    def is_registration_open(self):
        """Check if registration is open."""
        return self.registration_start <= now() <= self.registration_end

    def remaining_slots(self):
        """Check available slots."""
        return self.max_participants - self.participants.count()

    def __str__(self):
        return f"{self.title} ({self.get_visibility_display()})"


class Invitation(models.Model):
    """Model for event invitations."""
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="invitations")
    email = models.EmailField()
    name = models.CharField(max_length=100, blank=True, null=True)
    invited_at = models.DateTimeField(auto_now_add=True)
    accepted = models.BooleanField(default=False)

    class Meta:
        unique_together = ('event', 'email')

    def __str__(self):
        return f"Invitation to {self.email} for {self.event.title}"


class ParticipantEvent(models.Model):
    """Tracks participants registered for events."""
    participant = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE, 
        related_name="event_participations"
    )
    event = models.ForeignKey(
        Event, 
        on_delete=models.CASCADE, 
        related_name="participant_events"  # Changed related_name to avoid conflict
    )
    registered_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.participant.username} registered for {self.event.title}"
