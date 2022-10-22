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