import mysql.connector

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Heslo123"
)

cursor = mydb.cursor()
cursor.execute("CREATE DATABASE restaurants")
cursor.execute("SHOW DATABASES")
for db in cursor:
    print(db)