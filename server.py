#!/usr/bin/env python3
import socket
import os

from commonhelp import verify_command, txt_file_2_dic
import pickle

TCP_IP = '127.0.0.1' 
TCP_PORT = 23232
BUFFER_SIZE = 1024

serv =socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
serv.bind((TCP_IP, TCP_PORT))
serv.listen(1)
conn, addr = serv.accept()
print('connected from ', conn)
count=0

while True:
    d = conn.recv(BUFFER_SIZE)
    if not d: break 
    msg=pickle.loads(d)
    #o= "0x" +" 0x".join(f'{(cmd)[i]:02x}' for i in range(len(cmd))) 
    #print (f"received message {count} :", cmd, " - hex values " , o)
    if verify_msg(msg):
        coding, level, data, ctl = msg
    else:
        r="U" # wrong message 
    conn.sendall(pickle.dumps(r))
    count+=1
