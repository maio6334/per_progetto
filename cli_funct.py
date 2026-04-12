"""
This module contains functions used by client.py.

Used for analizing and checking command line parameters   



Functions:
    validate_cmline()->None : analize and checks command line parameters 


Date: 
    AA 2025/2026

Author:
    Angelo Maurizio Calabrese <angelo.calabrese@studenti.unimi.it>

Version:
    1.0
"""

import argparse
from pathlib import Path
import sys
import logging
import time
import numpy as np
import random

#constants
DEF_MSG='All work and no play makes Jack a dull boy' # 'My mama always said, Life was like a box of chocolates; you never know what you’re gonna get.'
DEF_LOG= 'log.csv'
DEF_RATE= 0.5
DEF_REPT=5
MAX_REPT=50
INTERNAL=True

def validate_cmdline()-> (int,float,str,str,bool):
    """
    Parse command line argument checking type for numeric inputs
    Add help funcionality to command line
    Verify that input file exists and isn't binary type
    Set defaults when parameter is missing
    when a numeric parameter is out of range set it to nearest limit

    Parameters
    ----------
    None


    Returns
    -------
    num_msg
        how many messagges to send
    err_rate
        % of errors in message
    log_file
        file to log events
    file_input
        full path of input file from command line ( None if input is missing)
    mod
        True id input file is missing

    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default=None, help="Path to the input text file (default: built-in default string)")
    parser.add_argument("--messages",type=int, default=DEF_REPT,help=f"number of messages to send (default: {DEF_REPT}, max:{MAX_REPT} )")
    parser.add_argument("--error-rate", type=float,default=DEF_RATE,help="Error injection rate, float between 0.0 and 1.0  (default: 0.0)")
    parser.add_argument("--log", default=DEF_LOG, help="Path to the output log file (default: ./client.log)")
    args = parser.parse_args()

    script_dir = Path(__file__).parent.resolve()


    if args.input:
        file_input= '/'.join([script_dir._str,args.input]) # rem script_dir is a object
        #check file exist
        try:
            f=open(file_input, encoding="utf-8") 
            try:
                t=f.read()
            except UnicodeDecodeError:
                print(f"Error: Input file \"{file_input}\" di tipo binario")
                sys.exit()
        except FileNotFoundError:
            print(f"Error: Input file \"{file_input}\" does\'nt exists.")
            sys.exit()
        
        mod= not(INTERNAL)
    else:
        mod=INTERNAL 


    log_file= '/'.join([script_dir._str,args.log]) 
    try:
        f=open(log_file,'a',  encoding="utf-8") 
    except FileNotFoundError:
        print(f"Input file \"{file_input}\" does\'nt exists.")
        sys.exit()

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


    num_msg=range_validate('--messages',args.messages,DEF_REPT,MAX_REPT)
    err_rate =range_validate('--error-rate',args.error_rate,0.0,1.0)  # !! Parser translate - with _
    # print(num_msg)
    # print(err_rate)
    # print(log_file)
    # print(file_input)
    return (num_msg, err_rate,log_file,file_input, mod)



def _dummy_rnd_gen(d:int)->(int,bool,bool):
    """
    Generates dummy pseudo-random values used by _log_test

    Parameters
    ----------
    d
        duration

    Returns
    -------
    d
        duration modified
    e_d
       detect an error
    e_c
        correct an error 
    """
    d+=random.randint(-5,5)
    e_d=random.randint(0,1)
    if e_d:
        e_c=random.randint(0,1)
    else:
        e_c=0
    return (d,e_d,e_c)

def _log_test(n_msg:int,e_rate:float, log_f:str)-> None:
    """
    Logs to log_f messages to test logger functionality

    messagge formats:
        tempo,send,n_mesg,tipo_codifica,durata_cod,err_rate 
        tempo,recv,n_mesg,tipo_codifica,durata_dec, err_ril, err_corr
    Parameters
    ----------
    n_mesg
        number of messages to log
    e_rate
        error rate
    log_f
        log file full path

    Returns
    -------
    None
    """
    # opening log
    logger = logging.getLogger(__name__) # maybe None but it's a reccommended practice maybe to distinguish logs from differente modules
    logging.basicConfig(filename=log_f, filemode='a',encoding='utf-8', \
    format='%(asctime)s,%(message)s',level=logging.INFO) # datefmt='%m/%d/%Y %I:%M:%S %p',

    for i in np.arange(n_msg):
        start=time.perf_counter_ns()
        print(f'dummy {i}')
        end=time.perf_counter_ns()
        delta=end-start
        msg=f"'send',{i},'HAM',{delta},{e_rate},NaN"
        logger.info(msg)

        delta, *rest = _dummy_rnd_gen(delta)
        msg=f"'send',{i},'LDPC',{delta},{e_rate},NaN"
        logger.info(msg)

        delta,e_detect,e_correct = _dummy_rnd_gen(delta)
        msg=f"'recv',{i},'HAM',{delta},{e_detect},{e_correct}"
        logger.info(msg)

        delta,e_detect,e_correct = _dummy_rnd_gen(delta)   
        msg=f"'recv',{i},'LDPC',{delta},{e_detect},{e_correct}"
        logger.info(msg)