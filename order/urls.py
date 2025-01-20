from django.urls import path
from .views import DashboardView, OrderView, PaymentView, generate_order_pdf, ParticipantDashboardView, OrderDashboardView, OrderListView

urlpatterns = [
    # Participant dashboard URL
    path('participant/dashboard/', ParticipantDashboardView.as_view(), name='participant_dashboard'),

    # Main dashboard URL (for both participant and organizer)
    path('', DashboardView.as_view(), name='dashboard'),

    # Order placement URL with dynamic post_id and post_type
    path('order/<str:post_type>/<int:post_id>/', OrderView.as_view(), name='place_order'),
    #  path('order/<str:post_type>/<int:post_id>/', place_order, name='place_order'),

    # Payment URL, where the participant can make the payment for a specific order
    path('payment/<int:order_id>/', PaymentView.as_view(), name='payment'),

    # Generate PDF for the order (both participant and organizer can download the PDF)
    path('order/<int:order_id>/pdf/', generate_order_pdf, name='generate_order_pdf'),

    # Order dashboard for the organizer (view all orders)
    path('dashboard/', OrderDashboardView.as_view(), name='order_dashboard'),
    path('orders/', OrderListView.as_view(), name='order_list'),
]
