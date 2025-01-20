from django.urls import path
from .views import EventListView, EventDetailView, EventCreateView, EventInviteView, ConfirmedParticipantsPDFView, InvitationsListPDFView, MyEventListView

urlpatterns = [
    path('', EventListView.as_view(), name='event_list'),
    path('my-events/', MyEventListView.as_view(), name='my_event_list'),
    path('event/create/', EventCreateView.as_view(), name='event_create'),
    # path('event/<int:pk>/edit/', EventUpdateView.as_view(), name='event_edit'),
    path('event/<int:pk>/', EventDetailView.as_view(), name='event_detail'),
    path('event/<int:pk>/invite/', EventInviteView.as_view(), name='event_invite'),
    path('event/<int:pk>/confirmed-participants-pdf/', ConfirmedParticipantsPDFView.as_view(), name='confirmed_participants_pdf'),
    path('event/<int:pk>/invitations-list-pdf/', InvitationsListPDFView.as_view(), name='invitations_list_pdf'),
]
