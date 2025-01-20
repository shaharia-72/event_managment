from datetime import datetime
from urllib import request
from django.views import View
from django.views.generic import ListView, DetailView, CreateView
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.core.mail import send_mail
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from .models import Event, Invitation
from .forms import EventForm, InvitationForm, CSVInvitationForm
import csv
from io import TextIOWrapper
from django.utils import timezone
from django.core.mail import send_mail
from django.db import IntegrityError
from django.contrib import messages
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO


# List View for Events
class EventListView(ListView):
    """Displays a list of events with filters applied."""
    model = Event
    template_name = 'index.html'
    context_object_name = 'events'
    paginate_by = 9  # Show 9 events per page

    def get_queryset(self):
    # Start with public events for everyone
        queryset = Event.objects.filter(visibility='public')

        # Check if the user is logged in
        if self.request.user.is_authenticated:
            # Find private events where the user is invited
            invited_events = Event.objects.filter(
                visibility='private',
                invitations__email=self.request.user.email  # Check email in invitations
            )

            # If the user has invitations, include both public and invited private events
            if invited_events.exists():  # Only add private events if invitations exist
                queryset = queryset | invited_events  # Combine public and invited private events

        # Apply additional filters based on query parameters
        price = self.request.GET.get('price')
        date = self.request.GET.get('date')

        # Filter by price (free/paid)
        if price == 'free':
            queryset = queryset.filter(ticket_price__isnull=True)
        elif price == 'paid':
            queryset = queryset.filter(ticket_price__gt=0)

        # Filter by date (upcoming events)
        if date == 'upcoming':
            queryset = queryset.filter(event_date__gte=timezone.now())

        # Remove duplicates and sort events by date
        return queryset.distinct().order_by('-event_date')



class MyEventListView(ListView):
    """Displays a list of events created by the logged-in user (My Events)."""
    model = Event
    template_name = 'my_events.html'
    context_object_name = 'events'
    paginate_by = 9  # Show 9 events per page

    def get_queryset(self):
        # Filter events created by the current user
        return Event.objects.filter(created_by=self.request.user).order_by('-event_date')

# Detail View for Event
class EventDetailView(DetailView):
    """Displays details of a specific event."""
    model = Event
    template_name = 'event_detail.html'


# Create View for Event
@method_decorator(login_required, name='dispatch')
class EventCreateView(CreateView):
    """Handles event creation."""
    model = Event
    form_class = EventForm
    template_name = 'event_form.html'
    success_url = reverse_lazy('event_list')

    def form_valid(self, form):
        """Set creator before saving the form."""
        event = form.save(commit=False)
        event.created_by = self.request.user
        event.save()
        messages.success(self.request, "Event created successfully!")
        return super().form_valid(form)

    def form_invalid(self, form):
        """Handle invalid form submission."""
        messages.error(self.request, "Please correct the errors below.")
        return super().form_invalid(form)


# Handle Event Invitations
@method_decorator(login_required, name='dispatch')
class EventInviteView(View):
    """Handles manual and CSV invitations for events."""

    def get(self, request, pk):
        """Display invitation forms."""
        event = get_object_or_404(Event, pk=pk)
        invite_form = InvitationForm()
        csv_form = CSVInvitationForm()
        return render(request, 'event_invite.html', {
            'event': event,
            'invite_form': invite_form,
            'csv_form': csv_form
        })

    def post(self, request, pk):
        """Process invitations."""
        event = get_object_or_404(Event, pk=pk)

        # Handle Manual Invitations
        if 'manual_invite' in request.POST:
            invite_form = InvitationForm(request.POST)
            if invite_form.is_valid():
                email = invite_form.cleaned_data['email']
                name = invite_form.cleaned_data['name']
                if self.send_invitation(request, event, email, name):
                    messages.success(request, f"Invitation sent to {email}.")
                return redirect('event_detail', pk=event.pk)

        # Handle CSV Invitations
        if 'csv_invite' in request.POST:
            csv_form = CSVInvitationForm(request.POST, request.FILES)
            if csv_form.is_valid():
                csv_file = TextIOWrapper(request.FILES['csv_file'].file, encoding='utf-8')
                reader = csv.reader(csv_file)
                errors = []
                success_count = 0

                for row in reader:
                    try:
                        name, email = row
                        if self.send_invitation(request, event, email, name):
                            success_count += 1
                    except Exception as e:
                        errors.append(str(e))

                if success_count > 0:
                    messages.success(request, f"{success_count} invitations sent successfully!")
                if errors:
                    messages.warning(request, f"Some errors occurred: {errors}")
                return redirect('event_detail', pk=event.pk)

        # Invalid forms, render the page again
        invite_form = InvitationForm()
        csv_form = CSVInvitationForm()
        return render(request, 'event_invite.html', {
            'event': event,
            'invite_form': invite_form,
            'csv_form': csv_form
        })

    @staticmethod
    def send_invitation(request, event, email, name):
        """Helper function to send email invitations."""
        try:
            # Attempt to create the invitation
            Invitation.objects.create(event=event, email=email, name=name)
            send_mail(
                subject=f"Invitation to {event.title}",
                message=f"Dear {name},\n\nYou are invited to {event.title}.\n\nThank you!",
                from_email='noreply@example.com',
                recipient_list=[email],
            )
            return True
        except IntegrityError:
            messages.warning(request, f"{email} has already been invited to this event.")
        except Exception as e:
            messages.error(request, f"Failed to send invitation to {email}. Error: {str(e)}")
        return False
    






class ConfirmedParticipantsPDFView(View):
    """Generates a PDF of confirmed participants for an event."""
    def get(self, request, pk):
        event = get_object_or_404(Event, pk=pk)
        participants = event.participants.all()

        # PDF Generation
        buffer = BytesIO()
        pdf = canvas.Canvas(buffer, pagesize=letter)
        pdf.setTitle(f"Confirmed Participants for {event.title}")

        # Header
        pdf.setFont("Helvetica-Bold", 16)
        pdf.drawString(50, 750, f"Confirmed Participants for {event.title}")

        # Participant List
        pdf.setFont("Helvetica", 12)
        y_position = 720
        for participant in participants:
            pdf.drawString(50, y_position, f"{participant.get_full_name()} ({participant.email})")
            y_position -= 20
            if y_position < 50:  # New page if needed
                pdf.showPage()
                pdf.setFont("Helvetica", 12)
                y_position = 750

        pdf.save()
        buffer.seek(0)

        # Return as PDF response
        response = HttpResponse(buffer, content_type="application/pdf")
        response['Content-Disposition'] = f'attachment; filename="confirmed_participants_{event.pk}.pdf"'
        return response


class InvitationsListPDFView(View):
    """Generates a PDF of the invitations list for an event."""
    def get(self, request, pk):
        event = get_object_or_404(Event, pk=pk)
        invitations = event.invitations.all()

        # PDF Generation
        buffer = BytesIO()
        pdf = canvas.Canvas(buffer, pagesize=letter)
        pdf.setTitle(f"Invitations List for {event.title}")

        # Header
        pdf.setFont("Helvetica-Bold", 16)
        pdf.drawString(50, 750, f"Invitations List for {event.title}")

        # Invitations List
        pdf.setFont("Helvetica", 12)
        y_position = 720
        for invitation in invitations:
            pdf.drawString(50, y_position, f"{invitation.name} ({invitation.email}) - Accepted: {invitation.accepted}")
            y_position -= 20
            if y_position < 50:  # New page if needed
                pdf.showPage()
                pdf.setFont("Helvetica", 12)
                y_position = 750

        pdf.save()
        buffer.seek(0)

        # Return as PDF response
        response = HttpResponse(buffer, content_type="application/pdf")
        response['Content-Disposition'] = f'attachment; filename="invitations_list_{event.pk}.pdf"'
        return response