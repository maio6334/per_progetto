#!/usr/bin/env python3
"""
Client side module of a two-component application for evaluating Hamming and LDPC error correction algorithms.

It's coupled with a "server module" that relays the client's messages back injecting random errors.
Messages are read from a user-selected (utf-8 enconded) text file or from a built-in default string.
User can configure the number of messages to send and the error injection rate 
Client attemps to detect and correct errors logging each event to a file

Usage:
    python client.py [arguments]

Arguments:
    -i --input FILE        Path to the input text file (default: built-in default string)
    -m --messages N        Number of messages to send (default: 10)
    -r --repetition
    -e --error-rate RATE   Error injection rate, float between 0.0 and 1.0  (default: 0.01)
    -l --log FILE          Path to the output log file (default: client.log)

Examples:
    $ python client.py --help
    $ python client.py --input dati.txt --messages 50 

Dependencies:
    - python       >= 3.12.3
    - pandas       >= 2.3.3
    - numpy        >= 2.3.5
    - matplotlib   >= 3.10.8
    - PyQt6        >= 6.10.2
    - pyldpc        = 0.7.10
    - hamming_codec = 0.3.6
    - cli_funct

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
from cli_funct import validate_cmdline, _log_test,DEF_MSG



# import os

# local modules
# from commonhelp import  print_file_dic

#constants
TCP_IP = '127.0.0.1' #  'lab00'
TCP_PORT = 23232
BUFFER_SIZE = 1024

#validate input
num_msg,num_rept, error_rate, log_f, input_f, is_internal_input = validate_cmdline()
print(num_msg,num_rept, error_rate, log_f, input_f, is_internal_input)

#test log function
'''
#messagge formats
#every messag is repeated num_rept times
#tempo,send,n_mesg,tipo_codifica,durata_cod,err_rate 
#tempo,recv,n_mesg,tipo_codifica,durata_dec, err_ril, err_corr
)
_log_test(n_msg,e_rate, log_f)
'''
f=None

def get_next_line(fd)-> str:
    if l:=fd.readline():
        return l
    else:
        fd.seek(0)
        return fd.readline()

def get_message(internal:bool)-> (str,):
    global f
    if internal:
        line=DEF_MSG
    else:
        if f is None:
            f=open(input_f, encoding="utf-8")
        line= get_next_line(f)   
    return line,f

for i in range(12):
    mesg, f= get_message(is_internal_input)
    print(i,mesg)

if not(f is None):
    f.close()
exit()

def connect_2_server():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
   # s.settimeout(5.0)
    try:
        s.connect((TCP_IP, TCP_PORT))
    except ConnectionRefusedError:
        print('Server refused connection. Exiting')
        exit(1)
    except socket.timeout:
        print('Timeout connection to server. Exiting')
        exit(2)      
    return s



s=connect_2_server()
while True and count<3:
    #os.system('clear')
    ctl=Controller()
    mesg = pickle.dumps(cmd)
    s.sendall(mesg) # defualt utf-8
    if (cm1=='q'):
            end_prog(s,0)
    data=pickle.loads(s.recv(BUFFER_SIZE))
    cm1,value = data
    cmd_res(cm1,value)

    # print(data)
    # time.sleep(5)
    
    count+=1

s.close()


""" class Controller:
    selectedfile=""
    currentcmd=""
    filelist={}
    cmd=""
    cmd_value=""
    def __init_(self):
        pass


    def get_command(self)-> None:       
        valid=False
        while not(valid):
            os.system('clear')
            _print_choices()
            cmd = input(f"\nSelect a command -> ") 
            valid, cm1, cm2 =verify_command(cmd)
            if not(valid):
                print(f'command unknown :{cmd}')
                time.sleep(3)
        self.cmd=cm1
        self.cmd_value= cm2       

def cmd_res(cm1 :str,val: str | list| dict)-> None:
    resp=""
    match cm1:
        case "l":
            print_file_dic(val)
        case "r":
            print("data read :")

        case _: 
            print("unknown command ")
            
    return None



def end_prog(s,val=0):
    s.close()
    sys.exit(val)



#check number of parameters
if (len(sys.argv) < 2):
    my.usage_info()

count =0
"""