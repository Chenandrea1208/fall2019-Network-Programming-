#!/usr/bin/python
import socket
import json
import sys 
import stomp
import pymysql
import boto3
import time

ec2 = boto3.resource('ec2')
#con = sqlite3.connect('HW4.db')
Endpoint = "testdb.cels5fzv2nsr.ap-northeast-1.rds.amazonaws.com"
con = pymysql.Connect(host=Endpoint,port=3306,user="testname",passwd=":PvJt:tL2P7T!Du",db="testdb")
#print "Opened database successfully";
c = con.cursor()

def search_ip(ins_id):
  ins_ip = None
  while (ins_ip == None):
    collection = ec2.instances.filter(InstanceIds = [ins_id])
    for col in collection:
      ins_ip = col.public_ip_address
      #print('inside ip :')
      #print(ins_ip)
    time.sleep(5)
  return ins_ip  

def create():  
  user_data = """#!/bin/bash
pip install stomp.py
pip install pymysql
python /home/ubuntu/server2.py 0.0.0.0 8888
"""
  # create a new EC2 instance
  new = ec2.create_instances(
      ImageId='ami-0aa6b2b9e9d8f903f',
      MinCount=1,
      MaxCount=1,
      InstanceType='t2.micro',
      KeyName='ec2-keypair',
      UserData=user_data
  )
  res=search_ip(new[0].id)
  val=(new[0].id,res,1)
  c.execute('INSERT INTO ec2_ip VALUES (%s,%s,%s)', val)
  con.commit()
  time.sleep(30)
  return res

def delete_(ip):
  c.execute('SELECT * FROM ec2_ip WHERE ip = %s ',[ip])
  tmp = c.fetchone()
  if (tmp[2])==1:
    instance = ec2.Instance(tmp[0])
    res = instance.terminate()
    print(res)
    c.execute('DELETE FROM ec2_ip WHERE ip = %s ',[tmp[1]])
  else :
    c.execute('UPDATE ec2_ip SET num = %s WHERE ip = %s ',[tmp[2]-1,ip])
  con.commit()  

def send_to_queue(msg,queue_name):
    conn = stomp.Connection10([('54.249.144.111',61613)])
    conn.start()
    conn.connect()
    conn.send(queue_name, msg)
    conn.disconnect()
 
def send_to_topic(msg,topic_name):
    conn = stomp.Connection10([('54.249.144.111',61613)])
    conn.start()
    conn.connect()
    conn.send(topic_name, msg)
    conn.disconnect()


#id_list = []
#token_dict=dict()

host = sys.argv[1] 
port = int(sys.argv[2])
server = socket.socket()
server.bind((host,port))
#server.bind(('127.0.0.1',8006))
server.listen(5) 
print('start listen')

com=["exit","register","login","post","receive-post","delete","logout",
     "invite","list-invite","accept-invite","list-friend","send-group",
     "join-group","list-joined","list-group","create-group","send"]
while True:
    conn,addr = server.accept()
    arg = conn.recv(1024)
    
    #print('recv:',arg)
    if not arg:
      #print('client has lost....')
      break
    arg = arg.decode()  
    arg = arg.replace('\n','')
    arg_list = arg.split()
    if arg_list[0] not in com :
      data = {'status': 1, 'message': "Unknown command "+arg_list[0]}
      continue
################################################################################
    elif arg_list[0] == "register" :#ok
      if len(arg_list) != 3:
        print(len(arg_list))
        print(arg_list)
        data = { 'status': 1, 'message': "Usage: register <username> <password>"}
      else :
        reg = [arg_list[1]]
        c.execute('SELECT ID FROM member where ID = %s',reg)
        result=c.fetchall()        
        if result!=():
          data = { 'status': 1, 'message': arg_list[1]+" is already used"}
        else :
          arg0 = json.dumps({'friend':[], 'invite':[],'post':[],'group':[]})
          reg_5 = [arg_list[1], arg_list[2], arg0]
          c.execute('INSERT INTO member VALUES (%s,%s,%s)',reg_5)
          data = { 'status': 0, 'message': "Success!"}   
    elif arg_list[0] == "login" :#ok
      if len(arg_list) == 3 :
        reg = [arg_list[1],arg_list[2]] 
        c.execute('SELECT * FROM member where ID = %s AND password = %s',reg)
        temp = c.fetchall()
        if temp!=() :
          group=json.loads(temp[0][2])
          group=group['group']
          reg_1 = [arg_list[1]]
          c.execute('SELECT * FROM login where ID = %s ',reg_1)
          tmp = c.fetchall()
          if tmp!=() :
            token=tmp[0][1]
            ip = tmp[0][2]
          else :
            token = str(hash(arg_list[1]))
            c.execute('SELECT * FROM ec2_ip where num = (SELECT max(num) FROM ec2_ip where num < 10)')
            tmp_ip = c.fetchone()
            if tmp_ip == None:
              ip = create()
            else :
              ip = tmp_ip[1]
              num = tmp_ip[2]+1
              c.execute('UPDATE ec2_ip SET num = %s WHERE ip = %s ',[num,ip])
            reg = [arg_list[1],token,ip]
            c.execute('INSERT INTO login VALUES (%s,%s,%s)', reg)
          data = { 'status': 0, 'token': token,'group': group,'message': "Success!",'ip':ip }##notdone
        else :
          data = { 'status': 1, 'message': "No such user or password error" } 
      else :
        data = { 'status': 1, 'message': "Usage: login <id> <password>" }
#########################################################################
    else:
      if len(arg_list)>1:
        reg = [arg_list[1]]
      else:
        reg = " " 
      #print(reg)
      c.execute('SELECT ID FROM login where token = %s ',reg)
      temp = c.fetchall()
      #print(temp)
      if temp==() :
        data = { 'status': 1, 'message': "Not login yet"}
      else:
        temp_id = temp[0][0]
        c.execute('SELECT * FROM member where ID = %s ',[temp_id])
        temp = c.fetchall()
        temp_data = temp[0]
        #print(temp_data)
        temp_data = json.loads(temp_data[2])
        if arg_list[0] == "logout" :#ok      
          if len(arg_list) != 2 :
            data = { 'status': 1, 'message': "Usage: logout <user>"}
          else :
            c.execute('SELECT ip FROM login WHERE ID = %s ',[temp_id])
            tmp = c.fetchone()
            if tmp!=None:
              delete_(tmp)
            c.execute('DELETE FROM login WHERE ID = %s ',[temp_id])
            data = { 'status': 0, 'message': "Bye!"}
        elif arg_list[0] == "invite" :#ok
          if len(arg_list) == 3: 
            c.execute('SELECT * FROM member where ID = %s ',[arg_list[2]])
            temp = c.fetchall()
            if temp_id == arg_list[2] :
              data = { 'status': 1, 'message': "You cannot invite yourself"}
            elif temp==() :
              data = { 'status': 1, 'message': arg_list[2]+" does not exist"}
            else :
              temp_invite = temp[0]
              print(temp_invite)
              temp_list = temp_invite[2]
              temp_list = json.loads(temp_list)
              if arg_list[2] in temp_data['friend'] :
                data = { 'status': 1, 'message': arg_list[2]+" is already your friend"}
              elif arg_list[2] in temp_data['invite'] :
                data = { 'status': 1, 'message': arg_list[2]+" has invited you"}
              elif temp_id in temp_list['invite'] :
                data = { 'status': 1, 'message': "Already invited"}
              else :
                temp_list['invite'].append(temp_id)
                temp_list = json.dumps(temp_list)
                c.execute('UPDATE member SET data = %s WHERE ID = %s',[temp_list,arg_list[2]])
                data = { 'status': 0, 'message': "Success!"}                                     
          else :
            data = { 'status': 1, 'message': "Usage: invite <user> <id>"}
        elif arg_list[0] == "accept-invite" :#ok 
          if len(arg_list) != 3 :
            data = { 'status': 1, 'message': "Usage: accept-invite <user> <id>"}
          else :
            if arg_list[2] in temp_data['invite'] :
              c.execute('SELECT * FROM member where ID = %s ',[arg_list[2]])
              temp = c.fetchall()
              temp_invite = temp[0]
              print(temp_invite)
              temp_list = temp_invite[2]
              temp_list = json.loads(temp_list)              
              temp_data['friend'].append(arg_list[2])
              temp_data['invite'].remove(arg_list[2])
              temp_list['friend'].append(temp_id)

              temp_list = json.dumps(temp_list)
              temp_data = json.dumps(temp_data)
              c.execute('UPDATE member SET data = %s WHERE ID = %s',[temp_data,temp_id])
              c.execute('UPDATE member SET data = %s WHERE ID = %s',[temp_list,arg_list[2]])
              data = { 'status': 0, 'message': "Success!"}
            else :
              data = { 'status': 1, 'message': arg_list[2]+" did not invite you"}    
        elif arg_list[0] == "post" :     
          if len(arg_list) > 2 :
            message = " ".join(arg_list[2:])
            post_data = {'id': temp_id, 'message': message}
            for tmp in temp_data['friend'] :
              c.execute('SELECT * FROM member where ID = %s ',[tmp])
              temp = c.fetchone()
              if temp != None:
                temp_list = json.loads(temp[2])
                temp_list['post'].append(post_data)
                temp_list = json.dumps(temp_list)
                c.execute('UPDATE member SET data = %s WHERE ID = %s',[temp_list,tmp])
            data = { 'status': 0, 'message': "Success!"}     
          else :
            data = { 'status': 1, 'message': "Usage: post <user> <message>"}   
        elif arg_list[0] == "list-invite" :
          if len(arg_list) != 2 :
            data = { 'status': 1, 'message': "Usage: list-invite <user>"}
          else :
            list_invite = temp_data['invite']
            data = { 'status': 0, 'invite': list_invite}
        elif arg_list[0] == "list-friend" :
          if len(arg_list) != 2 :
            data = { 'status': 1, 'message': "Usage: list-friend <user>"}
          else :
            list_friend = temp_data['friend']
            data = { 'status': 0, 'friend': list_friend}     
        elif arg_list[0] == "receive-post" :
          if len(arg_list) != 2 :
            data = { 'status': 1, 'message': "Usage: receive-post <user>"}
          else :
            post = temp_data['post']
            data = { 'status': 0, 'post': post}
        elif arg_list[0] == "send" :     
          if len(arg_list) > 3 :
            message = " ".join(arg_list[3:])
            post_data = {'id': temp_id, 'message': message}
            c.execute('SELECT ID FROM member where ID = %s ', [arg_list[2]])
            mem_tmp = c.fetchall()
            c.execute('SELECT ID FROM login where ID = %s ', [arg_list[2]])
            log_tmp = c.fetchall()
            if mem_tmp ==() :
              data = { 'status': 1, 'message': "No such user exist"}  
            elif arg_list[2] not in temp_data['friend'] :
              data = { 'status': 1, 'message': arg_list[2]+" is not your friend"}
            elif log_tmp ==():
              data = { 'status': 1, 'message': arg_list[2]+" is not online"}
            else :    
              message = " ".join(arg_list[3:])
              msg = '<<<'+temp_id+'->'+arg_list[2]+':'+message+'>>>'
              queue_name = '/queue/'+arg_list[2]
              send_to_queue(msg,queue_name)
              data = { 'status': 0, 'message': "Success!"}
          else :
            data = { 'status': 1, 'message': "Usage: send <user> <friend> <message>"}   
        elif arg_list[0] == "create-group" :
          if len(arg_list) == 3:
            c.execute('SELECT groupID FROM group_table where groupID = %s',[arg_list[2]])
            tmp = c.fetchall()
            if tmp!=() :
              data = { 'status': 1, 'message': arg_list[2]+" already exist"}
            else:
              group_mem = {'member':[]}
              group_mem['member'].append(temp_id)
              group_mem = json.dumps(group_mem)
              c.execute('INSERT INTO group_table VALUES (%s,%s)', [arg_list[2],group_mem])
              temp_data['group'].append(arg_list[2])
              temp_data = json.dumps(temp_data)
              c.execute('UPDATE member SET data = %s WHERE ID = %s',[temp_data,temp_id])
              data = { 'status': 0, 'message': "Success!"}  
          else :
            data = { 'status': 1, 'message': "Usage: create-group <user> <group>"}
        elif arg_list[0] == "list-group" :
          if len(arg_list) == 2:
            temp_list = list()
            for tmp in c.execute('SELECT groupID FROM group_table'):
              temp_list.append(tmp[0])
            if len(temp_list) == 0 :
              data = {'status':0, 'message':"No groups"}
            else:  
              data = {'status':0, 'message':temp_list}  
          else:
            data = {'status':1, 'message':"Usage: list-group <user>"}
        elif arg_list[0] == "list-joined" :
          if len(arg_list) == 2:
            temp_list = temp_data['group']
            if len(temp_list) == 0 :
              data = {'status':0, 'message':"No groups"}
            else:  
              data = {'status':0, 'message':temp_list}  
          else:
            data = {'status':1, 'message':"Usage: list-joined <user>"}
        elif arg_list[0] == "join-group" :
          if len(arg_list) == 3:
            c.execute('SELECT groupID FROM group_table where groupID = %s',[arg_list[2]])
            tmp = c.fetchall()
            if tmp==() :
              print(arg_list[2])
              data = {'status':1, 'message':arg_list[2]+" does not exist"}
            elif arg_list[2] in temp_data['group']:
              data = {'status':1, 'message':"Already a member of "+arg_list[2]}   
            else :
              c.execute('SELECT * FROM group_table where groupID = %s ',[arg_list[2]])
              temp = c.fetchall()
              group_mem = temp[0][1]
              group_mem = json.loads(group_mem)
              group_mem['member'].append(temp_id)
              group_mem = json.dumps(group_mem)
              c.execute('UPDATE group_table SET member_id = %s WHERE groupID = %s',[group_mem ,arg_list[2]])
              
              temp_data['group'].append(arg_list[2])
              temp_data = json.dumps(temp_data)
              c.execute('UPDATE member SET data = %s WHERE ID = %s',[temp_data,temp_id])  
              data = {'status':0, 'message': "Success!" }
          else:
            data = {'status':1, 'message':"Usage: join-group <token> <group>"}       
        elif arg_list[0] == "send-group" :###############################
          if len(arg_list) > 3:
            c.execute('SELECT groupID FROM group_table where groupID = %s',[arg_list[2]])
            tmp = c.fetchall()
            if tmp==() :
              data = {'status':1, 'message':"No such group exist"}
            elif arg_list[2] not in temp_data['group']:
              data = {'status':1, 'message':"You are not the member of "+arg_list[2]}   
            else :
              message = " ".join(arg_list[3:])
              msg = '<<<'+temp_id+'->GROUP<'+arg_list[2]+'>:'+message+'>>>'
              topic_name = '/topic/'+arg_list[2]
              send_to_topic(msg,topic_name)
              data = {'status':0, 'message': "Success!" }
          else:
            data = {'status':1, 'message':"Usage: send-group <token> <group> <message>"}
        elif arg_list[0] == "delete":
          if len(arg_list) != 2 :
            data = { 'status': 1, 'message': "Usage: delete <user>"}
          else:
            #ec2
            c.execute('SELECT ip FROM login WHERE ID = %s ',[temp_id])
            tmp = c.fetchone()
            if tmp!=None:
              delete_(tmp)
            #
            c.execute('DELETE FROM login WHERE ID = %s ',[temp_id])
            c.execute('SELECT data FROM member')
            tmp = c.fetchall()
            for i in tmp:
              print(i)
              temp_list = json.loads(i[0])
              if temp_id in temp_list['friend']:
                temp_list['friend'].remove(temp_id)
              if temp_id in temp_list['invite']:
                temp_list['invite'].remove(temp_id)
              for ii in temp_list['post']:
                if temp_id == ii['id']:
                  temp_list['post'].remove(ii)
              temp_list = json.dumps(temp_list)
              c.execute('UPDATE member SET data = %s WHERE ID = %s',[temp_list,i[0]])
            for i in temp_data['group']:
              c.execute('SELECT member_id FROM group_table where groupID = %s', [i])
              temp = c.fetchall()
              temp_group = temp[0]
              temp_group = json.dumps(temp_group)
              temp_group['member'].remove(temp_id)
              c.execute('UPDATE group_table SET member_id where groupID = %s', [i])
            data = { 'status': 0, 'message': "Success!"}
            c.execute('DELETE FROM member WHERE ID = %s ',[temp_id])                                
#########################################################################
    data = json.dumps(data)
    print(data)
    data = data.encode()
    conn.send(data)
    
    con.commit()

  