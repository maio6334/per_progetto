#!/usr/bin/env python3

"""
Server side module of a two-component application for evaluating Hamming and LDPC error correction algorithms.

It receives from client a messagge consisting a dictionary containing :
 - coding : representd the type of coding 
 - er     : bit error rate
 - enc    : a coded string 
 - hash   : hash value calculated for enc

 if coding=H enc is modified changing n bits to comply with er  
 then it send back 
 

Usage:
    python server.py 

Arguments:
    

Examples:
    python server.py 


Dependencies:
    - python       >= 3.12.3
    - shared_funct
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



# local modules and functions
from costants import TESTING,TCP_IP,TCP_PORT ,BUFFER_SIZE 
from shared_funct import GetDetailedInfo, msg_with_errors,\
    send_with_header, recv_witch_header ,\
    ConnectionClosed, ConnectionLost,get_hash , is_valid_data

#from commonhelp import verify_command, txt_file_2_dic

def server_activate():
    try:
        serv =socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        serv.bind((TCP_IP, TCP_PORT))
        serv.listen(1)
        print(f'Server is listening on {TCP_IP};{TCP_PORT}')
        
    except Exception as e:
        print(f'\nGeneric error starting server.\n\nClosing {__file__}\n')
        exit(1)
    return serv

def stop_loop():
    global stop
    stop=True

descr=\
'''
Server side module of a two-component application for evaluating Hamming and LDPC error correction algorithms.
CTRL +C to stop
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
        conn, addr = serv.accept()
        print(f'Connected from {addr}')
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
                d=recv_witch_header(conn) 
                msg=pickle.loads(d)
                count+=1
                
                #check corrupted payload
                r_hash=msg['hash']
                r_enc=msg['enc']
                check=is_valid_data(r_enc,r_hash)
                #check=False
                if not(check):
                    print("payload is corrupted, request resending ")
                    msg['coding']='W' #signal wrong message requiring resend
                else:
                    if msg['coding']=='H':
                        #  insert error routine
                        print(f'{count} - received  {msg}')
                        rate=msg['er']
                        enc=msg['enc']
                        ret_mesg, flipped=msg_with_errors(rate, enc)
                        msg['enc']=ret_mesg
                        msg['hash']=get_hash(ret_mesg)
                        print(f'{count} - send back {msg}')   

                payload=pickle.dumps(msg)
                l=len(payload)
                send_with_header(conn,payload)    #conn.sendall(pickle.dumps(msg))
            except ConnectionClosed:
                break
            except Exception as e:
                    print(f'Error: {e}\nClosing program{__file__}')
                    exit(1) 

serv.close() # close the socket
print(f'Server is gracefully closed.\nManaged {conn_count} connections')

