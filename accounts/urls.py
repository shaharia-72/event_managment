from django.urls import path
from .views import (
    RegisterView,  # Combined registration view
    CustomLoginView, logout_view, ParticipantProfileView, OrganizerProfileView, 
    ParticipantProfileUpdateView, OrganizerProfileUpdateView, DepositAmountView,
    # OrganizerHomeView, HomeView, GuestHomeView  # Added these views
)
from accounts import views

urlpatterns = [
    # Registration and Login/Logout paths
    path('register/', RegisterView.as_view(), name='register'),  # Combined registration view
    path('login/', CustomLoginView.as_view(), name='login'),  # Login view
    path('logout/', logout_view, name='logout'),  # Logout view
    
    # Profile views for participant and organizer
    path('participant/profile/', ParticipantProfileView.as_view(), name='participant_profile'),
    path('organizer/profile/', OrganizerProfileView.as_view(), name='organizer_profile'),
    
    # Profile update views for participant and organizer
    path('participant/profile/update/', ParticipantProfileUpdateView.as_view(), name='update_participant_profile'),
    path('organizer/profile/update/', OrganizerProfileUpdateView.as_view(), name='update_organizer_profile'),
    
    # Password change for organizers
    path('organizer/profile/password_change/', views.password_change, name='password_change'),
    
    # Deposit view for participants
    path('participant/deposit/', DepositAmountView.as_view(), name='deposit_amount'),
    path('organizer/deposit/', DepositAmountView.as_view(), name='deposit_amount'),

    # Home page views for organizer, participant, and guest
    # path('organizer/home/', OrganizerHomeView.as_view(), name='organizer_home'),
    # path('home/', HomeView.as_view(), name='home'),  # For participant
    # path('guest_home/', GuestHomeView.as_view(), name='guest_home'),  # For guests or unknown users
]
