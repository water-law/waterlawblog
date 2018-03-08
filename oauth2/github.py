import six
import collections
import time
import requests

if six.PY3:
    from urllib import request as urllib2
    unicode = str
    basestring = str
    Exception = BaseException
else:
    import urllib2


class APIError(Exception):
    def __init__(self, error_code, error, request):
        self.error_code = error_code
        self.error = error
        self.request = request
        Exception.__init__(self, error)

    def __str__(self):
        return 'APIError: %s: %s, request: %s' % (
            self.error_code, self.error, self.request)


def _encode_params(**kw):
    '''
    do url-encode parameters

    >>> _encode_params(a=1, b='R&D')
    'a=1&b=R%26D'
    >>> _encode_params(a=u'\u4e2d\u6587', b=['A', 'B', 123])
    'a=%E4%B8%AD%E6%96%87&b=A&b=B&b=123'
    '''
    args = []
    for k, v in kw.items():
        if isinstance(v, basestring):
            qv = v.encode('utf-8') if isinstance(v, unicode) else v
            args.append('%s=%s' % (k, urllib2.quote(qv)))
        elif isinstance(v, collections.Iterable):
            for i in v:
                qv = i.encode('utf-8') if isinstance(v, unicode) else v
                args.append('%s=%s' % (k, urllib2.quote(qv)))
        else:
            qv = str(v)
            args.append('%s=%s' % (k, urllib2.quote(qv)))

    return '&'.join(args)


class APIClient(object):

    def __init__(
            self,
            app_key,
            app_secret,
            redirect_uri=None,
            response_type='code',
            domain='api.github.com',
            ):
        self.client_id = str(app_key)
        self.client_secret = str(app_secret)
        self.redirect_uri = redirect_uri
        self.response_type = response_type
        self.auth_url = 'https://github.com/login/oauth/'
        self.api_url = 'https://%s/' % domain
        self.access_token = None
        self.expires = 0.0

    def set_access_token(self, access_token, expires):
        self.access_token = str(access_token)
        self.expires = float(expires)

    def get_authorize_url(self, redirect_uri=None, **kw):
        redirect = redirect_uri if redirect_uri else self.redirect_uri
        if not redirect:
            raise APIError(
                '23105',
                'Parameter absent: redirect_uri',
                'OAuth2 request')
        response_type = kw.pop('response_type', 'code')
        return '%s%s?%s' % (self.auth_url, 'authorize',
                          _encode_params(client_id=self.client_id,
                                         response_type=response_type,
                                         redirect_uri=redirect, **kw))

    # noinspection PyMethodMayBeStatic
    def _parse_access_token(self, r):
        if isinstance(r.content, bytes):
            r = r.content.decode()
        access_token = r.split('&')[0].split('=')[1]
        current = int(time.time())
        expires = 0.0 + current
        return dict(access_token=access_token,
                    expires=expires,
                    expires_in=expires)

    def request_access_token(self, code, redirect_uri=None):
        redirect = redirect_uri if redirect_uri else self.redirect_uri
        if not redirect:
            raise APIError(
                '23105',
                'Parameter absent: redirect_uri',
                'OAuth2 request')

        r = requests.get('%s%s' % (self.auth_url, 'access_token'),
                     params={
                         "client_id": self.client_id,
                         "client_secret": self.client_secret,
                         "code":code,
                         "redirect_uri": redirect})
        return self._parse_access_token(r)

    def refresh_token(self, refresh_token):
        pass








