import os
import sys
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sites.settings")
django.setup()
from oauth2.github import APIClient


def main():
    app_key = "5ce2826552d2560621ca"
    app_secret = "3ac3c4fdc97cb08e1dfa5e0d3b0463ecb652fc86"
    redirect_uri = "http://localhost:8000/github/oauth/callback"
    client = APIClient(app_key=app_key, app_secret=app_secret, redirect_uri=redirect_uri)
    r = client.get_authorize_url()
    print(r.json())
    print(r.text)


if __name__ == '__main__':
    main()