from django import forms
from blog.models import Profile, Post, File
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class ExtendedRegisterForm(UserCreationForm):
    first_name = forms.CharField(max_length = 30, required = False, help_text = 'Имя')
    last_name = forms.CharField(max_length = 30, required = False, help_text = 'Фамилия')
    phone = forms.CharField(max_length = 30, required = False, help_text = 'Телефон')
    city = forms.CharField(max_length = 30, required = False, help_text = 'Город')
    photo = forms.ImageField(required = False, help_text = 'Аватар')
    description = forms.CharField(widget = forms.Textarea(attrs = {'placeholder': 'О себе'}),
                            label = 'Введите информацию о себе', 
                            required = False)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'password1', 'password2', 'phone', 'city', 'photo', 'description']

class ProfileForm(forms.ModelForm):

    class Meta:
        model = Profile
        fields = ['city', 'phone', 'photo', 'description']

class UserEditForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ['first_name', 'last_name']

class FileForm(forms.Form):
    files = forms.ImageField(widget = forms.ClearableFileInput(attrs = {'multiple' : True}), required = False)

class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = ['title', 'description']

class PostAddListForm(forms.Form):
    file = forms.FileField(help_text = 'Добавьте файл csv с записями')