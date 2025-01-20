from django.urls import path
from . import views
from .views import RequestAdminApprovalView, AllPostsView, PostDetailView, PostDeleteView

urlpatterns = [
    # Function-based views for post creation, update, and deletion
    path('create_post/<str:post_type>/', views.create_post, name='create_post'),
    path('update_post/<int:post_id>/<str:post_type>/', views.update_post, name='update_post'),
    path('delete_post/<int:post_id>/<str:post_type>/', views.delete_post, name='delete_post'),
    
    # Class-based view for requesting admin approval
    path('request-approval/', RequestAdminApprovalView.as_view(), name='request_approval'),
    
    # Class-based view for displaying all posts with pagination and filters
    path('all_posts/', AllPostsView.as_view(), name='all_posts'),
    path('post/<str:post_type>/<int:pk>/', PostDetailView.as_view(), name='post_detail'),
    # path('post/<str:post_type>/<int:pk>/', PostDetailView.as_view(), name='post_detail'),
    path('post/<str:post_type>/delete/<int:pk>/', PostDeleteView.as_view(), name='post_delete'),
    # path('post/<int:pk>/', views.PostDetailView.as_view(), name='post_detail'),
]
