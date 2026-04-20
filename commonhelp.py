#!/usr/bin/env python3

import random
from pathlib import Path 

# test functions
def test_change_1_bit(t='10101010'):
    print('a=',t)
    f,p=change_1_bit(t)
    print(f'b={f}')

def test_str_2_int(a='01'):
    b,l=str_2_int(a)
    print(b,hex(b),l)

def test_int_2_str(i=6382179): #  string 'abc'
    print(int_2_str(i)) 

def test_txt_file_2_dic()->dict:
    f_dic=txt_file_2_dic()
    print(f_dic)
    return f_dic


def test_print_file_dic(fdic={1: 'appunti_progetto.txt', 2: 'snippet.txt', 3: 'due.txt', 4: 'uno.txt', 5: 'istruzioni.txt', 6: 'prove.txt', 7: 'convenzioni.txt'})->None:
    print_file_dic(fdic) 



# utils function
def txt_file_2_dic() -> dict:
    f_dic={i:f.name for i,f in enumerate(Path('.').glob('*.txt'), start=1)}
    return f_dic

def print_file_dic(f_dic:dict)-> None:
    print("file txt available, select from ID")
    print("ID\tFilename")
    for i in (f_dic):
        print(f"{i}\t{f_dic[i]}")
    

 
def int_2_str(i:int) -> str: #converts a int  in a string
    s=""
    while i>0:
        t= i & 0xFF
        s= s + chr(t)
        i= i >> 8
    return "".join(reversed(s))

def str_2_int(s:str) -> tuple[int, int]: #converts a string in a int , returns also the bit's count
    i=0
    for c in range(len(s)):
        if c!=0:
            i=i<< 8
        i+=ord(s[c]) 
    return i, len(s.encode())


def change_1_bit(s_in: str)-> tuple[str, int]: # supposing s is a string of 1,0  returns s where a bit is changed and his position in string 
    position=random.randint(0,len(s_in)-1)
    print(f'bit flipped position={position}')
    f= '1' if s_in[position]=='0' else '0'
    s_out= s_in[:position] + f+ s_in[position+1:]
    return s_out,position
# 
def verify_command(cmd: str) ->tuple[bool, str, int]: # returns True if cmd is well formed, returns also him components cm1 and cm2
    l =cmd.split(' ', maxsplit=1) # so it split maximum in 3 values list
    cmd_1=l[0]    
    if cmd_1 not in ('l','r','s','q'): #'c', not used
        return False,0 ,0
    elif cmd_1 in ('s'): # needs 2 param , 'c' not used
        if len(l)>1:
            cmd_2=l[1]
            if not(cmd_2.isdigit()): 
                return False, 0, 0
        else:  # insufficient parameters
            return False, 0, 0
    else: #  only first value needed
        cmd_2=0
    return True, cmd_1, int(cmd_2)



#testing

# test_change_1_bit()
# test_str_2_int()
# test_int_2_str()
# test_txt_file_2_dic()
# test_print_file_dic()