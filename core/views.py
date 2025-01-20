from django.views.generic import ListView
from django.shortcuts import render
from createevent.models import Event  # Import Event model

# Updated Home Page View
class HomePageView(ListView):
    """Home page displaying all public events."""
    model = Event
    template_name = 'index.html'  # Use your homepage template
    context_object_name = 'events'  # Access events in template as 'events'

    def get_queryset(self):
        """Filter only public events ordered by event date."""
        return Event.objects.filter(visibility='public').order_by('-event_date')
