# pip install mysql-connector-python
import mysql.connector

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    # user="weblesimdbuser",
    passwd="hejsan123"
)

my_cursor = mydb.cursor()

my_cursor.execute("CREATE DATABASE db_weblesim")

my_cursor.execute("SHOW DATABASES")

for db in my_cursor:
    print(db)
