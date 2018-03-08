import requests
from django.shortcuts import redirect
from django.conf.urls import url
from django.http.response import HttpResponseBadRequest
from .github import APIClient


def callback(request):
    if not request.GET:
        return HttpResponseBadRequest
    app_key = "5ce2826552d2560621ca"
    app_secret = "3ac3c4fdc97cb08e1dfa5e0d3b0463ecb652fc86"
    redirect_uri = "http://localhost:8000/github/oauth/callback"
    client = APIClient(app_key=app_key, app_secret=app_secret, redirect_uri=redirect_uri)
    code = request.GET.get("code")
    d= client.request_access_token(code=code)
    user_info = requests.get("https://api.github.com/user",
                             params={"access_token": d["access_token"]})
    print(user_info.text)

    return redirect("/")


urlpatterns = [
    url(r'^github/oauth/callback$', callback),
]
