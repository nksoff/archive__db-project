# Technopark DB project

## Server prerequisites

1. As `root`:
```
apt-get update
apt-get -y install vim nginx mysql-server mysql-client python python-pip libmysqlclient-dev python-dev git locales curl build-essential libtool
pip install flask flask-runner MySQL-python requests gunicorn

echo 'LANG="ru_RU.UTF-8"' >> /etc/environment

git clone git@github.com:nksoff/db-project.git /var/www
chmod ug+rwx /var/www
chown -R tpadmin:tpadmin /var/www

cp /var/www/conf/locale.gen /etc/locale.gen
locale-gen

cp /var/www/conf/my.cnf /etc/mysql/my.cnf
service mysql restart

rm -rf /etc/nginx/sites-enabled/default

cp /var/www/conf/nginx-host.conf /etc/nginx/sites-enabled
sudo service nginx restart
```

2. Database
Login as `root` in MySQL.
```
mysql -u root -p
```

Execute SQL from `sql/sql.sql`:
```
source /var/www/sql/sql.sql;
```

Fill the database with `dump.sql`:
```
use db;
source /var/www/sql/dump.sql;
```

3. Start server
```
service nginx start
cd /var/www/server && gunicorn -D -b 127.0.0.1:8000 production:app

4. Test
cd
git clone https://github.com/andyudina/technopark-db-api test
sudo cp test/conf/test.conf /usr/local/etc/
cd test/tests
python tests/func_test.py --address=localhost:5000 -l
```
