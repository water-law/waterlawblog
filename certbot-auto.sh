#! /bin/bash -l
set -e
if command -v wget >/dev/null 2>&1; then
  :
else
  echo "the command 'wget' not exists"
  echo "try to install 'wget', please wait..."
  apt install wget
fi

# 获取证书生成工具 certbot
certbot_auto_file="certbot-auto"

if [ ! -x "$certbot_auto_file"]; then
  wget https://dl.eff.org/certbot-auto
fi

chmod a+x certbot-auto

# 获取证书
email="1301144569@qq.com"
domain="waterlaw.top"
./certbot-auto certonly  -d $domain -d *.$domain -m $email --manual --preferred-challenges dns --server https://acme-v02.api.letsencrypt.org/directory

# 使用上一步生成的字符串在域名解析中添加一条 TXT 类型的名为 _acme-challenge.域名 的主机记录

# reload nginx
if command -v nginx >/dev/null 2>&1; then
  echo "'nginx' dosen't exists."
else
  :
#  nginx -s reload
fi
