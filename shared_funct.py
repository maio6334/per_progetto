#!/usr/bin/env python3
"""
This module contains functions used by client.py.

Used for:
   - analizing and checking command line parameters 
   - testing logger object
   - reading lines from source selected (file/internal)


Functions:
    manage_cmdline          : analize and checks command line parameters 
    hamming_enc_str_to_list : using hamming lib, code every char from a utf-8 string, returns a list
    hamming_dec_list_to_str : using hamming lib, decode a list of encodeded char, returns string
    msg_with_errors         : introduces errors flipping single bit in a list of encoded chars, returns list corrupted and total flipped bits
    log                     : log events in a csv format to a file  
    ber_to_snr              : converts a value of Bit erorr rate to a Signal to noise ratio
    count_differences       : counts difference in string
    recv_witch_header       : receive a message from a socket collecting chunks of data if lmessage lenght > BUFFER_SIZE
    send_with_header        : send a payload to a socket prepending his lenght
    get_hash                : calculate data's hash digest 
    is_valid_data           : validate data against his hash digest
    sweep_range             : returns a list of 'steps' values around a given mean value 

Date: 
    AA 2025/2026

Author:
    Angelo Maurizio Calabrese <angelo.calabrese@studenti.unimi.it>

Version:
    1.0
"""
# standard modules
import argparse
from pathlib import Path
import sys
import logging
import time
import numpy as np
import random
import socket
import hamming_codec  as hc
from timeit import timeit
import math
import struct
from pyldpc import make_ldpc, decode, get_message, encode
import hashlib
import pandas as pd
import matplotlib.pyplot as plt

# local modules
from costants import TCP_IP,TCP_PORT ,BUFFER_SIZE, TIMING_ITERATIONS,\
                     PACKING_FORMAT, BYTES_IN_INTEGER, TESTING
                    
# local constants
DEF_MSG=    '"A§€𝄞.My mama always said: "Life was like a box of chocolates; you never know what you’re gonna get."'
DEF_LOG= 'log.csv'
DEF_ERR_RATE= 0.02
MIN_ERR_RATE= 0.001
MAX_ERR_RATE= 0.1

DEF_STEPS= 30
MAX_STEPS= 500


def sweep_range(mid:float,steps:int)->list:
    """
    Returns a list of 'steps' values around a given mean value 

    Parameters
    ----------
    mid
        center of range
    steps
        number of steps

    Returns
    -------
    seq
        list of float
    """
    delta = (mid/(steps/2))
    start = mid-delta
    stop  = mid+ delta
    seq = np.linspace(start,stop,steps) 
    return seq 



class GetDetailedInfo(argparse.Action):
    """
    Class used by manage_cmdline to generate a verbose descrtiption when --verbose in command line
    Prints all docstrings
    """

    def __init__(self,option_strings,dest,nargs, **kwargs):
        super().__init__(option_strings,dest,nargs, **kwargs)

    def __call__(self,parser,namespace,values,option_strings=None):
        print(sys.modules['__main__'].__doc__)
        parser.exit()

def manage_cmdline(descr:str)-> (str,str,float,int): #bool):
    """
    Parse command line argument checking type for numeric inputs
    Add help funcionality to command line
    Verify that input file exists and isn't a binary type
    Set defaults when parameter is missing
    controls numeric parameter is in range limits, if not sets it to nearest limit

    Parameters
    ----------
    descr
        brief description of module

    Returns
    -------
    file_input
        full path of input file from command line ( None if input is missing)
    log_file
        file to log events
    err_rate
        mean % of errors in message (BER)
    steps
        number of cycles  code /decode to be measured

    """
    #internal
    #    True if input file is missing use internal string

    parser = argparse.ArgumentParser(description=descr, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("-i","--input", default=None, help="Path to the input text file, if input is missing will be code/decode a built-in string")
    parser.add_argument("-l","--log", default=DEF_LOG, help=f"Path to the output log file (default: ./{DEF_LOG})")
    parser.add_argument("-e","--error-rate", type=float,default=DEF_ERR_RATE,help=f"Error rate, float between {MIN_ERR_RATE} and {MAX_ERR_RATE} if missing default: {DEF_ERR_RATE})")
    #parser.add_argument("-r","--repeat", type=int,default=DEF_REPT,help=f"number of repetition for code-decode cycle (default: {DEF_REPT}, max:{MAX_REPT} )") 
    parser.add_argument("-s","--steps", type=int,default=DEF_STEPS,help=f"number of code-decode cycles using equally spaced values around the selected error rate(default: {DEF_STEPS})") 
    parser.add_argument("-v","--verbose", nargs=0,action=GetDetailedInfo, help="Prints the main-module's docstring")
    
    args = parser.parse_args()

    script_dir = Path(__file__).parent.resolve()

    if args.input:
        file_input= '/'.join([script_dir._str,args.input]) # rem script_dir is a object
        #check file exist and is text
        try:
            f=open(file_input, encoding="utf-8") 
            try:
                t=f.read(1) # check only first char - that is one or more bytes
            except UnicodeDecodeError:
                print(f"Error: Input file \"{file_input}\" di tipo binario")
                sys.exit(2)
        except FileNotFoundError:
            print(f"Error: Input file \"{file_input}\" does\'nt exists.")
            sys.exit(3)     
    else:
        file_input=None

    log_file= '/'.join([script_dir._str,args.log]) 
    try:
        f=open(log_file,'a',  encoding="utf-8") 
    except FileNotFoundError:
        print(f"Input file \"{file_input}\" does\'nt exists.")
        sys.exit(3)

    def range_validate(name:str, val:any, min:any, max:any)-> any:
        mod=True
        if val < min:
            ret= min
        elif val > max:
            ret= max
        else:
            ret= val
            mod=False
        if mod:
            print(f'Warning:\n{name} input value {val} is out-of-range {min}-{max}: modified to {ret} (nearest range value)\n')
        return ret


    #num_repetition=range_validate('--repeat',args.repeat,DEF_REPT,MAX_REPT)
    err_rate =range_validate('--error-rate',args.error_rate,MIN_ERR_RATE,MAX_ERR_RATE)  # !! Parser translate - with _
    steps=range_validate('--steps',args.steps,0,MAX_STEPS) 

    return (file_input, log_file, err_rate,steps) 

def get_text_message(input_f:str | None)-> str:
    """
    Returns a string reading all text from input_f , if input_f is None return an internal string (DEF_MSG)

    Parameters
    ----------
    input_f
        text file full path from command line | None 

    Returns
    -------
    line
        text as a string

    """

    if input_f is None:
        l=DEF_MSG
    else: 
        l=read_file(input_f)
    return l

def connect_2_server():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
   # s.settimeout(5.0)
    try:
        s.connect((TCP_IP, TCP_PORT))
    except ConnectionRefusedError:
        print('Server refused connection. Exiting')
        exit(4)
    except socket.timeout:
        print('Timeout connection to server. Exiting')
        exit(5)      
    return s

def ldpc_enc_str_to_array(text:str,G:np.ndarray,snr:float,seed:int)->(np.ndarray,float):
    """
    Reads an input string,converts it to a matrix the encode using a LDPC matrix adding a noise 
    Calculate encoding average time of execution, Returns a matrix containing encoded chars and average time

    Parameters
    ----------
    text
        text message to encode
    G
        encoding matrix
    snr 
        signal to noise ratio 
    seed
        random value required to introduce a non deterministic error

    Returns
    -------
    encoded
        matrix containing the encoded text whit a noise
    dur_avg
        average duration in encoding 
    """
    k = G.shape[1] # k=8 as expected
    #convert text into matrix
    # first from text to flat array
    bits=np.array([ e>>i & 1 for e in text.encode() for i in range(8)])
    # split every byte into columns
    bits_matrix=bits.reshape((-1,k)).T
    try:
        encoded = encode(G, bits_matrix, snr, seed=seed)
        dur= timeit(lambda: encode(G, bits_matrix, snr, seed=seed), number=TIMING_ITERATIONS)
    except Exception :
        dur=float("nan")
    dur_avg=dur/(TIMING_ITERATIONS * len(text))
    
    return encoded, dur_avg

def ldpc_dec_list_to_str(r_enc:np.ndarray,H:np.ndarray,G:np.ndarray,snr:float)-> (str,float):
    """
    Using pyldpc lib, decode a list of encodeded char into a string

    Parameters
    ----------
    r_enc
        matrix encoded
    H,G
        decoding and coding matrices
    snr
        bit error rate

    Returns
    -------
    rtext, 
        decoded string 
    
    dur_avg
        average duration decoding
    """
    #decode
    try:
        D = decode(H, r_enc, snr)
    except Exception as e:
        print('Error LDPC decode function')
        pass

    try:
        dur= timeit(lambda: decode(H, r_enc, snr), number=TIMING_ITERATIONS)
    except Exception :
        dur=float("nan")    
    #extract message
    # flatting matrix 
    x=[]
    for i in range(D.shape[1]): # loop on columns
        x.append(get_message(G, D[:, i]))
    rbits=np.concatenate(x) # it is flattened if  axis= none

    #from bytearray to text
    bytelist=[]
    for l in range(len(rbits)//8):
        array_bit=rbits[l*8:8*(l+1)]
        byte=0
        for i in range(8):
            byte=byte |(array_bit[i]<<i)
        bytelist.append(byte)
    rtext=bytearray(bytelist).decode("utf-8",errors='replace') 
    dur_avg=dur/(TIMING_ITERATIONS * len(rtext))
    #rtext="dummy LPDC"
    return rtext, dur_avg

def hamming_enc_str_to_list(text:str)->list:
    """
    Reads an input string, encode every char.Calculate encoding average time of execution, Returns a list containing encoded chars and average time

    Parameters
    ----------
    text
        text message to encode

    Returns
    -------
    enc
        list of encoded chars
    dur_avg
        average duration in encoding 
    """
    enc=[]
    dur=0 # duration of an event
    for i in range(len(text)):
        l=len(text[i].encode())*8
        c_ord=ord(text[i])
        try:
            c=hc.encode(c_ord,l)
            dur+= timeit(lambda: hc.encode(c_ord,l), number=TIMING_ITERATIONS)
        except Exception :
            dur=float("nan")
        enc.append(c)
    dur_avg=dur/(TIMING_ITERATIONS * len(text))

    return enc, dur_avg

def msg_with_errors(rate :float, message:list) -> (list, int):
    """
    Changes ,according an input error rate, nput string, Returns the list containing errors

    after joing XXXXXXXX MAIO

    Parameters
    ----------
    rate
        % of bits to modify as a whole
    message
        list of strings representing encoded chars

    Returns
    -------
    enc
        list of corrupted strings
    num_err
        num of bits changed in every list's item
    """
    #rate=0.04
    joined_mess=''.join(message)
    total_bits=len(joined_mess)
    #print (f'joined_mess= {joined_mess}\ntotal_bits= {total_bits}')
    num_err=int(round(total_bits*rate,0))
    split_pos=[0]
    for i in range(len(message)):
        split_pos.append(split_pos[i]+len(message[i]))
    print(f'rate={rate}, total_bits={total_bits},num_err={num_err}')
    rng = np.random.default_rng() # init random generator
    pos_err = rng.integers(low=0, high=total_bits-1, size=num_err)
    #pos_err=[69,22,78]
    for pos in pos_err:
        #print(f'bit flipping position={pos}')
        f= '1' if joined_mess[pos]=='0' else '0'
        joined_mess= joined_mess[:pos] + f+ joined_mess[pos+1:]
    ret_mess=[]
    for i in range(len(split_pos)-1):
        ret_mess.append(joined_mess[split_pos[i]:split_pos[i+1]])
    
    return ret_mess, num_err

def hamming_dec_list_to_str(message:list)-> str:
    """
    Using Hamming lib, decode a list of encodeded char into a string, substitutes char with "X" if decoding fails

    Parameters
    ----------
    text
        list of encoded chars

    Returns
    -------
    r
        string
    
    dur_avg
        average duration decoding
    """
        
    r=[]
    dur=0
    for i in range(len(message)):
        imsg=int(message[i],2)
        l=len(message[i])

        try:
            d = hc.decode(imsg, l)
        except Exception:
            d='0b1111111111111101' #  �

        try:
            dur+= timeit(lambda: hc.decode(imsg, l), number=TIMING_ITERATIONS)
        except Exception :
            dur=float("nan")

        try:
            r.append(chr(int(d,2)))
        except (ValueError,OverflowError): # overflow detected when int is not a unicode value
            print(f'error decoding character in position {i} , inserting  "�" instead', file=sys.stderr)
            r.append(chr(0xFFFD)) #  �
    r=''.join(r)
    dur_avg=dur/(TIMING_ITERATIONS * len(message))
    #print(f'"DEC","HAM",{dur_avg}')
    return r, dur_avg


def log(event:dict,log_f:str)-> None:
    """
    log appending event to a file

    Parameters
    ----------
    event
        dictionary of data
    log_f
        path to log file

    Returns
    -------
    None

    """
    # old FORMAT='%(asctime)s;%(message)s;%(rate)s;%(diff)s;%(avg_te)s;%(avg_td)s'
    FORMAT='%(asctime)s;%(message)s;%(rate)s;%(action)s;%(diff)s;%(avg_t)s'
    logger = logging.getLogger(__name__) # maybe None but it's a reccommended practice maybe to distinguish logs from differente modules
    logging.basicConfig(filename=log_f, filemode='a',encoding='utf-8', \
    format=FORMAT,level=logging.INFO) # datefmt='%m/%d/%Y %I:%M:%S %p',
    logger.info(event['coding'],extra=event)

def read_file(fullp:str)-> str:
    """
    Open file for readind, close program if not utf-8 encoded file, returs file contents as signle string

    Compares two string by position, counts how many corrispondent chars differs

    Parameters
    ----------
    fullp
        string  path to file

    Returns
    -------
    l
        a string containg all the lines
    """
    try:
        with open(fullp,encoding='utf-8') as f:
            l=f.read()
            #print(l)
    except UnicodeDecodeError as e:
        print(f'error in encodig utf-8 file {fullp}\ndetected {e.reason}\nClosing program')
        exit(2)
    return l

def ber_to_snr(error_rate:float)-> float:
    """
    converts ber in snr

    Parameters
    ----------
    error_rate
        bit error rate = #bit wrong / #total bit

    Returns
    -------
    snr
        signal to noise ratio as 10*log((total - errors)/ errors) 

    """
    snr=10*math.log10((1/error_rate)-1)
    return snr   

def count_differences(ini:str, fin:str)->int:
    """
    Compares two string counting chars not correspondent 
    if different in lenght extra chars are added to errors

    Parameters
    ----------
    ini
        first string to compare
        
    fin
        second string to compare

    Returns
    -------
    errors
        total chars not corrispondent
    """
    errors=0
    li=len(ini)
    lf=len(fin)
    m=min(li,lf)
    if li!=lf:
        errors+=abs(li-lf)
    for i in range(m):
        if ini[i]!=fin[i]:
            errors+=1
    return errors

def send_with_header(s:int,payload:bytes)->None:
    """
    Send a payload to a socket, prepending his lenght 
    

    Parameters
    ----------
    s
        socket

    payload
        data to send

    Returns
    -------
    None
    """   
    header=struct.pack(PACKING_FORMAT, len(payload)) # unsigned int 4 bytes BE
    s.sendall(header+ payload)     

class ConnectionClosed(ConnectionError):
    "service class to export exception to server"
    pass

class ConnectionLost(ConnectionError):
    "service class to export exception to server"
    pass

def _recv_bytes(s:int, l:int)->bytearray:
    """
    Reads l bytes from socket
    
    Parameters
    ----------
    s
        socket
    l
        number of bytes to read f

    Returns
    -------
    buffer
         bytes read from socket 
    """  
    buffer = b''
    while len(buffer) < l:
        try:
            fragment = s.recv(min(BUFFER_SIZE, l- len(buffer)))
            if not fragment:
                raise ConnectionClosed("Connection closed")
            buffer += fragment
        except (ConnectionResetError,TimeoutError):
                raise ConnectionError('Connection lost')
    return buffer
    
def recv_witch_header(s)->bytearray:
    """
    receive a message from a socket collecting chunks of data if lmessage lenght > BUFFER_SIZE
    
    Parameters
    ----------
    s
        socket

    Returns
    -------
    data
        payload (a dictionary as bytearray)
    """   
    get_len=_recv_bytes(s,BYTES_IN_INTEGER) # to do substitute 4 with a tyoe lenght of int
    l=struct.unpack(PACKING_FORMAT,get_len)[0]
    data=_recv_bytes(s,l)
    return data

def is_valid_data(data:any, digest:bytearray)-> bool:
    """
    Validate data against his hash digest
    
    Parameters
    ----------
    data
        a list or an array
    
    digest
        sha256 digest to compare

    Returns
    -------
    _
        True if input digest matches calculated's one
        
    """   
    return  digest==get_hash(data) # better a lambda ? lambda( data, digest: digest==get_hash(data))

def get_hash(data:list|np.ndarray)-> str:
    """
    Calculate data's hash digest 
    
    Parameters
    ----------
    data
        a list or an array

    Returns
    -------
    data
        sha256 digest of data
    """   
  
    m=hashlib.sha256()
    mv_enc= memoryview(np.char.array(data))  if isinstance(data,list) else memoryview(data) 
    m.update(mv_enc)
    return  m.hexdigest()

def visually_compare2(logfile:str,columns:list):
    if TESTING:
        event={'coding':'H','rate':0.0, 'diff':0, 'avg_te':0.0, 'avg_td':0.0}
    columns=list(event)
    columns.insert(0,'datetime')
    df=pd.read_csv(logfile, names=columns, index_col=2, delimiter=';')
    df=df.groupby(['rate','coding']).mean()
    df.reset_index()
    
    
    l=[]
    for cod in coding:
        for dim in columns[4:]:
            filt=df[df['coding']==cod][dim].groupby(level=0).mean()
            ser_name=cod + '-' + dim
            filt.name=ser_name
            l.append(filt)

    df2=pd.concat(l,axis=1)
    df2.plot()
    plt.show()
    pass



def visually_compare(logfile:str,columns:list):
    if TESTING:
        event={'coding':'H','rate':0.0, 'diff':0, 'avg_te':0.0, 'avg_td':0.0}
    columns=list(event)
    columns.insert(0,'datetime')
    df=pd.read_csv(logfile, names=columns, index_col=2, delimiter=';')
    coding=pd.unique(df.coding)
    l=[]
    for cod in coding:
        for dim in columns[4:]:
            filt=df[df['coding']==cod][dim].groupby(level=0).mean()
            ser_name=cod + '-' + dim
            filt.name=ser_name
            l.append(filt)

    df2=pd.concat(l,axis=1)
    df2.plot()
    plt.show()
    pass



def main():
    #read_file('./inferno_c1.txt')
    #f='/home/maurizio/Desktop/progit.pdf'
    #f='./inferno_c1.txt'
    #read_file(f)
    visually_compare2('log.csv',[])

    pass

if __name__ == "__main__":
    print(hc.__file__)
    main()