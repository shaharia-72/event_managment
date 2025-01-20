from django import forms
from datetime import timedelta
from .models import Order, Payment

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['quantity', 'duration']  # The fields vary depending on the post type

    def __init__(self, *args, **kwargs):
        post_type = kwargs.pop('post_type', None)
        super().__init__(*args, **kwargs)
        if post_type == 'food_and_beverage':
            self.fields['duration'].widget = forms.HiddenInput()
            self.fields['quantity'].widget.attrs.update({'class': 'form-control'})
        elif post_type in ['conversation_hall', 'fun_and_activities']:
            self.fields['duration'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Duration in hours'})

    def clean_duration(self):
        """Ensure duration is not negative or zero"""
        duration = self.cleaned_data.get('duration')
        if duration:
            if isinstance(duration, timedelta):
                if duration.total_seconds() <= 0:
                    raise forms.ValidationError("Duration must be greater than 0 hours.")
            else:
                try:
                    duration = timedelta(hours=float(duration))
                    if duration.total_seconds() <= 0:
                        raise forms.ValidationError("Duration must be greater than 0 hours.")
                except ValueError:
                    raise forms.ValidationError("Invalid duration format.")
        return duration


class PaymentForm(forms.Form):
    amount = forms.DecimalField(max_digits=10, decimal_places=2)
    payment_method = forms.ChoiceField(choices=[('card', 'Card'), ('cash', 'Cash')])
    is_full_payment = forms.BooleanField(required=False, label="Pay Full Amount")

    def clean_amount(self):
        """Ensure the amount paid is valid based on the order amount"""
        amount = self.cleaned_data.get('amount')
        if amount <= 0:
            raise forms.ValidationError("Payment amount must be greater than zero.")
        return amount

    def clean(self):
        cleaned_data = super().clean()
        amount = cleaned_data.get('amount')
        is_full_payment = cleaned_data.get('is_full_payment')

        # You can tie is_full_payment to the logic of full or partial payment here
        if is_full_payment and amount:
            # Assuming you have access to the order object
            # Perform a check for matching full payment if needed
            pass
        return cleaned_data
