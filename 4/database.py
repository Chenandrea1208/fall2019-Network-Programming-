#!/usr/bin/python

import sqlite3

conn = sqlite3.connect('HW4.db')
#print "Opened database successfully";
c = conn.cursor()

c.execute("CREATE TABLE member (ID text primary key, password text, data text)")
c.execute("CREATE TABLE group_table (groupID text primary key, member_id text)") 
c.execute("CREATE TABLE login (ID text primary key, token text)")



#print "Table created successfully";
conn.commit()
conn.close()