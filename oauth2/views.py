import random
import requests
from django.shortcuts import redirect
from django.conf.urls import url
from django.http.response import HttpResponseBadRequest
from django.contrib.auth import login
from .github import APIClient
from blog.models import User, Github


def rand_username():
    seed = "1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    while True:
        sa = []
        for i in range(6):
            sa.append(random.choice(seed))
        salt = ''.join(sa)
        if not User.objects.filter(username=salt).exists():
            return salt


def callback(request):
    if not request.GET:
        return HttpResponseBadRequest
    host = request.get_host()
    app_key = "5ce2826552d2560621ca"
    app_secret = "3ac3c4fdc97cb08e1dfa5e0d3b0463ecb652fc86"
    redirect_uri = "https://%s/github/oauth/callback" % host
    client = APIClient(app_key=app_key, app_secret=app_secret, redirect_uri=redirect_uri)
    code = request.GET.get("code")
    d= client.request_access_token(code=code)
    user_info = requests.get("https://api.github.com/user",
                             params={"access_token": d["access_token"]})
    github_info = user_info.json()
    github, ok = Github.objects.update_or_create(
        github_id=github_info["id"],
        defaults={
            "login_name": github_info["login"],
            "avatar_url": github_info["avatar_url"]
        }
    )
    try:
        user = User.objects.get(github=github)
        login_user = user
    except User.DoesNotExist:
        if User.objects.filter(username=github_info["login"]).exists():
            new_user, created = User.objects.update_or_create(
                username=rand_username(),
                defaults={
                    "github": github
                }
            )
        else:
            new_user, created = User.objects.update_or_create(
                username=github_info["login"],
                defaults={
                    "github": github
                }
            )
        login_user = new_user
    login(request, login_user)

    return redirect("/")


urlpatterns = [
    url(r'^github/oauth/callback$', callback),
]
