from django.db import models
from django.conf import settings
from django.utils.text import slugify
from accounts.models import CustomUser
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext_lazy as _


class Organization(models.Model):
    organizer = models.OneToOneField('accounts.Organizer', on_delete=models.CASCADE, related_name='organization')
    name = models.CharField(max_length=255)
    is_active_food_and_beverage = models.BooleanField(default=False)
    is_active_conversation_hall = models.BooleanField(default=False)
    is_active_fun_and_activities = models.BooleanField(default=False)

    def __str__(self):
        active_features = []
        if self.is_active_food_and_beverage:
            active_features.append("Food & Beverage")
        if self.is_active_conversation_hall:
            active_features.append("Conversation Hall")
        if self.is_active_fun_and_activities:
            active_features.append("Fun & Activities")
        
        active_str = ", ".join(active_features) if active_features else "No active features"
        return f"{self.organizer.organization_name} - Active Features: {active_str}"


# Admin approval request model
class AdminApprovalRequest(models.Model):
    class StatusChoices(models.TextChoices):
        PENDING = 'Pending', _('Pending')
        APPROVED = 'Approved', _('Approved')
        REMOVED = 'Removed', _('Removed')

    organization = models.ForeignKey(
        'Organization', 
        on_delete=models.CASCADE, 
        related_name='approval_requests'
    )
    tag = models.CharField(
        max_length=50,
        choices=(
            ('food_and_beverage', 'Food and Beverage'),
            ('conversation_hall', 'Conversation Hall'),
            ('fun_and_activities', 'Fun and Activities'),
        )
    )
    is_approved = models.BooleanField(default=False)  # For quick status checks
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.PENDING,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('organization', 'tag')
        ordering = ['-updated_at']
        verbose_name = 'Admin Approval Request'
        verbose_name_plural = 'Admin Approval Requests'

    def __str__(self):
        return f"{self.organization.name} - {self.get_tag_display()} ({self.status})"

    def set_pending(self):
        """Resets the approval request to pending status."""
        self.is_approved = False
        self.status = self.StatusChoices.PENDING
        self.save()

    def approve(self):
        """Approves the request."""
        self.is_approved = True
        self.status = self.StatusChoices.APPROVED
        self.save()

    def remove(self):
        """Removes the approval (revokes admin approval)."""
        self.is_approved = False
        self.status = self.StatusChoices.REMOVED
        self.save()




class FoodCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class ConversationHallCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class FunAndActivitiesCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class FoodAndBeveragePost(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    food_category = models.ForeignKey(FoodCategory, on_delete=models.SET_NULL, null=True, related_name='food_posts')
    image = models.ImageField(upload_to='food_and_beverage/')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField()

    def __str__(self):
        return self.title
    
    def get_post_type(self):
        return "food_and_beverage"


class ConversationHallPost(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    hall_category = models.ForeignKey(ConversationHallCategory, on_delete=models.SET_NULL, null=True, related_name='hall_posts')
    image = models.ImageField(upload_to='conversation_hall/')
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.title
    
    def get_post_type(self):
        return "conversation_hall"


class FunAndActivitiesPost(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    activity_category = models.ForeignKey(FunAndActivitiesCategory, on_delete=models.SET_NULL, null=True, related_name='activity_posts')
    image = models.ImageField(upload_to='fun_and_activities/')
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.title
    
    def get_post_type(self):
        return "fun_and_activities"


class PostFeedback(models.Model):
    # Generic Foreign Key to allow multiple models (Food, Hall, Activities)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)  # Model type (Food, Hall, Activity)
    object_id = models.PositiveIntegerField()  # ID of the instance
    post = GenericForeignKey('content_type', 'object_id')  # Combine the two above

    participant = models.ForeignKey(
        'accounts.Participant',
        on_delete=models.CASCADE,
        related_name='feedbacks'
    )
    feedback_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback by {self.participant.user.username} on {self.post}"