"""blog URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin


urlpatterns = [
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^admin/', admin.site.urls),
    url(r'', include('blog.urls')),
    url(r'', include('blockchain.views')),
    url(r'api/v1/', include('blogapi.api_v1')),
    url(r'api/v2/', include('blogapi.api_v2')),
    url(r'', include('webreader.views')),
    url(r'^search/', include('haystack.urls')),
    url(r'', include('oauth2.views')),
]

# if django_settings.DEBUG:
#     urlpatterns.extend([
#         url(r'^media/(?P<path>.*)$', 'django.views.static.serve',
#             {"document_root": django_settings.MEDIA_ROOT}),
#         url(r'^static/(?P<path>.*)$', 'django.views.static.serve',
#             {"document_root": django_settings.STATIC_ROOT}),
#         url(r"^c.js", 'django.contrib.staticfiles.views.serve',
#             {"path": "adscript/d.js", "insecure": True}),
#     ])
