#!/usr/bin/python3
#!encoding=utf-8

import pyodbc

conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=127.0.0.1;port=1433;DATABASE=TPCH;UID=experiment;PWD=Yy7758258')

cursor = conn.cursor()
cursor.execute("SELECT * FROM nation")
row = cursor.fetchall()
if row:
    print(row[0:10])
