### 开发环境

Python3 + Django1.11.4 + virtualenv(虚拟环境)

### 数据库

默认采用 sqlite3 (无需安装，Python3 自带),  您可自行决定采用 pgsql9.6

如下操作在 linux 下您可自行参考:

启动 pgsql 数据库

使用 pgsql 命令行进入 blog 数据库， 

```bash
psql blog
```

将系统用户添加为数据库用户

```bash
CREATE ROLE xxx WITH LOGIN SUPERUSER; # xxx是当前用户名
```

启用 HStore 插件(可选)

```bash
CREATE EXTENSION IF NOT EXISTS hstore;
```

### 安装 Python 相关库

进入项目根目录， 创建虚拟环境

```bash
pip3 install virtualenv

virtualenv -p python3.6 env

. ./env/bin/activate  # Windows 下执行 .\env\Scripts\activate.bat

pip install -r requirements.txt
```

### 执行数据库迁移文件

在虚拟环境下，执行

```bash
python./manage.py makemigrations

python./manage.py migrate
```

### 本地运行

```bash
python ./manage.py runserver
```

在浏览器输入 127.0.0.1:8000即可访问

### 邮件通知

如果你想收到网站异常时的邮件通知，可以在项目根目录下创建 email.txt 文件， 写入 163 邮箱的授权码,  其他邮箱请自行在 sites/settings 中配置

### 收集静态资源(nginx 代理使用)

```bash
python manage.py collectstatic
```

### 同步本地文件到服务器(可选)

进入本地项目根目录， 激活虚拟环境

```bash
./sync_to_server 187  # 187 在 sync_to_server 字典中对应服务器的项目地址
```

### Nginx 部署(可选)

在 /etc/nginx/conf.d

```bash
sudo ln -s /home/zjp/waterlawblog/etc/nginx/conf/blog_187.conf /etc/nginx/conf.d/blog_187.conf
```

重启 nginx

```bash
nginx -s reload
```

进入服务器项目根目录， 激活虚拟环境
创建 product.txt 文件， 写入服务器的 ip

```bash
python ./manage.py runserver
```

访问 [waterlaw.top](https://waterlaw.top)   网站服务器到期了， 没有续费

### 帮助

如果你阅读此文档时仍有疑问，请阅读项目的 [项目 Wiki](https://github.com/water-law/waterlawblog/wiki/项目-wiki) 