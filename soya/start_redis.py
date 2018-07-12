#!/usr/bin/env python
# -*- coding:utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import
from __future__ import division

import os
from soya.deploy import create_deploy_information, run_command


def start_redis_main(deploy_info):
    redis_data_dir = os.path.join(deploy_info.base_dir, "redis-data")
    bound = deploy_info.redis_address
    print(bound[0], bound[1])
    for p in ("/usr/sbin/redis-server", "/usr/bin/redis-server", "/usr/local/bin/redis-server"):
        if os.path.exists(p):
            redis_bin = p
            break
    else:
        return None

    redis_args = "--daemonize no --bind {bound_ip} --port {bound_port} --databases 2 " \
                 "--dir {redis_data_dir} --maxclients 10000"
    redis_args += " --dbfilename dump.rdb --save 300 10000 --save 1200 1"
    redis_args = redis_args.format(**{
        "bound_ip": bound[0],
        "bound_port": bound[1],
        "redis_data_dir": redis_data_dir,
    })
    run_command(redis_bin, redis_args)


def main():
    deploy_info = create_deploy_information()
    start_redis_main(deploy_info)


if __name__ == "__main__":
    main()

