from django.conf.urls import url
from django.shortcuts import render


def web_reader(request):
    return render(request, 'reader.html')


app_name = 'webreader'
urlpatterns = [
    url(r'^webreader/$', web_reader, name='webreader'),
]