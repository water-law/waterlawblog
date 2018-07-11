from fabric.api import env, run
from fabric.operations import sudo


SSH_REPO = 'ssh://zjp@waterlaw.cn//home/zjp/waterlawblog'

env.user = 'zjp'
env.hosts = ['waterlaw.cn']
env.port = '22'


def deploy():
    source_folder = '/home/zjp/waterlawblog'

    run('cd %s && hg update' % source_folder)
    run("""
        cd {} &&
        ./env/bin/pip install -r requirements.txt &&
        ./env/bin/python3 manage.py collectstatic --noinput &&
        ./env/bin/python3 manage.py rebuild_index &&
        ./env/bin/python3 manage.py migrate &&
        ./env/bin/gunicorn --bind unix:/tmp/waterlaw.cn.socket sites.wsgi:application
        """.format(source_folder))
    # sudo('restart gunicorn-waterlaw.cn')
    sudo('service nginx reload')