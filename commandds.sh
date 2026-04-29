docker network create my-network

docker run -d --name mysql-db --network my-network -e MYSQL_ROOT_PASSWORD=root -e MYSQL_DATABASE=cloud -p 3306:3306 mysql:8.4

docker run -d --name python-demo-flask-app --network my-network -p 5000:5000 --link mysql-db:mysql -e DB_HOST=mysql -e DB_USER=root -e DB_PASSWORD=root -e DB_NAME=cloud liteshz/python-demo-flask-app
