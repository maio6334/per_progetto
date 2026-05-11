#!/usr/bin/env python3
"""
Client side module of a two-component application for evaluating Hamming and LDPC error correction algorithms.

It's coupled, via TCP socket, to a server module that relays the client's messages back after injecting random errors.
Messages are read from a user-selected (utf-8 enconded) text file or from a built-in default string.
User can configure the number of messages to send and the error injection rate
the same message is repeated  
Client attemps to detect and correct errors logging each event to a file

Usage:
    python client.py [arguments]

Arguments:
    -i --input FILE        Path to the input text file (default: built-in default string)
    -m --messages N        Number of messages to send (default: 10)
    -r --repetition REP    Number of repetition for each message (default:)
    -e --error-rate RATE   Error injection rate, float between 0.0 and 1.0  (default: 0.01)
    -l --log FILE          Path to the output log file (default: client.log)
       --verbose           Prints the docstring info of this module

Examples:
    python client.py --help
    python client.py --input dati.txt --messages 50 

Dependencies:
    - python       >= 3.12.3
    - pandas       >= 2.3.3
    - numpy        >= 2.3.5
    - matplotlib   >= 3.10.8
    - PyQt6        >= 6.10.2
    - pyldpc        = 0.7.10
    - hamming_codec = 0.3.6
    - shared_funct
    - constants

To do:
    Diagrams from log file

Date: 
    AA 2025/2026

Author:
    Angelo Maurizio Calabrese <angelo.calabrese@studenti.unimi.it>

Version:
    1.0
"""

# standard modules
import socket
import pickle
import matplotlib


# local modules 
from shared_funct import manage_cmdline, get_text_message,\
    connect_2_server,count_difference, enc_str_to_list,\
    dec_list_to_str, send_with_header, recv_witch_header     
from costants import TESTING,TCP_IP,TCP_PORT ,BUFFER_SIZE 

#validate input
descr=\
'''
Client side module of a two-component application for evaluating Hamming and LDPC error correction algorithms.

It's coupled, via TCP socket, to a "server module" that relays the client's messages back injecting random errors.
Messages are read from a user-selected (utf-8 enconded) text file or from a built-in default string.
User can configure the number of messages to send and the error injection rate 
Client attemps to detect and correct errors logging each event to a file
'''

input_f, log_f, num_rept, error_rate  = manage_cmdline(descr)



s=connect_2_server()
text = get_text_message(input_f)

if TESTING:
    num_rept=2
    #text='ABCD'
    error_rate=0.01

enc_text, avg_te= enc_str_to_list(text)
#print(enc_text)


for r in range(num_rept):
    for c in ['H','L']:
        #print(f'info:coding={c}\terror rate={error_rate}\tmesg={enc_text}')
        mesg={'coding':c,'er':error_rate,'enc_text':enc_text}
        if False:
            rmsg=mesg
        else:
            payload = pickle.dumps(mesg)
            l=len(payload)
            send_with_header(s,payload)  # needed ad payload > BUFFER_SIZE # old s.sendall(payload) 
            rmsg=pickle.loads((recv_witch_header(s))) #rmsg=pickle.loads(s.recv(BUFFER_SIZE))
        
        r_enc_text=rmsg['enc_text']
        rtext, avg_td= dec_list_to_str(r_enc_text)

        err=count_difference(text,rtext)
        if text==rtext:
            check='passed'
        else:
            check=f'total difference ={err}'
        #print(f'mesg coding:{c}, check:{check}\n')
        if c=='H':
            print(c,text)
            print(c,rtext)

if s is not None:
    s.close()
exit()
