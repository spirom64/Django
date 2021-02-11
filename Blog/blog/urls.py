from django.urls import path
from . import views
from django.contrib.auth.decorators import login_required

urlpatterns = [
    path('posts/', views.BlogListView.as_view(), name = 'blog_list'),
    path('new/', login_required(views.PostFormView.as_view()), name = 'post_create'),
    path('add_list/', login_required(views.PostAddListFormView.as_view()), name = 'post_add_list'),
    path('post/<int:post_id>/edit/', login_required(views.PostEditFormView.as_view()), name = 'post_edit'),
    path('post/<int:pk>/', views.PostDetailView.as_view(), name = 'post_detail'),
    path('login/', views.BlogLoginView.as_view(), name = 'login'),
    path('logout/', views.BlogLogoutView.as_view(), name = 'logout'),
    path('register/', views.RegisterView.as_view(), name = 'register'),
    path('profile/', login_required(views.ProfileView.as_view()), name = 'profile'),
    path('profile/edit', login_required(views.ProfileEditView.as_view()), name = 'profile_edit')
]
