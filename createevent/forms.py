from django import forms
from .models import Event, Invitation
from django.core.exceptions import ValidationError
from django.utils.timezone import now
import csv
from io import TextIOWrapper


class EventForm(forms.ModelForm):
    """Form to create or update events."""
    class Meta:
        model = Event
        fields = [
            'title', 'image', 'category', 'description', 'registration_start',
            'registration_end', 'event_date', 'ticket_price', 'max_participants', 'visibility'
        ]
        widgets = {
            'registration_start': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'registration_end': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'event_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def clean(self):
        """Custom validation for date and time."""
        cleaned_data = super().clean()
        reg_start = cleaned_data.get('registration_start')
        reg_end = cleaned_data.get('registration_end')
        event_date = cleaned_data.get('event_date')

        if reg_start and reg_start < now():
            raise ValidationError("Registration start time cannot be in the past.")
        if reg_start and reg_end and reg_start >= reg_end:
            raise ValidationError("Registration start must be before registration end.")
        if reg_end and event_date and reg_end >= event_date:
            raise ValidationError("Registration end must be before the event date.")
        return cleaned_data


class InvitationForm(forms.Form):
    """Form to send invitations manually."""
    email = forms.EmailField()
    name = forms.CharField(max_length=100, required=False)


class CSVInvitationForm(forms.Form):
    """Form to upload invitations via CSV."""
    csv_file = forms.FileField()

    def clean_csv_file(self):
        """Validate the uploaded CSV file."""
        csv_file = self.cleaned_data['csv_file']
        if not csv_file.name.endswith('.csv'):
            raise ValidationError('File must be a CSV.')

        # Validate CSV format
        try:
            decoded_file = TextIOWrapper(csv_file.file, encoding='utf-8')
            reader = csv.reader(decoded_file)
            for row in reader:
                if len(row) != 2:
                    raise ValidationError('CSV must have exactly two columns: Name and Email.')
        except Exception:
            raise ValidationError('Invalid CSV file format.')
        return csv_file
