from decimal import Decimal
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.core.exceptions import ValidationError
from accounts.models import Participant, Organizer
from events.models import Organization, FoodAndBeveragePost, ConversationHallPost, FunAndActivitiesPost
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.urls import reverse


class Order(models.Model):
    participant = models.ForeignKey('accounts.Participant', on_delete=models.CASCADE)
    post = models.ForeignKey('events.FoodAndBeveragePost', null=True, blank=True, on_delete=models.SET_NULL)
    conversation_hall_post = models.ForeignKey('events.ConversationHallPost', null=True, blank=True, on_delete=models.SET_NULL)
    activity_post = models.ForeignKey('events.FunAndActivitiesPost', null=True, blank=True, on_delete=models.SET_NULL)
    quantity = models.IntegerField(null=True, blank=True)  # for food and beverage
    duration = models.DurationField(null=True, blank=True)  # for hall and activity bookings
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=[('Pending', 'Pending'), ('Accepted', 'Accepted'), ('Paid', 'Paid'), ('Cancelled', 'Cancelled')], default='Pending')
    order_date = models.DateTimeField(default=timezone.now)
    payment_status = models.BooleanField(default=False)

    def clean(self):
        """Custom validation for the fields based on the type of post."""
        if self.post:
            if self.quantity is None or self.quantity <= 0:
                raise ValidationError(_("Quantity must be a positive integer for food and beverage orders."))
        if self.conversation_hall_post or self.activity_post:
            if self.duration is None or self.duration.total_seconds() <= 0:
                raise ValidationError(_("Duration must be specified and greater than zero for hall or activity bookings."))

    def calculate_total_price(self):
        """Calculates the total price based on quantity, duration, or activity."""
        if self.post:
            return self.post.price * self.quantity
        if self.conversation_hall_post:
            # Assuming duration is in hours, calculate price for the hall booking
            return self.conversation_hall_post.price_per_hour * self.duration.total_seconds() / 3600
        if self.activity_post:
            return self.activity_post.price * self.duration.total_seconds() / 3600
        return Decimal(0)

    def save(self, *args, **kwargs):
        self.clean()  # Call clean method to validate fields
        self.total_price = self.calculate_total_price()
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('order_history')

    def __str__(self):
        return f"Order #{self.pk} by {self.participant.user.username} - {self.status}"

    def cancel(self):
        """Cancel the order and update status."""
        self.status = 'Cancelled'
        self.save()

class Payment(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment')
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=50, choices=(('card', 'Card'), ('cash', 'Cash')))
    is_full_payment = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)  # Added field for created timestamp

    def clean(self):
        """Validate the payment amount to ensure it does not exceed the order total."""
        if self.amount_paid > self.order.total_price:
            raise ValidationError(_("Amount paid cannot exceed the total price of the order."))

    def save(self, *args, **kwargs):
        self.clean()  # Validate payment details before saving
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Payment for Order #{self.order.pk}"

class Notification(models.Model):
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    order = models.ForeignKey(  # Added optional ForeignKey to Order
        'Order',
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name='notifications'
    )
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def mark_as_read(self):
        """Mark notification as read."""
        self.is_read = True
        self.save()

    def __str__(self):
        return f"Notification for {self.recipient.username} - {self.message[:50]}..."
