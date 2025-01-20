from django.db.models import Q
import logging
import json
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.views import View
from django.views.generic.edit import FormView, UpdateView
from django.views.generic import TemplateView
from django.contrib import messages
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from jsonschema import ValidationError
from .forms import (
    ParticipantRegistrationForm, OrganizerRegistrationForm,
    ParticipantProfileUpdateForm, OrganizerProfileUpdateForm
)
from .models import CustomUser, Participant, Organizer

# Logger setup
logger = logging.getLogger(__name__)

# Combined Registration View
from django.contrib import messages
from django.http import HttpResponseRedirect




class RegisterView(TemplateView):
    template_name = 'register.html'

    def get_context_data(self, **kwargs):
        # Pass form instances from kwargs or create new ones if not present
        context = super().get_context_data(**kwargs)
        context['participant_form'] = kwargs.get('participant_form', ParticipantRegistrationForm())
        context['organizer_form'] = kwargs.get('organizer_form', OrganizerRegistrationForm())
        return context

    def post(self, request, *args, **kwargs):
        # Instantiate both forms with POST data
        participant_form = ParticipantRegistrationForm(request.POST, request.FILES)
        organizer_form = OrganizerRegistrationForm(request.POST, request.FILES)

        if 'participant_button' in request.POST:
            if participant_form.is_valid():
                return self.handle_participant_registration(participant_form)
            else:
                messages.error(request, "Please correct the errors in the Participant form.")
                return self.render_to_response(self.get_context_data(participant_form=participant_form))

        elif 'organizer_button' in request.POST:
            if organizer_form.is_valid():
                return self.handle_organizer_registration(organizer_form)
            else:
                messages.error(request, "Please correct the errors in the Organizer form.")
                return self.render_to_response(self.get_context_data(organizer_form=organizer_form))

        return self.render_to_response(self.get_context_data())

    def handle_participant_registration(self, form):
        try:
            user = form.save(commit=False)
            user.is_participant = True
            user.save()
            Participant.objects.create(
                user=user,
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                email=form.cleaned_data['email'],
                profile_image=form.cleaned_data.get('profile_image')
            )
            login(self.request, user)
            messages.success(self.request, "Participant registered successfully!")
            return redirect('home')
        except Exception as e:
            logger.error(f"Participant registration error: {e}")
            messages.error(self.request, "An error occurred during registration.")
            return self.render_to_response(self.get_context_data(participant_form=form))

    def handle_organizer_registration(self, form):
        try:
            user = form.save(commit=False)
            user.is_organizer = True
            user.save()
            Organizer.objects.create(
                user=user,
                organization_name=form.cleaned_data['organization_name'],
                location=form.cleaned_data['location'],
                description=form.cleaned_data['description'],
                organization_image=form.cleaned_data.get('organization_image'),
                website=form.cleaned_data.get('website')
            )
            login(self.request, user)
            messages.success(self.request, "Organizer registered successfully!")
            return redirect('home')
        except Exception as e:
            logger.error(f"Organizer registration error: {e}")
            messages.error(self.request, "An error occurred during registration.")
            return self.render_to_response(self.get_context_data(organizer_form=form))






# Custom Login View
class CustomLoginView(LoginView):
    template_name = 'login.html'

    def form_invalid(self, form):
        # If form is invalid, display an error message
        messages.error(self.request, "Invalid login credentials. Please try again.")
        return self.render_to_response(self.get_context_data(form=form))

    def get_success_url(self):
        user = self.request.user
        if user.is_organizer:
            return reverse_lazy('home')  # Redirect to organizer home
        elif user.is_participant:
            return reverse_lazy('home')  # Redirect to participant home
        else:
            return reverse_lazy('guest_home')  # Redirect to guest home

# Logout View
@login_required
def logout_view(request):
    logout(request)
    logger.info(f"User {request.user.username} logged out successfully.")
    return redirect('home')

# Participant Profile View
class ParticipantProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'participant_profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            participant = Participant.objects.get(user=self.request.user)
            context['profile'] = participant
            context['active_page'] = 'profile'
        except Participant.DoesNotExist:
            logger.error(f"Participant profile not found for user {self.request.user.username}")
            context['error'] = "Profile not found"
        return context

# Organizer Profile View
class OrganizerProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'organizer_profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            organizer = Organizer.objects.get(user=self.request.user)
            context['profile'] = organizer
            context['active_page'] = 'profile'
        except Organizer.DoesNotExist:
            logger.error(f"Organizer profile not found for user {self.request.user.username}")
            context['error'] = "Profile not found"
        return context

# Update Participant Profile
class ParticipantProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = Participant
    form_class = ParticipantProfileUpdateForm
    template_name = 'update_participant_profile.html'

    def get_object(self, queryset=None):
        return Participant.objects.get(user=self.request.user)

    def form_valid(self, form):
        participant = form.save(commit=False)
        participant.user.email = form.cleaned_data['email']
        participant.user.save()
        participant.save()
        logger.info(f"Participant profile updated for {self.request.user.username}")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('participant_profile')

# Update Organizer Profile
class OrganizerProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = Organizer
    form_class = OrganizerProfileUpdateForm
    template_name = 'update_organizer_profile.html'

    def get_object(self, queryset=None):
        return Organizer.objects.get(user=self.request.user)

    def form_valid(self, form):
        # Check if email already exists for another user
        email = form.cleaned_data.get('email')
        if self.model.objects.filter(Q(user__email=email) & ~Q(user=self.request.user)).exists():
            form.add_error('email', ValidationError("This email is already in use."))
            messages.error(self.request, "This email is already in use.")
            return self.form_invalid(form)
        
        # Save changes
        organizer = form.save(commit=False)
        organizer.user.email = email
        organizer.user.save()
        organizer.save()
        
        # Success feedback
        messages.success(self.request, "Profile updated successfully!")
        logger.info(f"Organizer profile updated for {self.request.user.username}")
        return super().form_valid(form)

    def form_invalid(self, form):
        # Add an error message
        messages.error(self.request, "There was an error updating your profile. Please check the form.")
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse_lazy('organizer_profile')

# Change Password View
@login_required
def password_change(request):
    if request.method == 'POST':
        password_change_form = PasswordChangeForm(request.user, data=request.POST)
        if password_change_form.is_valid():
            user = password_change_form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Password changed successfully.')
            logger.info(f"Password changed for user {request.user.username}")
            if request.user.is_organizer:
                return redirect('organizer_profile')
            elif request.user.is_participant:
                return redirect('participant_profile')
            else:
                return redirect('home')
        else:
            messages.error(request, 'Please fix the errors below.')
    else:
        password_change_form = PasswordChangeForm(request.user)

    return render(request, 'password_change.html', {'form': password_change_form})

# Deposit Amount View
class DepositAmountView(LoginRequiredMixin, View):
    @method_decorator(csrf_exempt)
    def post(self, request, *args, **kwargs):
        try:
            # Check if the user has a participant or organizer profile
            if not hasattr(request.user, 'participant') and not hasattr(request.user, 'organizer'):
                logger.error(f"User {request.user.username} is neither a participant nor an organizer.")
                return JsonResponse({'error': 'Only participants or organizers can make deposits.'}, status=403)

            data = json.loads(request.body)
            amount = float(data.get('amount', 0))

            # Validate amount
            if amount <= 0:
                logger.error(f"Invalid deposit amount: {amount}")
                return JsonResponse({'error': 'Deposit amount must be greater than zero.'}, status=400)

            # Check if user is a participant or an organizer and handle the deposit accordingly
            if hasattr(request.user, 'participant'):
                user_profile = request.user.participant
                user_type = 'participant'
            else:
                user_profile = request.user.organizer
                user_type = 'organizer'

            # Update the balance for the participant or organizer
            user_profile.amount += amount
            user_profile.save()

            logger.info(f"Deposit successful for {user_type} {request.user.username}. New balance: {user_profile.amount}")
            return JsonResponse({'success': True, 'new_balance': user_profile.amount})

        except ValueError:
            logger.error(f"Invalid amount format: {data.get('amount')}")
            return JsonResponse({'error': 'Invalid amount format.'}, status=400)
        except Exception as e:
            logger.exception(f"Unexpected error in DepositAmountView: {str(e)}")
            return JsonResponse({'error': 'An unexpected error occurred. Please try again.'}, status=500)