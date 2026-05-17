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
import numpy as np
from pyldpc import make_ldpc, decode, get_message, encode

# local modules 
from shared_funct import manage_cmdline, get_text_message,\
    connect_2_server,count_difference, hamming_enc_str_to_list,\
    hamming_dec_list_to_str, send_with_header, recv_witch_header, \
    log, ber_to_snr,ldpc_enc_str_to_array, ldpc_dec_list_to_str       

from costants import LDPC_N, LDPC_D_V, LDPC_D_C # TESTING


#validate input
descr=\
'''
Client side module of a two-component application for evaluating Hamming and LDPC error correction algorithms.

It's coupled, via TCP socket, to a "server module" that relays the client's messages back injecting random errors.
Messages are read from a user-selected (utf-8 enconded) text file or from a built-in default string.
User can configure the number of messages to send and the error injection rate 
Client attemps to detect and correct errors logging each event to a file
'''

# commande line param management & defaults
input_f, log_f, num_rept, error_rate  = manage_cmdline(descr)

# create code/decode matrix using LDPC lib
seed = np.random.RandomState(42)
H, G = make_ldpc(LDPC_N, LDPC_D_V, LDPC_D_C, seed=seed, systematic=True, sparse=True)
k = G.shape[1] # k=8 as expected
#converting BER to SNR
snr=ber_to_snr(error_rate) 

s=connect_2_server()
text = get_text_message(input_f)

event={} # to log duration 

for r in range(num_rept):
    for c in ['H','L']:
        avg_te=0
        avg_td=0
        if c=="H":
            encoded, avg_te= hamming_enc_str_to_list(text)
        else:
            # #convert text into matrix
            # # first from text to flat array
            # bits=np.array([ e>>i & 1 for e in text.encode() for i in range(8)])
            # # split every byte into columns
            # bits_matrix=bits.reshape((-1,k)).T
            # encoded = encode(G, bits_matrix, snr, seed=seed)
            # #encoded="dummy LPDC"
            encoded, avg_te= ldpc_enc_str_to_array(text,G,snr,seed)
    
        mesg={'coding':c,'er':error_rate,'enc':encoded}

        payload = pickle.dumps(mesg)
        l=len(payload)
        send_with_header(s,payload)  # needed ad payload > BUFFER_SIZE # old s.sendall(payload) 
        rmsg=pickle.loads((recv_witch_header(s))) #rmsg=pickle.loads(s.recv(BUFFER_SIZE))
        
        r_enc=rmsg['enc']

        if c=="H":
            rtext, avg_td= hamming_dec_list_to_str(r_enc)
        else:
            # #decode
            # D = decode(H, r_enc, snr)
            # #extract message
            # # flatting matrix 
            # x=[]
            # for i in range(D.shape[1]): # loop on columns
            #     x.append(get_message(G, D[:, i]))
            # rbits=np.concatenate(x) # it is flattened if  axis= none

            # #from bytearray to text
            # bytelist=[]
            # for l in range(len(rbits)//8):
            #     array_bit=rbits[l*8:8*(l+1)]
            #     byte=0
            #     for i in range(8):
            #         byte=byte |(array_bit[i]<<i)
            #     bytelist.append(byte)
            # rtext=bytearray(bytelist).decode() 
            # #rtext="dummy LPDC"
            rtext, avg_td=ldpc_dec_list_to_str(r_enc,H,G,snr)
        

        err=count_difference(text,rtext)
        log({'coding':c,'rate':error_rate,'diff':err, 'avg_te':avg_te, 'avg_td':avg_td},log_f )
  
        print(f"ini {c} {text}" )
        print(f"fin {c} {rtext}\n")
        

if s is not None:
    s.close()
exit()
