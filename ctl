#!/usr/bin/env python
# -*- coding:utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import
from __future__ import division

import io
import sys

import os
import argparse
import logging
import time
from etc.deploy import create_deploy_information

if sys.version_info[0] == 3:
    import builtins
else:
    import __builtin__ as builtins


def hack_python_interpreter():
    python_path = ""
    # XXX No Microsoft Windows!
    if os.path.exists("../pysp/bin/python"):
        python_path = os.path.abspath("../pysp/bin/python")
    elif os.path.exists("pysp/bin/python"):
        python_path = os.path.abspath("pysp/bin/python")
    if not python_path or sys.executable == python_path:
        activate_this = os.path.join(os.path.dirname(python_path), "activate_this.py")
        if os.path.isfile(activate_this):
            if sys.version_info[0] < 3:
                getattr(builtins, "execfile")(activate_this, {'__file__': activate_this})
            else:
                with io.open(activate_this, "r", encoding = "utf-8") as f:
                    getattr(builtins, "exec")(f.read(), {'__file__': activate_this})
    else:
        args = [python_path]
        args.extend(sys.argv)
        os.execv(python_path, args)


def hack_docker(deploy_info, copoment_name):
    if not os.path.exists("/usr/bin/docker"):
        print("in docker")
        return
    docker_image = deploy_info.get_docker_image(copoment_name)
    if not docker_image:
        print("no docker image")
        return

    interpret = "-ti" if sys.stdout.isatty() else "-i"
    args = [
        "/usr/bin/docker", "run", interpret, "--rm",
        "--net", "host",
        "-v", "/etc/localtime:/etc/localtime:ro",
        "-v", "{0}:{0}".format(deploy_info.base_dir),
    ]
    for k, v in deploy_info.docker_vpaths.items():
        args.extend(["-v", "{}:{}".format(k, v)])
    args.extend([
        "-w", deploy_info.base_dir,
        docker_image, __file__
    ])
    args.extend(sys.argv[1:])
    os.execv(args[0], args)


def touchall(cwd = "."):
    for root, dirs, filenames in os.walk(cwd):
        for filename in filenames:
            path = os.path.join(root, filename)
            print("update {} modification time.".format(path))
            os.utime(path, None)


def start_celery():
    os.environ["C_FORCE_ROOT"] = "1"
    command = "celery worker -A sites.celery -B -l INFO"
    os.system(command)


def say_hello():
    print("hello, world!")
    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            return


def run_bash():
    bash = "/bin/bash"
    os.execv(bash, [bash])


def main():
    parser = argparse.ArgumentParser(description = 'sites services controller.')
    parser.add_argument("command", help = "command to run.")
    parser.add_argument("--debug", "-d", action = "store_true", help = "print debug info.")
    parser.add_argument("-c", action = "store_true", help = "check compoment to start.")
    parser.add_argument("--docker", help = "run in docker.")
    options = parser.parse_args()
    deploy_info = create_deploy_information()
    if options.debug:
        logging.basicConfig(level = logging.DEBUG)
    if options.c:
        if options.command not in deploy_info.components:
            print("component {} will not start in this machine. available copoments: {}".format(
                options.command, ", ".join(deploy_info.components)))
            say_hello()
            return 0
        else:
            hack_docker(deploy_info, options.command)
    elif options.docker:
        hack_docker(deploy_info, options.docker)
    if options.command == "setup":
        from etc.setup import main as command_main
    elif options.command == "mddb":
        from etc.start_mddb import main as command_main
    elif options.command == "redis":
        from etc.start_redis import main as command_main
    elif options.command == "touch_all":
        command_main = touchall
    elif options.command == "celery":
        command_main = start_celery
    elif options.command == "say_hello":
        command_main = say_hello
    elif options.command == "pgsql":
        from etc.start_pgsql import main as command_main
    elif options.command == "gunicorn":
        from etc.run_gunicorn import main as command_main
    elif options.command == "bash" or options.command == "test":
        hack_docker(deploy_info, "gunicorn")
        command_main = run_bash
    elif options.command == "pgbash":
        hack_docker(deploy_info, "pgsql")
        command_main = run_bash
    else:
        parser.print_usage()
        return 2
    command_main()
    return 0

if __name__ == "__main__":
    hack_python_interpreter()
    sys.exit(main())
