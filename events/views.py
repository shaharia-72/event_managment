from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView
from django.views.generic import TemplateView
from django.db.models import Q

from accounts.models import Organizer
from .models import (
    FoodAndBeveragePost, ConversationHallPost, FunAndActivitiesPost,
    AdminApprovalRequest, Organization
)
from .forms import FoodAndBeveragePostForm, ConversationHallPostForm, FunAndActivitiesPostForm
from django.db.models import Q
from .models import FoodAndBeveragePost, ConversationHallPost, FunAndActivitiesPost
from django.core.paginator import Paginator
from django.shortcuts import render
from django.views.generic import TemplateView
from .models import FoodAndBeveragePost, ConversationHallPost, FunAndActivitiesPost

from django.views.generic import TemplateView
from django.core.paginator import Paginator
from django.shortcuts import render
from .models import FoodAndBeveragePost, ConversationHallPost, FunAndActivitiesPost
from django.views.generic import DetailView, UpdateView
from .models import PostFeedback
from django.http import HttpResponseRedirect
from django.views.generic import DeleteView
from django.contrib.contenttypes.models import ContentType

# Create Post View
def create_post(request, post_type):
    if post_type == 'food_and_beverage':
        form = FoodAndBeveragePostForm(request.POST or None, request.FILES or None)
        template = 'create_food_post.html'
    elif post_type == 'conversation_hall':
        form = ConversationHallPostForm(request.POST or None, request.FILES or None)
        template = 'create_hall_post.html'
    elif post_type == 'fun_and_activities':
        form = FunAndActivitiesPostForm(request.POST or None, request.FILES or None)
        template = 'create_activity_post.html'
    else:
        messages.error(request, "Invalid post type!")
        return redirect('home')

    if request.method == 'POST' and form.is_valid():
        post = form.save(commit=False)
        post.organization = request.user.organizer.organization
        post.save()
        messages.success(request, "Post created successfully!")
        return redirect('home')

    return render(request, template, {'form': form})

# Update Post View
def update_post(request, post_id, post_type):
    if post_type == 'food_and_beverage':
        post = get_object_or_404(FoodAndBeveragePost, id=post_id)
        form = FoodAndBeveragePostForm(request.POST or None, request.FILES or None, instance=post)
        template = 'update_food_post.html'
    elif post_type == 'conversation_hall':
        post = get_object_or_404(ConversationHallPost, id=post_id)
        form = ConversationHallPostForm(request.POST or None, request.FILES or None, instance=post)
        template = 'update_hall_post.html'
    elif post_type == 'fun_and_activities':
        post = get_object_or_404(FunAndActivitiesPost, id=post_id)
        form = FunAndActivitiesPostForm(request.POST or None, request.FILES or None, instance=post)
        template = 'update_activity_post.html'
    else:
        messages.error(request, "Invalid post type!")
        return redirect('home')

    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, "Post updated successfully!")
        return redirect('home')

    return render(request, template, {'form': form, 'post': post})

# Delete Post View
def delete_post(request, post_id, post_type):
    if post_type == 'food_and_beverage':
        post = get_object_or_404(FoodAndBeveragePost, id=post_id)
    elif post_type == 'conversation_hall':
        post = get_object_or_404(ConversationHallPost, id=post_id)
    elif post_type == 'fun_and_activities':
        post = get_object_or_404(FunAndActivitiesPost, id=post_id)
    else:
        messages.error(request, "Invalid post type!")
        return redirect('home')

    if request.method == 'POST':
        post.delete()
        messages.success(request, "Post deleted successfully!")
        return redirect('home')

    return render(request, 'delete_post.html', {'post': post})

# Admin Approval Request View
class RequestAdminApprovalView(View):
    template_name = 'request_approval.html'

    def get(self, request, *args, **kwargs):
        try:
            organization = request.user.organizer.organization
        except AttributeError:
            messages.error(request, "You need to be an organizer with an associated organization.")
            return redirect('home')

        # Fetch statuses dynamically for all tags
        statuses = self.get_all_statuses(organization)

        context = {
            'statuses': statuses,
            'active_page': 'Unlock',
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        tag = request.POST.get('tag')  # Feature tag
        action = request.POST.get('action')  # Action (send, cancel, resend)

        try:
            organization = request.user.organizer.organization
        except AttributeError:
            messages.error(request, "You need to be an organizer with an associated organization.")
            return redirect('home')

        if tag and action:
            # Fetch or create the approval request
            approval_request, created = AdminApprovalRequest.objects.get_or_create(
                organization=organization,
                tag=tag,
            )

            # Perform actions based on the button clicked
            if action == 'send':
                approval_request.set_pending()
                messages.success(request, f'Request for {tag} sent successfully.')

            elif action == 'cancel':
                approval_request.delete()  # Cancel the request
                messages.success(request, f'Request for {tag} has been canceled.')

            elif action == 'resend':
                approval_request.set_pending()
                messages.success(request, f'Request for {tag} resent successfully.')

        return redirect('request_approval')

    def get_all_statuses(self, organization):
        """Fetches status for all features dynamically."""
        tags = ['food_and_beverage', 'conversation_hall', 'fun_and_activities']
        statuses = {}

        for tag in tags:
            approval_request = AdminApprovalRequest.objects.filter(organization=organization, tag=tag).first()
            if approval_request:
                statuses[tag] = approval_request.status
            else:
                statuses[tag] = 'Not Requested'  # Default for new features
        return statuses

# Some view to pass the approval statuses to the navbar template
def organizer_dashboard(request):
    if request.user.is_organizer:
        # Get the associated organization for the logged-in user
        organization = request.user.organizer.organization
        
        # Fetch the approval status for each feature
        food_approval_status = 'Approved' if organization.is_active_food_and_beverage else 'Not Approved'
        hall_approval_status = 'Approved' if organization.is_active_conversation_hall else 'Not Approved'
        activity_approval_status = 'Approved' if organization.is_active_fun_and_activities else 'Not Approved'
        
        # Pass approval statuses to navbar or the view that renders the navbar
        context = {
            'food_approval_status': food_approval_status,
            'hall_approval_status': hall_approval_status,
            'activity_approval_status': activity_approval_status
        }
        return render(request, 'organizer_dashboard.html', context)
    else:
        messages.error(request, "You are not an organizer.")
        return redirect('home')

# Common function to fetch post based on type
def get_post_and_form(post_type, pk):
    if post_type == 'food_and_beverage':
        post = get_object_or_404(FoodAndBeveragePost, pk=pk)
        form_class = FoodAndBeveragePostForm
    elif post_type == 'conversation_hall':
        post = get_object_or_404(ConversationHallPost, pk=pk)
        form_class = ConversationHallPostForm
    elif post_type == 'fun_and_activities':
        post = get_object_or_404(FunAndActivitiesPost, pk=pk)
        form_class = FunAndActivitiesPostForm
    else:
        raise ValueError("Invalid Post Type")
    return post, form_class

class AllPostsView(View):
    template_name = 'home.html'

    def get(self, request):
        # Get query parameters
        category = request.GET.get('category')
        min_price = request.GET.get('min_price')
        max_price = request.GET.get('max_price')
        search_query = request.GET.get('search')

        # Get the current user and their associated organization
        user = request.user
        organization = None
        if user.is_authenticated:
            try:
                # Fetch the organization for the authenticated user (assuming they are an organizer)
                organization = user.organizer.organization
            except Organizer.DoesNotExist:
                pass  # User is not an organizer, no organization found

        # Filter posts dynamically
        posts = []

        # Food and Beverage Posts
        if not category or category == 'food_and_beverage':
            food_posts = FoodAndBeveragePost.objects.all()
            if organization:
                food_posts = food_posts.filter(organization=organization)  # Filter by organization
            if min_price:
                food_posts = food_posts.filter(price__gte=min_price)
            if max_price:
                food_posts = food_posts.filter(price__lte=max_price)
            if search_query:
                food_posts = food_posts.filter(Q(title__icontains=search_query) | Q(description__icontains=search_query))

            posts += [{
                'id': post.id,
                'title': post.title,
                'description': post.description,
                'image': post.image.url if post.image else None,
                'price': post.price,
                'type': 'food_and_beverage'
            } for post in food_posts]

        # Conversation Hall Posts
        if not category or category == 'conversation_hall':
            hall_posts = ConversationHallPost.objects.all()
            if organization:
                hall_posts = hall_posts.filter(organization=organization)  # Filter by organization
            if min_price:
                hall_posts = hall_posts.filter(price_per_hour__gte=min_price)
            if max_price:
                hall_posts = hall_posts.filter(price_per_hour__lte=max_price)
            if search_query:
                hall_posts = hall_posts.filter(Q(title__icontains=search_query) | Q(description__icontains=search_query))

            posts += [{
                'id': post.id,
                'title': post.title,
                'description': post.description,
                'image': post.images.url if post.images else None,
                'price': post.price_per_hour,
                'type': 'conversation_hall'
            } for post in hall_posts]

        # Fun & Activities Posts
        if not category or category == 'fun_and_activities':
            activity_posts = FunAndActivitiesPost.objects.all()
            if organization:
                activity_posts = activity_posts.filter(organization=organization)  # Filter by organization
            if min_price:
                activity_posts = activity_posts.filter(price__gte=min_price)
            if max_price:
                activity_posts = activity_posts.filter(price__lte=max_price)
            if search_query:
                activity_posts = activity_posts.filter(Q(title__icontains=search_query) | Q(description__icontains=search_query))

            posts += [{
                'id': post.id,
                'title': post.title,
                'description': post.description,
                'image': post.image.url if post.image else None,
                'price': post.price,
                'type': 'fun_and_activities'
            } for post in activity_posts]

        # Pagination
        paginator = Paginator(posts, 6)
        page = request.GET.get('page')
        paginated_posts = paginator.get_page(page)

        return render(request, self.template_name, {'posts': paginated_posts})


# The combined Detail and Update View
class PostDetailView(DetailView, UpdateView):
    template_name = 'post_detail.html'
    
    def get_object(self, queryset=None):
        post_type = self.kwargs['post_type']
        pk = self.kwargs['pk']
        post, _ = get_post_and_form(post_type, pk)
        return post

    def get_form_class(self):
        _, form_class = get_post_and_form(self.kwargs['post_type'], self.kwargs['pk'])
        return form_class

    def post(self, request, *args, **kwargs):
        post = self.get_object()

        if 'reply_feedback' in request.POST:
            feedback = request.POST.get('feedback_text')

            # Create feedback dynamically for any post type
            PostFeedback.objects.create(
                content_type=ContentType.objects.get_for_model(post),
                object_id=post.id,
                feedback_text=feedback,
                participant=request.user.participant  # Ensure `Participant` user is set up
            )
            messages.success(request, 'Feedback posted successfully!')
            return HttpResponseRedirect(
                reverse_lazy('post_detail', kwargs={'post_type': kwargs['post_type'], 'pk': kwargs['pk']})
            )

        # Handle updates using the parent method
        return super().post(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.get_object()

        # Retrieve feedbacks based on generic relation
        content_type = ContentType.objects.get_for_model(post)
        context['feedbacks'] = PostFeedback.objects.filter(
            content_type=content_type,
            object_id=post.id
        )

        context['post_type'] = self.kwargs['post_type']
        context['edit_mode'] = 'edit' in self.request.GET
        return context

    def get_success_url(self):
        return reverse_lazy('post_detail', kwargs={
            'post_type': self.kwargs['post_type'],
            'pk': self.kwargs['pk']
        })
    
class PostDeleteView(DeleteView):
    template_name = 'post_confirm_delete.html'

    def get_object(self, queryset=None):
        # Dynamically fetch the correct model based on post_type
        post_type = self.kwargs['post_type']
        pk = self.kwargs['pk']
        post, _ = get_post_and_form(post_type, pk)  # Reuse existing helper function
        return post

    def get_success_url(self):
        messages.success(self.request, 'Post deleted successfully!')
        # Redirect to the list view of posts after deletion
        post_type = self.kwargs.get('post_type')
        return reverse_lazy('all_posts', kwargs={'post_type': post_type})
