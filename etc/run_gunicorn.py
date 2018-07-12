#!/usr/bin/env python
# -*- coding:utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import
from __future__ import division

import os
import socket
import fcntl
import gunicorn.app.base
import struct

from etc.deploy import create_deploy_information


def fix_sslwrap():
    import inspect
    __ssl__ = __import__('ssl')

    try:
        _ssl = __ssl__._ssl
    except AttributeError:
        _ssl = __ssl__._ssl2

    def new_sslwrap(sock, server_side=False, keyfile=None, certfile=None, cert_reqs=__ssl__.CERT_NONE, ssl_version=__ssl__.PROTOCOL_SSLv23, ca_certs=None, ciphers=None):
        context = __ssl__.SSLContext(ssl_version)
        context.verify_mode = cert_reqs or __ssl__.CERT_NONE
        if ca_certs:
            context.load_verify_locations(ca_certs)
        if certfile:
            context.load_cert_chain(certfile, keyfile)
        if ciphers:
            context.set_ciphers(ciphers)

        caller_self = inspect.currentframe().f_back.f_locals['self']
        return context._wrap_socket(sock, server_side=server_side, ssl_sock=caller_self)

    if not hasattr(_ssl, 'sslwrap'):
        _ssl.sslwrap = new_sslwrap


def get_interface_ip(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        r = socket.inet_ntoa(fcntl.ioctl(
            s.fileno(),
            0x8915,  # SIOCGIFADDR
            struct.pack(b'256s', ifname.encode()[:15])
        )[20:24])
    except IOError:
        return ""
    return r.decode("ascii")


def post_fork(server, worker):
    from . import gevent_psycopg2
    gevent_psycopg2.monkey_patch()


# TODO 有 Application 为啥要继承自 BaseApplication 呢？
class StandaloneApplication(gunicorn.app.base.BaseApplication):
    def load_config(self):
        deploy_info = create_deploy_information()
        options = {
            'bind': "{}:{}".format(*deploy_info.gunicorn_bind_address),
            'workers': deploy_info.number_of_gunicorn_worker,
            "max_requests": 1024 * 4,
            "max_requests_jitter": 512,
            "preload_app": False,
            "worker_connections": 100,  # 跟数据库的连接数有关。
            "default_proc_name": deploy_info.project_name,
            "worker_class": "gevent",
            "pidfile": os.path.join(deploy_info.base_dir, "gunicorn.pid"),
            "accesslog": "/dev/null",   # os.path.join(BASE_DIR, "logs/gunicorn_access.log"),
            "errorlog": os.path.join(deploy_info.base_dir, "logs/gunicorn_error.log"),
            "post_fork": post_fork,
            "forwarded_allow_ips": ",".join(backend[0] for backend in deploy_info.backend_servers),
        }
        for key, value in options.items():
            if key in self.cfg.settings and value is not None:
                self.cfg.set(key.lower(), value)

    def load(self):
        from sites.wsgi import application
        return application


def main():
    print("start gunicorn.")
    fix_sslwrap()
    StandaloneApplication().run()


if __name__ == "__main__":
    main()
