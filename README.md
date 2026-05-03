# demo_python_flask_app
This repo contains files related to python-demo-flask-app

# docker image registry
https://hub.docker.com/repository/docker/liteshz/python-demo-flask-app/tags

# Output Screen
<img width="2794" height="1624" alt="image" src="https://github.com/user-attachments/assets/fb1694db-c7ac-490d-8cfa-056af5c727e3" />
<br>
<img width="2796" height="1622" alt="image" src="https://github.com/user-attachments/assets/4c7ebf0b-eec7-4492-8a09-e1de5845e8db" />

------------------------------------------

# Configure mysqld on localhost
sudo apt install -y mysql-server<br>
sudo systemctl start mysql<br>
sudo systemctl enable mysql<br>

------------------------------------------

sudo mysql


CREATE DATABASE cloud;

CREATE USER 'flaskuser'@'localhost' IDENTIFIED BY 'flaskpass';

GRANT ALL PRIVILEGES ON cloud.* TO 'flaskuser'@'localhost';

FLUSH PRIVILEGES;

------------------------------------------

Change this in your app:

conn = pymysql.connect(
    host="localhost",
    user="flaskuser",
    password="flaskpass",
    db="cloud",
    port=3306
)

------------------------------------------

sudo mysql

ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'root';
FLUSH PRIVILEGES;

------------------------------------------

export DB_HOST=localhost
export DB_USER=flaskuser
export DB_PASSWORD=flaskpass
export DB_NAME=cloud

------------------------------------------

mysql -u flaskuser -p cloud < init.sql

------------------------------------------

python app.py

Running on http://0.0.0.0:5000

------------------------------------------
