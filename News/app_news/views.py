from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView
from django.views import View
from app_news.models import News, Comments, Profile, Tags
from app_news.forms import NewsForm, CommentsFormAuth, CommentsFormNonAuth, ExtendedRegisterForm, ProfileForm, UserEditForm, TagsForm
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth import authenticate, login
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.models import User
from datetime import date, datetime

class NewsListView(ListView):
    model = News
    context_object_name = 'news_list'

    def get_context_data(self, **kwargs):
        context = super(NewsListView, self).get_context_data(**kwargs)
        context['title'] = 'Список новостей'
        return context

    def get_queryset(self):
        queryset = News.objects.filter(is_approved = True)
        if self.request.GET.get('date'):
            filter_date = datetime.strptime(self.request.GET.get('date'), '%Y-%m-%d').date()
            queryset = queryset.filter(published_at__date = filter_date)
        if self.request.GET.get('tag'):
            tag = self.request.GET.get('tag')
            queryset = queryset.filter(tags__tag = tag)
        return queryset

class NewsDetailView(DetailView):
    model = News
    context_object_name = 'news'

class NewsFormView(View):
    def get(self, request):
        news_form = NewsForm()
        tags_form = TagsForm()
        return render(request, 'app_news/create_edit_news.html', context = {'news_form' : news_form, 'title' : 'Создать новость', 'tags_form' : tags_form})

    def post(self, request):
        news_form = NewsForm(request.POST)
        tags_form = TagsForm(request.POST)

        if news_form.is_valid() and tags_form.is_valid():
            news = News.objects.create(**news_form.cleaned_data, user = request.user)
            tags = [tag.strip() for tag in tags_form.cleaned_data['tags'].splitlines()]
            for tag in tags:
                tag_obj, created = Tags.objects.get_or_create(tag = tag)
                tag_obj.news.add(news)
                tag_obj.save()
            return HttpResponseRedirect(reverse('news_added'))

        return render(request, 'app_news/create_edit_news.html', context = {'news_form' : news_form, 'title' : 'Создать новость'})

class NewsEditFormView(View):
    def get(self, request, news_id):
        news = News.objects.get(id = news_id)
        news_form = NewsForm(instance = news)
        return render(request, 'app_news/create_edit_news.html', context = {'news_form' : news_form, 'title' : 'Редактировать новость', 'news_id' : news_id})

    def post(self, request, news_id):
        news = News.objects.get(id = news_id)
        news_form = NewsForm(request.POST, instance = news)

        if news_form.is_valid():
            news.save()
            return HttpResponseRedirect(reverse('news_detail', args = [news_id]))

        return render(request, 'app_news/create_edit_news.html', context = {'news_form' : news_form, 'title' : 'Редактировать новость', 'news_id' : news_id})

class CommentsFormView(View):
    def get(self, request, news_id):
        if request.user.is_authenticated:
            comments_form = CommentsFormAuth()
        else:
            comments_form = CommentsFormNonAuth()
        return render(request, 'app_news/news_detail.html', context = {'comments_form' : comments_form, 'news' : News.objects.get(id = news_id)})

    def post(self, request, news_id):
        if request.user.is_authenticated:
            comments_form = CommentsFormAuth(request.POST)
        else:
            comments_form = CommentsFormNonAuth(request.POST)
        news_obj = News.objects.get(id = news_id)

        if comments_form.is_valid():
            Comments.objects.create(**comments_form.cleaned_data, news = news_obj, user = request.user if request.user.is_authenticated else None)
            return HttpResponseRedirect(reverse('news_detail', args = [news_id]))

        return render(request, 'app_news/news_detail.html', context = {'comments_form' : comments_form, 'news' : news_obj})

class CommentsEditFormView(View):
    def get(self, request, news_id, comment_id):
        news = News.objects.get(id = news_id)
        comment = Comments.objects.get(id = comment_id)
        comments_form = CommentsFormAuth(instance = comment)
        return render(request, 'app_news/news_detail.html', context = {'news' : news, 'comment_id' : comment_id, 'comments_form' : comments_form})

    def post(self, request, news_id, comment_id):
        news = News.objects.get(id = news_id)
        comment = Comments.objects.get(id = comment_id)
        comments_form = CommentsFormAuth(request.POST, instance = comment)

        if comments_form.is_valid():
            comment.save()
            return HttpResponseRedirect(reverse('news_detail', args = [news_id]))

        return render(request, 'app_news/news_detail.html', context = {'news' : news, 'comment_id' : comment_id, 'comments_form' : comments_form})

class NewsLoginView(LoginView):
    template_name = 'app_news/login.html'

class NewsLogoutView(LogoutView):
    template_name = 'app_news/logout.html'
    next_page = '/news/'

class RegisterView(View):
    def get(self, request):
        form = ExtendedRegisterForm()
        return render(request, 'app_news/register.html', context = {'form' : form})

    def post(self, request):
        form = ExtendedRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            phone = form.cleaned_data.get('phone')
            city = form.cleaned_data.get('city')
            Profile.objects.create(user = user, phone = phone, city = city)
            user = authenticate(username = username, password = password)
            login(request, user)
            return redirect(reverse('news_list'))
        return render(request, 'app_news/register.html', context = {'form' : form})

class ProfileView(View):
    def get(self, request):
        return render(request, 'app_news/user_detail.html')

class NewsAddView(View):
    def get(self, request):
        return render(request, 'app_news/news_added.html')

class ProfileEditView(View):
    def get(self, request):
        user = request.user
        if hasattr(user, 'profile'):
            profile = user.profile
            profile_form = ProfileForm(instance = profile)
        else:
            profile_form = ProfileForm()
        user_form = UserEditForm(instance = user)
        return render(request, 'app_news/profile_edit.html', context = {'user_form' : user_form, 'profile_form' : profile_form})

    def post(self, request):
        user = request.user
        if hasattr(user, 'profile'):
            profile = user.profile
            profile_form = ProfileForm(request.POST, instance = profile)
        else:
            profile_form = ProfileForm(request.POST)
        user_form = UserEditForm(request.POST, instance = user)
        if user_form.is_valid() and profile_form.is_valid():
            if hasattr(user, 'profile'):
                profile.save()
            else:
                phone = profile_form.cleaned_data.get('phone')
                city = profile_form.cleaned_data.get('city')
                Profile.objects.create(user = user, phone = phone, city = city) 
            user.save()
            return HttpResponseRedirect(reverse('profile'))
        return render(request, 'app_news/profile_edit.html', context = {'user_form' : user_form, 'profile_form' : profile_form})