#!/bin/bash
# 输入参数
DEBUG=0
DB_ENGINE=mysql
DB_HOST=127.0.0.1
DB_PORT=3306
DB_ROOT_PASSWD=weakPassword
DB_NAME=jumpserver
DB_USER=jumpserver
DB_PASSWORD=weakPassword

SECRET_KEY=`cat /proc/sys/kernel/random/uuid | base64`

# 环境配置
echo "***** 修改系统字符集 *****"
export LC_ALL=zh_CN.UTF-8
export AUTOENV_ASSUME_YES=1
localedef -c -f UTF-8 -i zh_CN zh_CN.UTF-8
echo 'LANG="zh_CN.UTF-8"' > /etc/locale.conf

echo ""
echo "***** 修改yum源与安装依赖包 *****"
yum install -y epel-release
# rm -f /etc/yum.repos.d/*.repo
# wget mirror.t.com/home.repo -O /etc/yum.repos.d/home.repo
yum clean all
yum install -y python36 python36-devel wget MariaDB MariaDB-devel MariaDB-server MariaDB-shared redis python-pip krb5-devel openssl-devel expect nginx
yum groupinstall "Development Tools" -y

echo ""
echo "***** 建立py3虚拟环境 *****"
cd /opt
python3.6 -m venv py3
# source /opt/py3/bin/activate

echo ""
echo "***** 配置自动进入py3虚拟环境 *****"
git clone https://github.com/kennethreitz/autoenv.git
echo 'source /opt/autoenv/activate.sh' >> ~/.bashrc
# source ~/.bashrc

echo ""
echo "***** 克隆jumpserver到本地 *****"
git clone https://github.com/jumpserver/jumpserver.git
echo "source /opt/py3/bin/activate" > /opt/jumpserver/.env
source /opt/py3/bin/activate

echo ""
echo "***** 安装rpm依赖包 *****"
cd /opt/jumpserver/requirements
yum -y install $(cat ./rpm_requirements.txt)

echo ""
echo "***** 安装py3依赖包 *****"
#pip install pip -U
#pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
pip install --upgrade pip setuptools
pip install -r ./requirements.txt

echo ""
echo "***** 启动redis *****"
systemctl enable redis
systemctl start redis

echo ""
echo "***** 启动mariadb *****"
systemctl enable mariadb
systemctl start mariadb

echo ""
echo "***** 初始化mariadb *****"
MARIADB_SECURE_INSTALL=$(expect -c "
  set timeout 10
  spawn mysql_secure_installation

  expect \"Enter current password for root (enter for none):\"
  send \"\r\"

  expect \"root password?\"
  send \"y\r\"

  expect \"New password:\"
  send \"$DB_ROOT_PASSWD\r\"

  expect \"Re-enter new password:\"
  send \"$DB_ROOT_PASSWD\r\"

  expect \"Remove anonymous users?\"
  send \"y\r\"

  expect \"Disallow root login remotely?\"
  send \"y\r\"

  expect \"Remove test database and access to it?\"
  send \"y\r\"

  expect \"Reload privilege tables now?\"
  send \"y\r\"

  expect eof
")
echo "$MARIADB_SECURE_INSTALL"

echo ""
echo "***** 创建数据库 *****"
mysql -uroot -p"$DB_ROOT_PASSWD" --default-character-set=utf8 -e "create database $DB_NAME default charset 'utf8';"
mysql -uroot -p"$DB_ROOT_PASSWD" --default-character-set=utf8 -e "grant all on $DB_NAME.* to '$DB_USER'@'127.0.0.1' identified by '$DB_PASSWORD';"
mysql -uroot -p"$DB_ROOT_PASSWD" --default-character-set=utf8 -e "flush privileges;"

echo ""
echo "***** 修改jumpserver配置文件 *****"
cp /opt/jumpserver/config_example.py /opt/jumpserver/config.py

# 生成加密盐
export SECRET_KEY=$SECRET_KEY
echo "SECRET_KEY=$SECRET_KEY" >> ~/.bashrc

if [ "$DEBUG" = "0" ] ; then
	export "DEBUG=False"
	echo "DEBUG=False" >> ~/.bashrc
fi

if [ "$DB_ENGINE" = "mysql" ] ; then
	sed -i "s/DB_ENGINE = 'sqlite3'/# DB_ENGINE = 'sqlite3'/g" /opt/jumpserver/config.py
	sed -i "s/DB_NAME =.*db.sqlite3')/# DB_NAME = os.path.join(BASE_DIR, 'data', 'db.sqlite3')/g" /opt/jumpserver/config.py
	sed -i "s/# DB_ENGINE =.*mysql'/DB_ENGINE = 'mysql'/g" /opt/jumpserver/config.py
	sed -i "s/# DB_HOST =.*/DB_HOST ='$DB_HOST'/g" /opt/jumpserver/config.py
	sed -i "s/# DB_PORT =.*/DB_PORT ='$DB_PORT'/g" /opt/jumpserver/config.py
	sed -i "s/# DB_USER =.*/DB_USER ='$DB_USER'/g" /opt/jumpserver/config.py
	sed -i "s/# DB_PASSWORD =.*/DB_PASSWORD ='$DB_PASSWORD'/g" /opt/jumpserver/config.py
	sed -i "s/# DB_NAME =.*jumpserver'/DB_NAME ='$DB_NAME'/g" /opt/jumpserver/config.py

	#export "DB_ENGINE=mysql"
	#echo "DB_ENGINE=mysql" >> ~/.bashrc
	#export "DB_HOST=$DB_HOST"
	#echo "DB_HOST=$DB_HOST" >> ~/.bashrc
	#export "DB_PORT=$DB_PORT"
	#echo "DB_PORT=$DB_PORT" >> ~/.bashrc
	#export "DB_USER=$DB_USER"
	#echo "DB_USER=$DB_USER" >> ~/.bashrc
	#export "DB_PASSWORD=$DB_PASSWORD"
	#echo "DB_PASSWORD=$DB_PASSWORD" >> ~/.bashrc
	#export "DB_NAME=$DB_NAME"
	#echo "DB_NAME=$DB_NAME" >> ~/.bashrc
fi

echo ""
echo "***** 建立jumpserver数据库结构 *****"
sh /opt/jumpserver/utils/make_migrations.sh

echo ""
echo "***** 启动jumpserver *****"
/opt/jumpserver/jms start all -d

# coco
cd /opt
git clone https://github.com/jumpserver/coco.git
echo "source /opt/py3/bin/activate" > /opt/coco/.env
yum -y  install $(cat ./coco/requirements/rpm_requirements.txt)
pip install -r ./coco/requirements/requirements.txt
mkdir /opt/coco/keys /opt/coco/logs
cp /opt/coco/conf_example.py /opt/coco/conf.py
/opt/coco/cocod start -d

# Web Terminal
wget https://github.com/jumpserver/luna/releases/download/v1.4.4/luna.tar.gz
tar xvf luna.tar.gz
chown -R root:root luna

# windows 组件
rpm --import http://li.nux.ro/download/nux/RPM-GPG-KEY-nux.ro
rpm -Uvh http://li.nux.ro/download/nux/dextop/el7/x86_64/nux-dextop-release-0-5.el7.nux.noarch.rpm
yum -y localinstall --nogpgcheck https://download1.rpmfusion.org/free/el/rpmfusion-free-release-7.noarch.rpm \
  https://download1.rpmfusion.org/nonfree/el/rpmfusion-nonfree-release-7.noarch.rpm
yum install -y --nogpgcheck java-1.8.0-openjdk libtool cairo-devel libjpeg-turbo-devel libpng-devel uuid-devel ffmpeg-devel \
  freerdp-devel pango-devel libssh2-devel libtelnet-devel libvncserver-devel pulseaudio-libs-devel openssl-devel libvorbis-devel libwebp-devel ghostscript

ln -s /usr/local/lib/freerdp/guacsnd.so /usr/lib64/freerdp/
ln -s /usr/local/lib/freerdp/guacdr.so /usr/lib64/freerdp/
ln -s /usr/local/lib/freerdp/guacai.so /usr/lib64/freerdp/
ln -s /usr/local/lib/freerdp/guacsvc.so /usr/lib64/freerdp/

# guacamole
git clone https://github.com/jumpserver/docker-guacamole.git
cd /opt/docker-guacamole/
tar -xf guacamole-server-0.9.14.tar.gz
cd guacamole-server-0.9.14
autoreconf -fi
./configure --with-init-dir=/etc/init.d
make && make install
cd ..
# rm -rf guacamole-server-0.9.14
ldconfig

# Tomcat
mkdir -p /config/guacamole /config/guacamole/lib /config/guacamole/extensions
cp /opt/docker-guacamole/guacamole-auth-jumpserver-0.9.14.jar /config/guacamole/extensions/guacamole-auth-jumpserver-0.9.14.jar
# guacamole 配置文件
cp /opt/docker-guacamole/root/app/guacamole/guacamole.properties /config/guacamole/
cd /config
wget http://mirror.bit.edu.cn/apache/tomcat/tomcat-8/v8.5.35/bin/apache-tomcat-8.5.35.tar.gz
tar xf apache-tomcat-8.5.35.tar.gz
rm -rf apache-tomcat-8.5.35.tar.gz
mv apache-tomcat-8.5.35 tomcat8
rm -rf /config/tomcat8/webapps/*
# guacamole client
cp /opt/docker-guacamole/guacamole-0.9.14.war /config/tomcat8/webapps/ROOT.war
# 修改默认端口为 8081
sed -i 's/Connector port="8080"/Connector port="8081"/g' `grep 'Connector port="8080"' -rl /config/tomcat8/conf/server.xml`
# 修改 log 等级为 WARNING
sed -i 's/FINE/WARNING/g' `grep 'FINE' -rl /config/tomcat8/conf/logging.properties`

cd /config
wget https://github.com/ibuler/ssh-forward/releases/download/v0.0.5/linux-amd64.tar.gz
tar xf linux-amd64.tar.gz -C /bin/
chmod +x /bin/ssh-forward

# http://127.0.0.1:8080 指 jumpserver 访问地址
export JUMPSERVER_SERVER=http://127.0.0.1:8080
echo "export JUMPSERVER_SERVER=http://127.0.0.1:8080" >> ~/.bashrc
export JUMPSERVER_KEY_DIR=/config/guacamole/keys
echo "export JUMPSERVER_KEY_DIR=/config/guacamole/keys" >> ~/.bashrc
export GUACAMOLE_HOME=/config/guacamole
echo "export GUACAMOLE_HOME=/config/guacamole" >> ~/.bashrc

/etc/init.d/guacd start
sh /config/tomcat8/bin/startup.sh

# nginx
rm -f /etc/nginx/nginx.conf
cat << EOT >> /etc/nginx/nginx.conf
user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log;
pid /run/nginx.pid;

include /usr/share/nginx/modules/*.conf;

events {
    worker_connections 1024;
}

http {
    log_format  main  '\$remote_addr - \$remote_user [\$time_local] "\$request" '
                      '\$status \$body_bytes_sent "\$http_referer" '
                      '"\$http_user_agent" "\$http_x_forwarded_for"';

    access_log  /var/log/nginx/access.log  main;

    sendfile            on;
    tcp_nopush          on;
    tcp_nodelay         on;
    keepalive_timeout   65;
    types_hash_max_size 2048;

    include             /etc/nginx/mime.types;
    default_type        application/octet-stream;

    include /etc/nginx/conf.d/*.conf;
}
EOT

cat << EOT >> /etc/nginx/conf.d/jumpserver.conf
server {
    listen 80;
    server_name default_server;

    client_max_body_size 100m;

    location /luna/ {
        try_files \$uri / /index.html;
        alias /opt/luna/;
    }

    location /media/ {
        add_header Content-Encoding gzip;
        root /opt/jumpserver/data/;
    }

    location /static/ {
        root /opt/jumpserver/data/;
    }

    location /socket.io/ {
        proxy_pass       http://localhost:5000/socket.io/;
        proxy_buffering off;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header Host \$host;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        access_log off;
    }

    location /coco/ {
        proxy_pass       http://localhost:5000/coco/;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header Host \$host;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        access_log off;
    }

    location /guacamole/ {
        proxy_pass       http://localhost:8081/;
        proxy_buffering off;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection \$http_connection;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header Host \$host;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        access_log off;
    }

    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header Host \$host;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
    }
}
EOT

systemctl enable nginx.service
systemctl start nginx.service
