from datetime import timezone
from django.contrib import messages
from django.forms import ValidationError
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import View
from django.http import JsonResponse, HttpResponse
from django.template.loader import render_to_string

from accounts.models import Participant
from .models import Order, Payment, Notification
from events.models import FoodAndBeveragePost, ConversationHallPost, FunAndActivitiesPost
from .forms import OrderForm, PaymentForm
from xhtml2pdf import pisa
from django.db.models import Q
from django.core.paginator import Paginator
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction
from django.views.generic import ListView


class DashboardView(View):
    def get(self, request):
        if not hasattr(request.user, 'participant'):
            return redirect('error_page')

        orders = Order.objects.filter(participant=request.user.participant).select_related('post', 'conversation_hall_post', 'activity_post')
        notifications = Notification.objects.filter(recipient=request.user)
        return render(request, 'dashboard.html', {'orders': orders, 'notifications': notifications})


class ParticipantDashboardView(View):
    template_name = 'participant_dashboard.html'

    def get(self, request):
        category = request.GET.get('category')
        min_price = request.GET.get('min_price')
        max_price = request.GET.get('max_price')
        search_query = request.GET.get('search')

        user = request.user
        organization = None

        if user.is_authenticated and user.is_participant:
            try:
                participant = user.participant
                organization = participant.organization
            except Participant.DoesNotExist:
                messages.error(request, "You are not associated with an organization.")
                return redirect('home')

        posts = self.get_filtered_posts(category, min_price, max_price, search_query, organization)

        paginator = Paginator(posts, 6)
        page = request.GET.get('page')
        paginated_posts = paginator.get_page(page)

        return render(request, self.template_name, {'posts': paginated_posts})

    def get_filtered_posts(self, category, min_price, max_price, search_query, organization):
        posts = []

        if not category or category == 'food_and_beverage':
            food_posts = FoodAndBeveragePost.objects.all()
            if organization:
                food_posts = food_posts.filter(organization=organization)
            if min_price:
                food_posts = food_posts.filter(price__gte=min_price)
            if max_price:
                food_posts = food_posts.filter(price__lte=max_price)
            if search_query:
                food_posts = food_posts.filter(Q(title__icontains=search_query) | Q(description__icontains=search_query))

            posts += self.format_posts(food_posts, 'food_and_beverage')

        if not category or category == 'conversation_hall':
            hall_posts = ConversationHallPost.objects.all()
            if organization:
                hall_posts = hall_posts.filter(organization=organization)
            if min_price:
                hall_posts = hall_posts.filter( price__gte=min_price)
            if max_price:
                hall_posts = hall_posts.filter( price__lte=max_price)
            if search_query:
                hall_posts = hall_posts.filter(Q(title__icontains=search_query) | Q(description__icontains=search_query))

            posts += self.format_posts(hall_posts, 'conversation_hall')

        if not category or category == 'fun_and_activities':
            activity_posts = FunAndActivitiesPost.objects.all()
            if organization:
                activity_posts = activity_posts.filter(organization=organization)
            if min_price:
                activity_posts = activity_posts.filter(price__gte=min_price)
            if max_price:
                activity_posts = activity_posts.filter(price__lte=max_price)
            if search_query:
                activity_posts = activity_posts.filter(Q(title__icontains=search_query) | Q(description__icontains=search_query))

            posts += self.format_posts(activity_posts, 'fun_and_activities')

        return posts

    def format_posts(self, posts, post_type):
        formatted_posts = []
        
        for post in posts:
            post_data = {
                'id': post.id,
                'title': post.title,
                'description': post.description,
                'price': post.price,
                'type': post_type,
            }
            
            # Check if the post has an 'image' attribute and if it exists
            if hasattr(post, 'image') and post.image:
                post_data['image'] = post.image.url
            else:
                post_data['image'] = None
            
            formatted_posts.append(post_data)
        
        return formatted_posts


class OrderDashboardView(View):
    def get(self, request):
        orders = Order.objects.filter(participant=request.user.participant).order_by('-order_date')
        return render(request, 'order_dashboard.html', {'orders': orders})

@receiver(post_save, sender=Order)
def order_placed_notification(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            recipient=instance.post.organization.organizer.user,  # Fixed field from 'user' to 'recipient'
            message=f"New order placed by {instance.participant.user.username}",
            order=instance
        )


class OrderView(View):
    """Handles order creation for different post types."""
    template_name = 'order_form.html'

    def get_post_instance(self, post_type, post_id):
        """Retrieve the post instance based on the type and ID."""
        post_mapping = {
            'food_and_beverage': FoodAndBeveragePost,
            'conversation_hall': ConversationHallPost,
            'fun_and_activities': FunAndActivitiesPost,
        }
        model = post_mapping.get(post_type)
        if not model:
            return None
        return get_object_or_404(model, id=post_id)

    def get(self, request, post_type, post_id):
        """Render the order form."""
        post = self.get_post_instance(post_type, post_id)
        if not post:
            messages.error(request, "Invalid post type.")
            return redirect('dashboard')

        form = OrderForm(post_type=post_type)
        return render(request, self.template_name, {'form': form, 'post': post})

    def post(self, request, post_type, post_id):
        """Handle order form submission."""
        post = self.get_post_instance(post_type, post_id)
        if not post:
            messages.error(request, "Invalid post type.")
            return redirect('dashboard')

        form = OrderForm(request.POST, post_type=post_type)
        if form.is_valid():
            try:
                with transaction.atomic():
                    order = form.save(commit=False)
                    order.participant = request.user.participant
                    order.post_type = post_type
                    order.post_id = post.id
                    order.total_amount = post.price * order.quantity if post_type == 'food_and_beverage' else post.price * order.duration
                    order.save()

                    messages.success(request, "Order placed successfully!")
                    return redirect('order_list')
            except Exception as e:
                messages.error(request, f"An error occurred: {e}")
        else:
            messages.error(request, "Please correct the errors in the form.")

        return render(request, self.template_name, {'form': form, 'post': post})


class OrderHistoryView(View):
    def get(self, request, *args, **kwargs):
        orders = Order.objects.filter(participant=request.user.participant).order_by('-order_date')
        return render(request, 'order_history.html', {'orders': orders})

from django.views.generic import ListView
from .models import Order

class OrderListView(ListView):
    model = Order
    template_name = 'order_list.html'
    context_object_name = 'orders'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_page'] = 'My_Oder_List'  # Set active page
        return context


class PaymentView(View):
    def get(self, request, order_id, *args, **kwargs):
        order = get_object_or_404(Order, id=order_id)
        if order.status == 'Accepted' and not order.payment_status:
            return render(request, 'payment_form.html', {'order': order})
        return redirect('order_history')

    def post(self, request, order_id, *args, **kwargs):
        order = get_object_or_404(Order, id=order_id)
        payment = Payment.objects.create(order=order, amount_paid=order.total_price, payment_method=request.POST.get('payment_method'))
        payment.save()

        order.payment_status = True
        order.status = 'Paid'
        order.save()

        generate_order_pdf(request, order.id)  # Generate invoice PDF

        return redirect('order_history')


def generate_order_pdf(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    html_string = render_to_string('order_pdf.html', {'order': order})
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="order_{order.id}.pdf"'
    pisa_status = pisa.CreatePDF(html_string, dest=response)
    if pisa_status.err:
        return HttpResponse('Error generating PDF')
    return response
