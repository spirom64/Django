from django import forms
from app_news.models import News, Comments, Profile
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class NewsForm(forms.ModelForm):

    class Meta:
        model = News
        exclude = ['published_at', 'updated_at', 'user', 'is_approved']

class CommentsFormAuth(forms.ModelForm):

    class Meta:
        model = Comments
        exclude = ['news', 'user', 'username']

class CommentsFormNonAuth(forms.ModelForm):

    class Meta:
        model = Comments
        exclude = ['news', 'user']

class ExtendedRegisterForm(UserCreationForm):
    first_name = forms.CharField(max_length = 30, required = False, help_text = 'Имя')
    last_name = forms.CharField(max_length = 30, required = False, help_text = 'Фамилия')
    phone = forms.CharField(max_length = 30, required = False, help_text = 'Телефон')
    city = forms.CharField(max_length = 30, required = False, help_text = 'Город')

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'password1', 'password2', 'phone', 'city']

class ProfileForm(forms.ModelForm):

    class Meta:
        model = Profile
        fields = ['city', 'phone']

class UserEditForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ['first_name', 'last_name']

class TagsForm(forms.Form):
    tags = forms.CharField(widget = forms.Textarea(attrs = {'placeholder': 'Теги'}),
                            label = 'Теги (по 1 в строке)', 
                            required = False)