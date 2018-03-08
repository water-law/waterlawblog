from django.contrib.auth.forms import UserCreationForm
from django import forms
from .models import User, Post
from comment.models import Comment


class RegisterForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", )


class PublishForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = ['title', 'body', 'tags', "category"]


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('content', )
