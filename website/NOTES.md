How to migrate
--------------

- flask db migrate -m "migrate message"
- (flask db stamp head) if above gives error `ERROR [flask_migrate] Error: Target database is not up to date.` 
- flask db upgrade

SQL
---
- Run "MySQL Shell" (file mysqlsh.exe in C:\Program Files\MySQL\MySQL Shell 8.0\bin)
- \connect mysql://root:hejsan123@localhost/db_weblesim
- If prompt ends with "JS", typs \sql
- Issue sql commands, like
  - show tables;
  - DESCRIBE settings;

MySQL WSL
=========

Install MySQL
-------------
sudo apt update
sudo apt install mysql-server

Start mysql server process 
--------------------------
sudo /etc/init.d/mysql start

or

sudo service mysql start/restart/stop

If "su: warning: cannot change directory to /nonexistent: No such file or directory", do

sudo usermod -d /var/lib/mysql/ mysql

Error "sqlalchemy.exc.OperationalError: (pymysql.err.OperationalError) (1698, "Access denied for user 'root'@'localhost'")":
Follow Option 2 in https://stackoverflow.com/questions/39281594/error-1698-28000-access-denied-for-user-rootlocalhost:

sudo mysql -u root # I had to use "sudo" since it was a new installation

mysql> USE mysql;
mysql> CREATE USER 'markus'@'localhost' IDENTIFIED BY 'YOUR_PASSWD';
mysql> GRANT ALL PRIVILEGES ON *.* TO 'markus'@'localhost';
# mysql> UPDATE user SET plugin='auth_socket' WHERE User='markus';
mysql> FLUSH PRIVILEGES;
mysql> exit;

sudo service mysql restart