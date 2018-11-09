# -*- coding:utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import
from __future__ import division

import fcntl

try:
    str = unicode
except NameError:
    pass

import io
import os
import sys
import multiprocessing
import shlex
import fcntl
import socket
import struct

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def run_command(prog, args):
    if sys.version_info[0] < 3:
        arg_list = (prog.decode("utf-8"),) + tuple(shlex.split(args))
    else:
        arg_list = (prog,) + tuple(shlex.split(args))
    print("Running command: ", prog, arg_list)
    return os.execv(prog, arg_list)


def get_ip():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("14.215.177.38", 80))
            ip, _ = s.getsockname()
        return ip
    except:
        return "127.0.0.1"


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


class BaseDeployInformation(object):
    name = "base"
    net_ip = []

    project_name = "blog"
    secret_key = '_(760jtp_nb7$!tb#fh6s-qcg#^1k2bnqljqk=w88jtr9a(wxl'
    debug = True
    base_dir = BASE_DIR

    gunicorn_bind_address = ("127.0.0.1", 8000)
    number_of_gunicorn_worker = 1
    redis_address = ("127.0.0.1", 6379)

    pgsql_address = ("127.0.0.1", 5432)
    pgsql_path = os.path.join(BASE_DIR, "pgsql-data")

    sitename = ("127.0.0.1",)
    api_sitename = tuple()
    static_sitename = ("localhost",)

    backend_servers = [
        ("127.0.0.1", 8000),
    ]

    docker_vpaths = {
        "/home/pgsql": "/home/pgsql",
    }

    @property
    def django_settings(self):
        return {
        }

    @property
    def components(self):
        return ["pgsql", "redis", "gunicorn", "celery"]

    @staticmethod
    def get_docker_image(component):
        if component in ["pgsql", "redis", "gunicorn", "celery"]:
            return "kuaiyun:earth"
        else:
            return ""


class DeveloperDeployInformation(BaseDeployInformation):
    name = "developer"
    debug = True
    base_dir = BASE_DIR

    @property
    def sitename(self):
        ip = get_ip()
        return ("127.0.0.1", ip)


class EarthDeployInformation(BaseDeployInformation):
    name = "47.97.160.187"
    debug = False
    net_ip = ["47.97.160.187"]

    sitename = ("waterlaw.top",)
    static_sitename = ("waterlaw.top",)


class Aliyun228DeployInformation(BaseDeployInformation):
    name = "47.104.230.228"
    debug = False
    net_ip = ["47.104.230.228"]

    sitename = ("waterlaw.top",)
    static_sitename = ("waterlaw.top",)

    pgsql_address = ("pgsql", 5432)


def choice_deploy():
    local_ip = get_ip()
    deploy_info = None
    for obj_name in globals():
        if obj_name.endswith("DeployInformation"):
            if local_ip in globals()[obj_name].net_ip:
                deploy_info = globals()[obj_name]()
                break
    if not deploy_info:
        deploy_info = DeveloperDeployInformation()
    with io.open("product.txt", "w") as f:
        f.write(deploy_info.name)
    return deploy_info


def create_deploy_information():
    product_txts = ["/home/zjp/waterlawblog/product.txt", "/home/code/product.txt"]

    deploy_info = None
    for product_txt in product_txts:
        if os.path.exists(product_txt):
            type_name = io.open(product_txt, "r", encoding="utf-8").read().strip()
            for obj_name in globals():
                if obj_name.endswith("DeployInformation"):
                    if globals()[obj_name].name == type_name:
                        deploy_info = globals()[obj_name]()
                        break

    if not deploy_info:
        deploy_info = choice_deploy()
    if deploy_info not in sys.path:
        sys.path.append(deploy_info.base_dir)
    return deploy_info


def email_host_password():
    email_txts = ["/home/zjp/waterlawblog/email.txt", "/home/code/email.txt"]
    for email_txt in email_txts:
        if os.path.exists(email_txt):
            return io.open(email_txt, mode="r", encoding="utf-8").read().strip()
    return ""
