import pymysql

#conn = sqlite3.connect('HW4.db')
Endpoint = "testdb.cels5fzv2nsr.ap-northeast-1.rds.amazonaws.com"
db = pymysql.Connect(host=Endpoint,port=3306,user="testname",passwd=":PvJt:tL2P7T!Du",db="testdb")
print ("Opened database successfully");
#c = conn.cursor()
c = db.cursor()

c.execute('DROP TABLE IF EXISTS login')
c.execute('DROP TABLE IF EXISTS member')
c.execute('DROP TABLE IF EXISTS group_table')
c.execute('DROP TABLE IF EXISTS ec2_ip')
db.commit()
db.close()
print ("delet TABLE successfully");