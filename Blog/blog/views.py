from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView
from django.views import View
from blog.models import Profile, Post, File
from blog.forms import ExtendedRegisterForm, ProfileForm, UserEditForm, PostForm, FileForm, PostAddListForm
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth import authenticate, login
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.models import User
from datetime import date, datetime
from csv import reader
from django.core.exceptions import PermissionDenied

class BlogListView(ListView):
    model = Post
    context_object_name = 'post_list'

    def get_context_data(self, **kwargs):
        context = super(BlogListView, self).get_context_data(**kwargs)
        context['title'] = 'Список записей'
        return context

    def get_queryset(self):
        queryset = Post.objects.all()
        if self.request.GET.get('date'):
            filter_date = datetime.strptime(self.request.GET.get('date'), '%Y-%m-%d').date()
            queryset = queryset.filter(published_at__date = filter_date)
        return queryset

class PostAddListFormView(View):
    def get(self, request):
        post_form = PostAddListForm()
        return render(request, 'blog/create_edit_post.html', context = {'post_form' : post_form, 'title' : 'Добавить записи файлом csv'})

    def post(self, request):
        post_form = PostAddListForm(request.POST, request.FILES)

        if post_form.is_valid():
            f = post_form.cleaned_data.get('file').read()
            post_str = f.decode('utf-8').split('\n')
            csv_reader = reader(post_str, delimiter = ',', quotechar = '"')
            for row in csv_reader:
                if len(row) == 2:
                    Post.objects.create(title = row[0].strip(), description = row[1].strip(), user = request.user)
            return HttpResponseRedirect(reverse('blog_list'))

        return render(request, 'blog/create_edit_post.html', context = {'post_form' : post_form, 'title' : 'Добавить записи файлом csv'})

class PostFormView(View):
    def get(self, request):
        post_form = PostForm()
        file_form = FileForm()
        return render(request, 'blog/create_edit_post.html', context = {'post_form' : post_form, 'title' : 'Создать запись', 'file_form' : file_form})

    def post(self, request):
        post_form = PostForm(request.POST)
        file_form = FileForm(request.POST, request.FILES)

        if post_form.is_valid() and file_form.is_valid():
            post = Post.objects.create(**post_form.cleaned_data, user = request.user)
            files = request.FILES.getlist('files')
            for f in files:
                instance = File(file = f, post = post)
                instance.save()
            return HttpResponseRedirect(reverse('blog_list'))

        return render(request, 'blog/create_edit_post.html', context = {'post_form' : post_form, 'title' : 'Создать запись', 'file_form' : file_form})

class PostEditFormView(View):
    def get(self, request, post_id):
        post = Post.objects.get(id = post_id)
        if request.user != post.user:
            raise PermissionDenied
        if request.GET.get('delete'):
            file_id = request.GET.get('delete')
            f = File.objects.get(id = file_id)
            f.on_delete = True
            f.save()
        if request.GET.get('restore'):
            file_id = request.GET.get('restore')
            f = File.objects.get(id = file_id)
            f.on_delete = False
            f.save()
        post_form = PostForm(instance = post)
        file_form = FileForm()
        return render(request, 'blog/create_edit_post.html', context = {'post_form' : post_form, 'title' : 'Редактировать запись', 'post' : post, 'file_form' : file_form})

    def post(self, request, post_id):
        post = Post.objects.get(id = post_id)
        if request.user != post.user:
            raise PermissionDenied
        post_form = PostForm(request.POST, instance = post)
        file_form = FileForm(request.POST, request.FILES)

        if post_form.is_valid() and file_form.is_valid():
            for f in post.files.all():
                if f.on_delete:
                    f.delete()
            post.save()
            files = request.FILES.getlist('files')
            for f in files:
                instance = File(file = f, post = post)
                instance.save()
            return HttpResponseRedirect(reverse('post_detail', args = [post_id]))

        return render(request, 'blog/create_edit_post.html', context = {'post_form' : post_form, 'title' : 'Редактировать запись', 'post' : post, 'file_form' : file_form})

class PostDetailView(DetailView):
    model = Post
    context_object_name = 'post'

class BlogLoginView(LoginView):
    template_name = 'blog/login.html'
    redirect_field_name = 'next'

class BlogLogoutView(LogoutView):
    template_name = 'blog/logout.html'
    next_page = '/blog/posts/'

class RegisterView(View):
    def get(self, request):
        form = ExtendedRegisterForm()
        return render(request, 'blog/register.html', context = {'form' : form})

    def post(self, request):
        form = ExtendedRegisterForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            phone = form.cleaned_data.get('phone')
            city = form.cleaned_data.get('city')
            photo = form.cleaned_data.get('photo')
            description = form.cleaned_data.get('description')
            Profile.objects.create(user = user, phone = phone, city = city, photo = photo, description = description)
            user = authenticate(username = username, password = password)
            login(request, user)
            return redirect(reverse('blog_list'))
        return render(request, 'blog/register.html', context = {'form' : form})

class ProfileView(View):
    def get(self, request):
        return render(request, 'blog/user_detail.html')

class ProfileEditView(View):
    def get(self, request):
        user = request.user
        if hasattr(user, 'profile'):
            profile = user.profile
            profile_form = ProfileForm(instance = profile)
        else:
            profile_form = ProfileForm()
        user_form = UserEditForm(instance = user)
        return render(request, 'blog/profile_edit.html', context = {'user_form' : user_form, 'profile_form' : profile_form})

    def post(self, request):
        user = request.user
        if hasattr(user, 'profile'):
            profile = user.profile
            profile_form = ProfileForm(request.POST, request.FILES, instance = profile)
        else:
            profile_form = ProfileForm(request.POST, request.FILES)
        user_form = UserEditForm(request.POST, instance = user)
        if user_form.is_valid() and profile_form.is_valid():
            if hasattr(user, 'profile'):
                profile.save()
            else:
                phone = profile_form.cleaned_data.get('phone')
                city = profile_form.cleaned_data.get('city')
                description = profile_form.cleaned_data.get('description')
                photo = profile_form.cleaned_data.get('photo')
                Profile.objects.create(user = user, phone = phone, city = city, photo = photo, description = description) 
            user.save()
            return HttpResponseRedirect(reverse('profile'))
        return render(request, 'blog/profile_edit.html', context = {'user_form' : user_form, 'profile_form' : profile_form})