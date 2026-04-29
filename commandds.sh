docker run -d --name mysql-db  -e MYSQL_ROOT_PASSWORD=root -e MYSQL_DATABASE=cloud -p 3306:3306 mysql:8 --default-authentication-plugin=mysql_native_password

docker run -d --name python-demo-flask-app -p 5000:5000 --link mysql-db:mysql -e DB_HOST=mysql -e DB_USER=root -e DB_PASSWORD=root -e DB_NAME=cloud liteshz/python-demo-flask-app
