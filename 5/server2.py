#!/usr/bin/python
import socket
import json
import sys 
import stomp
import pymysql
import time

Endpoint = "testdb.cels5fzv2nsr.ap-northeast-1.rds.amazonaws.com"
con = pymysql.Connect(host=Endpoint,port=3306,user="testname",passwd=":PvJt:tL2P7T!Du",db="testdb")
c = con.cursor()

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

host = sys.argv[1] 
port = int(sys.argv[2])
server = socket.socket()
server.bind((host,port))
#server.bind(('127.0.0.1',8006))
server.listen(5) 
print('start listen')

com=["exit","post","receive-post","invite","list-invite",
     "accept-invite","list-friend","send-group","join-group",
     "list-joined","list-group","create-group","send"]
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
        if arg_list[0] == "invite" :#ok
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
        elif arg_list[0] == "send-group" :
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
    data = json.dumps(data)
    print(data)
    data = data.encode()
    conn.send(data)
    
    con.commit()

  