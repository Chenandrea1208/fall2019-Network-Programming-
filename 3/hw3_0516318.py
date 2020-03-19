#!/usr/bin/python
import socket
import json
import sys 
import sqlite3

conn = sqlite3.connect('HW4.db')

id_list = []
token_dict=dict()

host = sys.argv[1]
port = sys.argv[2]
server = socket.socket()
server.bind((host,port))
#server.bind(('127.0.0.1',8000))
server.listen(5) 
print('start listen')

com=["exit","register","login","post","receive-post","delete","logout","invite","list-invite","accept-invite","list-friend"]

while True:
  conn,addr = server.accept()
  #print(conn,addr)
  while True:
    arg = conn.recv(1024)
    #print('recv:',arg)
    if not arg:
      #print('client has lost....')
      break
    arg = arg.replace('\n','')
    arg_list = arg.split()
    if arg_list[0] not in com :
      data = {'status': 1, 'message': "Unknown command "+arg_list[0]}
      continue
#######################################
    elif arg_list[0] == "register" :#ok
      if len(arg_list) != 3:
        data = { 'status': 1, 'message': "Usage: register <username> <password>"}
      else :        
        if any(arg_list[1] == temp for temp in c.execute('SELECT ID FROM member')):
          data = { 'status': 1, 'message': arg_list[1]+" is already used"}
        else :
          reg = (arg_list[1], arg_list[2], "{}", "{}", "{}")
          c.execute('INSERT INTO member VALUES (?,?,?,?,?)',reg)
          #key = ['ID', 'password', 'friend', 'invite', 'post']
          #reg = [arg_list[1], arg_list[2], [], [], [], []]
          #id_list.append(dict(zip(key, reg)))
          data = { 'status': 0, 'message': "Success!"}
      #print(id_list)    
    elif arg_list[0] == "login" :#ok
      if len(arg_list) == 3 :
        if any(arg_list[1] == temp['ID'] and arg_list[2] == temp['password']for temp in id_list):          
          token = str(hash(arg_list[1]))
          token_dict[token] = arg_list[1]
          data = { 'status': 0, 'token': token,'message': "Success!"}
        else :
          data = { 'status': 1, 'message': "No such user or password error"}
           
      else :
        data = { 'status': 1, 'message': "Usage: login <id> <password>"}
    
    else:
      if arg_list[1] in c.execute('SELECT token FROM login'):
        if arg_list[0] == "delete" :#ok
          if len(arg_list) == 1:  
            data = { 'status': 1, 'message': "Not login yet"}
          elif len(arg_list) != 2 :
            data = { 'status': 1, 'message': "Usage: delete <user>"}
          elif arg_list[1] in token_dict :
            for temp in id_list :
              if token_dict[arg_list[1]] == temp['ID']:
                id_list.remove(temp)
              if token_dict[arg_list[1]] in temp['invite']:
                temp['invite'].remove(token_dict[arg_list[1]])
              if token_dict[arg_list[1]] in temp['friend']:
                temp['friend'].remove(token_dict[arg_list[1]])
              for i in temp['post'] :
                if token_dict[arg_list[1]] == i['id']:
                  temp['post'].remove(i)
            token_dict.pop(arg_list[1])
            data = { 'status': 0, 'message': "Success!"}         
          else: 
            data = { 'status': 1, 'message': "Not login yet"}
        elif arg_list[0] == "logout" :#ok
          if len(arg_list) == 1:  
            data = { 'status': 1, 'message': "Not login yet"}      
          elif len(arg_list) > 2 :
            data = { 'status': 1, 'message': "Usage: logout <user>"}
          elif arg_list[1] in token_dict :
            token_dict.pop(arg_list[1])
            data = { 'status': 0, 'message': "Bye!"}        
          else :
            data = { 'status': 1, 'message': "Not login yet"}          
        elif arg_list[0] == "invite" :#ok
          if len(arg_list) == 2:  
            data = { 'status': 1, 'message': "Not login yet"}
          elif len(arg_list) == 3 :
            if arg_list[1] in token_dict :          
              if token_dict[arg_list[1]] == arg_list[2] :
                data = { 'status': 1, 'message': "You cannot invite yourself"}
              elif not any( arg_list[2] == temp['ID'] for temp in id_list) :
                data = { 'status': 1, 'message': arg_list[2]+" does not exist"}
              else :
                t = True
                for temp in id_list :
                  if token_dict[arg_list[1]] == temp['ID'] :
                    if arg_list[2] in temp['friend'] :
                      data = { 'status': 1, 'message': arg_list[2]+" is already your friend"}
                      t = False
                    elif arg_list[2] in temp['invite'] :
                      data = { 'status': 1, 'message': arg_list[2]+" has invited you"}
                      t = False
                for temp in id_list :
                  if arg_list[2] == temp['ID'] and t:
                    if token_dict[arg_list[1]] in temp['invite'] :
                      data = { 'status': 1, 'message': "Already invited"}
                    else :
                      temp['invite'].append(token_dict[arg_list[1]])
                      data = { 'status': 0, 'message': "Success!"}           
            else :
              data = { 'status': 1, 'message': "Not login yet"}          
          else :
            data = { 'status': 1, 'message': "Usage: invite <user> <id>"}         
        elif arg_list[0] == "list-invite" :#ok
          if len(arg_list) == 1: 
            data = { 'status': 1, 'message': "Not login yet"}
          elif len(arg_list) != 2 :
            data = { 'status': 1, 'message': "Usage: list-invite <user>"}
          elif arg_list[1] in token_dict:
            temp_id = token_dict[arg_list[1]]
            for temp in id_list :
              if temp_id == temp['ID'] :
                list_invite = temp['invite']
                data = { 'status': 0, 'invite': list_invite}
          else :
            data = { 'status': 1, 'message': "Not login yet"}     
        elif arg_list[0] == "accept-invite" : 
          if len(arg_list) == 2: 
            data = { 'status': 1, 'message': "Not login yet"}
          elif len(arg_list) == 3 :
            if arg_list[1] in token_dict :
              t = False 
              for temp in id_list :
                if token_dict[arg_list[1]] == temp['ID'] : 
                  if arg_list[2] in temp['invite'] :
                    temp['friend'].append(arg_list[2])
                    temp['invite'].remove(arg_list[2])
                    data = { 'status': 0, 'message': "Success!"}
                    t = True
                  else :
                    data = { 'status': 1, 'message': arg_list[2]+" did not invite you"}
              for temp in id_list :
                if arg_list[2] == temp['ID'] and t:
                  temp['friend'].append(token_dict[arg_list[1]])
            else :
              data = { 'status': 1, 'message': "Not login yet"}          
          else :
            data = { 'status': 1, 'message': "Usage: accept-invite <user> <id>"}         
        elif arg_list[0] == "list-friend" :#ok
          if len(arg_list) == 1: 
            data = { 'status': 1, 'message': "Not login yet"}
          elif len(arg_list) != 2 :
            data = { 'status': 1, 'message': "Usage: list-friend <user>"}
          elif arg_list[1] in token_dict:
            temp_id = token_dict[arg_list[1]]
            for temp in id_list :
              if temp_id == temp['ID'] :
                list_friend = temp['friend']
                data = { 'status': 0, 'friend': list_friend}
          else :
            data = { 'status': 1, 'message': "Not login yet"}  
        elif arg_list[0] == "post" :
          if len(arg_list) < 2: 
            data = { 'status': 1, 'message': "Not login yet"}     
          if len(arg_list) > 2 :
            if arg_list[1] in token_dict :
              message = " ".join(arg_list[2:])
              post_data = {'id': token_dict[arg_list[1]], 'message': message}
              for temp in id_list :
                if token_dict[arg_list[1]] in temp['friend'] :
                  temp['post'].append(post_data)
              data = { 'status': 0, 'message': "Success!"}    
            else :
              data = { 'status': 1, 'message': "Not login yet"}    
          else :
            data = { 'status': 1, 'message': "Usage: post <user> <message>"}    
        elif arg_list[0] == "receive-post" :
          if len(arg_list) == 1: 
            data = { 'status': 1, 'message': "Not login yet"}
          elif len(arg_list) != 2 :
            data = { 'status': 1, 'message': "Usage: receive-post <user>"}
          elif arg_list[1] in token_dict:
            temp_id = token_dict[arg_list[1]]
            for temp in id_list :
              if temp_id == temp['ID'] :
                post = temp['post']
                data = { 'status': 0, 'post': post}
          else :
            data = { 'status': 1, 'message': "Not login yet"}     
      else:
        data = { 'status': 1, 'message': "Not login yet"};  

    

    data = json.dumps(data)
    print(data)
    conn.send(data)    
  