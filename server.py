#!/usr/bin/env python3

# standard modules
import socket
import os
import pickle
import signal # to handle manual shutdown

# local modules and functions
from costants import TESTING,TCP_IP,TCP_PORT ,BUFFER_SIZE 
#from commonhelp import verify_command, txt_file_2_dic

def server_activate():
    try:
        serv =socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        serv.bind((TCP_IP, TCP_PORT))
        serv.listen(1)
        print(f'Server is listening on {TCP_IP};{TCP_PORT}')
        #raise testing except
    except Exception as e:
        print(f'\nGeneric error starting server.\n\nClosing {__file__}\n')
        exit(0)
    return serv

def stop_loop():
    global stop
    stop=True

stop=False
signal.signal(signal.SIGINT,stop_loop) # to accept ctrl +c from console

serv=server_activate()
serv.settimeout(2)
conn_count=0
conn=None

while not stop:
    try:
        #raise
        conn, addr = serv.accept()
        print(f'connected from {addr}')
        conn_count+=1
         
    except socket.timeout:  # solving timeout closing conneciont
        continue
    except Exception as e:
        print('\nGeneric socket error.\n')
        break

    try:
        d = conn.recv(BUFFER_SIZE)
        if not d:
            print(f'\nconnection from {addr} lost\n')
            continue # so wait a new connection
        msg=pickle.loads(d)
        conn.sendall(pickle.dumps(msg))
    except Exception as e:
        print(f'error starting server.\n Closing program{__file__}')  
    finally:
        if conn is not None:
            conn.close()
            print(f'Closing connection from {addr}')


serv.close() # close the socket
print(f'Server down.\nManaged {conn_count} connections')

"""  
#o= "0x" +" 0x".join(f'{(cmd)[i]:02x}' for i in range(len(cmd))) 
#print (f"received message {count} :", cmd, " - hex values " , o)
if verify_msg(msg):
    coding, level, data, ctl = msg
else:
    r="U" # wrong message  
"""