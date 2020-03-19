#!/usr/bin/python

import socket
import json
import sys 
host = '140.113.207.51'
port = 8010

id_list = {}

host = raw_input()
port = input()

while True:
  client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  client.connect((host, port))
  arg = raw_input()
  arg = arg.replace('\n','')
  arg_list = arg.split()
  #print(arg)
  if arg == "exit":
    break
  elif arg_list[0] == "register":
    client.send(arg)
    response = client.recv(4096)
    y = json.loads(response)
    print(y["message"])
  elif arg_list[0] == "login":
    client.send(arg)
    response = client.recv(4096)
    y = json.loads(response)
    id_list[arg_list[1]] = y["token"]
    print(y["message"])
  else :
    arg_list[1] = id_list[arg_list[1]]
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
            print("NO friends")
          if arg_list[0][5:] == 'invite':
            print("NO invitations")    
        else:
          for x in y[arg_list[0][5:]]:
            print(x) 
      elif arg_list[0] == "receive-post":
        #print(*y["post"])
        if y["post"] == []:
          print("NO posts")
        else:
          for x in y["post"]:
            print(x["id"]+":"+x["message"]) 
      elif arg_list[0] == "logout":
        id_list[arg_list[1]] = None
        print(y["message"])   
      else:
        print(y["message"])
        #print(response)
    else:
      print(y["message"])