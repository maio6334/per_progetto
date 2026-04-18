#!/usr/bin/env python3
"""
Server side module of a two-component application for evaluating Hamming and LDPC error correction algorithms.

It receives from client a messagge consisting in XXX fields:
 - id message (int)
 - an (float) error rate value
 - a coded string 
 - a checksum (byte)
 it modified the string 
 then it send back a message consisting in YY fields:
 - id message (int)
 - a coded string 
 - a checksum (byte)



Usage:
    python server.py 

Arguments:
    

Examples:
    python server.py 


Dependencies:
    - python       >= 3.12.3
    - random
    - constants

Date: 
    AA 2025/2026

Author:
    Angelo Maurizio Calabrese <angelo.calabrese@studenti.unimi.it>

Version:
    1.0
"""
# standard modules
import argparse  
import socket
import os
import pickle
import signal # to handle manual shutdown
import random

# local modules and functions
from costants import TESTING,TCP_IP,TCP_PORT ,BUFFER_SIZE 
from cli_funct import GetDetailedInfo
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

descr=\
'''
Server side module of a two-component application for evaluating Hamming and LDPC error correction algorithms.
'''

parser = argparse.ArgumentParser(description=descr, formatter_class=argparse.RawDescriptionHelpFormatter)
parser.add_argument("--verbose", nargs=0,action=GetDetailedInfo, help="Prints the main-module's docstring")
    
args = parser.parse_args()

stop=False
signal.signal(signal.SIGINT,stop_loop) # to accept ctrl +c from console

serv=server_activate()
print('\nServer started. CTRL+C to close.\n')
serv.settimeout(20)
conn_count=0
conn=None

while not stop:
    try:
        #raise
        conn, addr = serv.accept()
        print(f'connected from {addr}')
        count=0
        conn_count+=1
         
    except socket.timeout:  # solving timeout closing conneciont
        print('\nTimeout.\n')
        continue
    except Exception as e:
        print('\nGeneric socket error.\n')
        break

    with conn:
        while not stop:    
            try:
                d = conn.recv(BUFFER_SIZE)
                if not d:
                    print(f'\nconnection closed from {addr}\n')
                    break 
                msg=pickle.loads(d)
                count+=1
                print(f'{count} -received {msg}')
                conn.sendall(pickle.dumps(msg))
                print(f'{count} - send back {msg}')
            except Exception as e:
                print(f'error starting server.\n Closing program{__file__}')  

serv.close() # close the socket
print(f'Server down.\nManaged {conn_count} connections')

