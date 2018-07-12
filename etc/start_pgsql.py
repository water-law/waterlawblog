#!/usr/bin/env python
# -*- coding:utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import
from __future__ import division

import os
from etc.deploy import create_deploy_information


def start_pgsql(deploy_info):
    for pgsql_bin in [
        "/usr/pgsql-9.6/bin/postgres",
        "/usr/pgsql-9.5/bin/postgres",
        "/usr/pgsql-9.4/bin/postgres",
        "/usr/pgsql-9.3/bin/postgres",
        "/usr/bin/postgres",
    ]:
        if os.path.exists(pgsql_bin):
            break
    else:
        print("can not find postgres.")
        return
    if os.getuid() == 0:
        args = ["/bin/su", "postgres", "-c", "{} -D {}".format(pgsql_bin, deploy_info.pgsql_path)]
    else:
        args = [pgsql_bin, "-D", deploy_info.pgsql_path]
    os.execv(args[0], args)


def main():
    deploy_info = create_deploy_information()
    start_pgsql(deploy_info)


if __name__ == "__main__":
    main()
