#!/usr/bin/python

import socket
import json
import sys 
import stomp

class SampleListener(object):
    def on_message(self, headers, message):
        print(message)
#host = '140.113.207.51'
#port = 8010
id_list = {}
con_dict = {}

host = sys.argv[1] 
port = int(sys.argv[2])

##register, login, logout, delete

com=["exit","register","login","post","receive-post","delete","logout",
     "invite","list-invite","accept-invite","list-friend","send-group",
     "join-group","list-joined","list-group","create-group","send"]
listener_name = 'SampleListener'

while True:
  arg = raw_input()
  arg = arg.replace('\n','')
  arg_list = arg.split()
  #print(arg)
  if arg == "exit":
    break
  
  if arg_list[0] in com:
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)   
    client.connect((host, port))

    if arg_list[0] == "register":
      client.send(arg)
      response = client.recv(4096)
      y = json.loads(response)
      print(y["message"])
  
    elif arg_list[0] == "login":
      client.send(arg)      
      response = client.recv(4096)
      y = json.loads(response)
      if y["status"]==0:
        id_list[arg_list[1]] = y["token"]
        con_dict[y["token"]] = stomp.Connection10([('127.0.0.1',61613)])
        con_dict[y["token"]].set_listener(listener_name , SampleListener())
        con_dict[y["token"]].start()
        con_dict[y["token"]].connect()
        queue_name = '/queue/'+arg_list[1]
        con_dict[y["token"]].subscribe(queue_name)
        for i in y["group"]:
          topic_name = '/topic/'+i
          con_dict[y["token"]].subscribe(topic_name)
      print(y["message"])
    
    else :
      if len(arg_list)>1:
        if arg_list[1] in id_list:
          id_tmp=arg_list[1]
          arg_list[1] = id_list[arg_list[1]] 
        else:
          arg_list[1] = ""
      arg = " ".join(arg_list)
      client.send(arg)
      response = client.recv(4096)
      y = json.loads(response)
      #print(response)    
      if y["status"] == 0:
        if arg_list[0] == "list-friend" or arg_list[0] == "list-invite":
        #print(y["message"])
          if y[arg_list[0][5:]] == []:
            if arg_list[0][5:] == 'friend':
              print("No friends")
            if arg_list[0][5:] == 'invite':
              print("No invitations")    
          else:
            for x in y[arg_list[0][5:]]:
              print(x) 
        elif arg_list[0] == "receive-post":
          #print(*y["post"])
          if y["post"] == []:
            print("No posts")
          else:
            for x in y["post"]:
              print(x["id"]+": "+x["message"]) 
        elif arg_list[0] == "logout":
          con_dict[arg_list[1]].disconnect()
          id_list.pop(id_tmp)
          print(y["message"])   
        elif arg_list[0] == "delete":
          con_dict[arg_list[1]].disconnect()
          con_dict.pop(arg_list[1])
          id_list.pop(id_tmp)
          print(y["message"])
        elif arg_list[0] == "join-group":
          topic_name = '/topic/'+arg_list[2]
          con_dict[arg_list[1]].subscribe(topic_name)
          print(y["message"])
        elif arg_list[0] == "create-group":
          topic_name = '/topic/'+arg_list[2]
          con_dict[arg_list[1]].subscribe(topic_name)
          print(y["message"])
        elif arg_list[0] == "list-group" or arg_list[0] == "list-joined":
          if y["message"]=="No groups":
            print(y["message"])
          else:
            for i in y["message"]:
              print(i)
        else:
          print(y["message"])
          #print(response)
      else:
        print(y["message"])
  elif arg in com:
    client.send(arg)
    response = client.recv(4096)
    y = json.loads(response) 
    print(y["message"])       
  else:
  	print("Unknown command "+ arg_list[0])