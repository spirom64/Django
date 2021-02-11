from django.urls import path
from . import views

urlpatterns = [
    path('news/', views.NewsListView.as_view(), name = 'news_list'),
    path('news/create/', views.NewsFormView.as_view(), name = 'news_create'),
    path('news/<int:news_id>/edit/', views.NewsEditFormView.as_view(), name = 'news_edit'),
    path('news/<int:pk>/', views.NewsDetailView.as_view(), name = 'news_detail'),
    path('news/<int:news_id>/add-comment/', views.CommentsFormView.as_view(), name = 'comments_create'),
    path('news/<int:news_id>/edit-comment/<int:comment_id>/', views.CommentsEditFormView.as_view(), name = 'comments_edit'),
    path('news/login/', views.NewsLoginView.as_view(), name = 'login'),
    path('news/logout/', views.NewsLogoutView.as_view(), name = 'logout'),
    path('news/register/', views.RegisterView.as_view(), name = 'register'),
    path('news/profile/', views.ProfileView.as_view(), name = 'profile'),
    path('news/profile/edit', views.ProfileEditView.as_view(), name = 'profile_edit'),
    path('news/added/', views.NewsAddView.as_view(), name = 'news_added')
]
