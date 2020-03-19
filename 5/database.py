#!/usr/bin/python

#import sqlite3
import pymysql

#conn = sqlite3.connect('HW4.db')
Endpoint = "testdb.cels5fzv2nsr.ap-northeast-1.rds.amazonaws.com"
db = pymysql.Connect(host=Endpoint,port=3306,user="testname",passwd=":PvJt:tL2P7T!Du",db="testdb")
print ("Opened database successfully");
#c = conn.cursor()
c = db.cursor()

c.execute("CREATE TABLE member (ID VARCHAR(255) PRIMARY KEY, password VARCHAR(255), data VARCHAR(4096))")
c.execute("CREATE TABLE group_table (groupID VARCHAR(255) PRIMARY KEY, member_id VARCHAR(4096))") 
c.execute("CREATE TABLE login (ID VARCHAR(255) PRIMARY KEY, token VARCHAR(255), ip VARCHAR(255))")
c.execute("CREATE TABLE ec2_ip (ID VARCHAR(255) PRIMARY KEY, ip VARCHAR(255), num INT)")

print ("Table created successfully");
db.commit()
db.close()
#conn.commit()
#conn.close()