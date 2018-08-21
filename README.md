**[开发环境]**

python3 + Django1.11.4 + virtualenv

**[数据库]**

pgsql9.6 + redis(可选)

启动 pgsql 和 redis

进入 pgsql 命令行模式， psql blog

将系统用户添加为数据库用户

CREATE ROLE xxx WITH LOGIN SUPERUSER; // xxx是当前用户名

启用 HStore 插件

CREATE EXTENSION IF NOT EXISTS hstore;

**[安装 python 相关库]**

进入项目根目录， 创建虚拟环境

pip3 install virtualenv

virtualenv -p python3.6 env

. ./env/bin/activate

pip install -r requirements.txt

**[执行数据库迁移文件]**

激活虚拟环境，

./manage.py migrate

**[本地运行]**

./manage.py runserver

在浏览器输入 127.0.0.1:8000即可访问

**[同步本地文件到服务器]**

进入本地项目根目录， 激活虚拟环境

./sync_to_server 187


**[nginx 部署]**

在 /etc/nginx/conf.d

sudo ln -s /home/zjp/waterlawblog/etc/nginx/conf/blog_187.conf /etc/nginx/conf.d/blog_187.conf

重启 nginx

nginx -s reload

进入服务器项目根目录， 激活虚拟环境
创建 product.txt 文件， 写入服务器的 ip
创建 email.txt 文件， 写入 163 邮箱的授权码

./manage.py runserver

访问 [waterlaw.top](https://waterlaw.top/)