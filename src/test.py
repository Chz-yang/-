#!/usr/bin/python3
#!encoding=utf-8

# import pyodbc

# conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=127.0.0.1;port=1433;DATABASE=TakeOut;UID=sa;PWD=Yy7758258')

# cursor = conn.cursor()
# cursor.execute("SELECT * FROM Supplier")
# row = cursor.fetchall()
# if row:
#     print(row)

import pymssql

conn = pymssql.connect(host='localhost',user='sa',password='Yy7758258',database='master',charset='utf-8')

cur = conn.cursor()
cur.execute("SELECT * FROM Orders")
res_list = cur.fetchall()
print(res_list[0:10])
conn.commit()
conn.close()
