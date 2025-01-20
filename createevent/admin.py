from django.contrib import admin
from .models import EventCategory, Event, Invitation, ParticipantEvent


@admin.register(EventCategory)
class EventCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')  # Show name and slug in the list
    prepopulated_fields = {"slug": ("name",)}  # Auto-generate slug from name
    search_fields = ('name',)  # Enable search by category name
    ordering = ('name',)  # Default ordering by name


class InvitationInline(admin.TabularInline):
    """Inline model for managing invitations within events."""
    model = Invitation
    extra = 1  # Show one empty form by default
    fields = ('email', 'name', 'accepted')  # Display these fields
    readonly_fields = ('invited_at',)  # Mark 'invited_at' as read-only
    can_delete = True


class ParticipantEventInline(admin.TabularInline):
    """Inline model for managing participants within events."""
    model = ParticipantEvent
    extra = 0  # No extra empty forms by default
    readonly_fields = ('registered_at',)


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'category', 'created_by', 'event_date', 'registration_start', 
        'registration_end', 'visibility', 'remaining_slots'
    )
    list_filter = ('visibility', 'category', 'event_date')  # Add filters
    search_fields = ('title', 'description', 'category__name')  # Enable search
    date_hierarchy = 'event_date'  # Navigation by event date
    readonly_fields = ('remaining_slots',)  # Display available slots as read-only
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'category', 'description', 'image', 'visibility')
        }),
        ('Schedule', {
            'fields': ('registration_start', 'registration_end', 'event_date')
        }),
        ('Capacity and Pricing', {
            'fields': ('ticket_price', 'max_participants')
        }),
        ('Creator Details', {
            'fields': ('created_by',)
        }),
    )
    inlines = [InvitationInline, ParticipantEventInline]  # Add inline forms

    def remaining_slots(self, obj):
        """Show available slots."""
        return obj.remaining_slots()
    remaining_slots.short_description = 'Available Slots'


@admin.register(Invitation)
class InvitationAdmin(admin.ModelAdmin):
    list_display = ('email', 'event', 'invited_at', 'accepted')  # Display details
    list_filter = ('accepted', 'event')  # Filters
    search_fields = ('email', 'event__title')  # Search support


@admin.register(ParticipantEvent)
class ParticipantEventAdmin(admin.ModelAdmin):
    list_display = ('participant', 'event', 'registered_at')  # Show participant details
    list_filter = ('event',)  # Add filters
    search_fields = ('participant__username', 'event__title')  # Search by user or event
    date_hierarchy = 'registered_at'  # Date-based navigation
