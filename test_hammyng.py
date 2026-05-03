#!/usr/bin/env python3

import hamming_codec  as hc
from commonhelp  import change_1_bit, str_2_int, int_2_str
from shared_funct import enc_str_to_list, msg_with_errors, dec_list_to_str,\
                        diff_in_mess, log

import numpy as np

def _max_len_supported():
    """
    Encode/decode strings with increasing lenght until excepetion raised to check function limits

    Parameters
    ----------
    None

    Returns
    -------
    None
    """
    mesg=0x0
    for i in range(60):
        mesg=(mesg<<1)+1
        l=4*(len(hex(mesg))-2) # number of bit
        print(f"i={i} msg={hex(mesg)}, l={l}")
        try:
            encoded_message = hc.encode(mesg, l)
            print(encoded_message, len(encoded_message))
        except Exception as e:
            print(f'encode failed at {(i+1)//8} bytes')
            exit()
        try:
            decoded_message = hc.decode(int(encoded_message,2), len(encoded_message))
            print(encoded_message, len(encoded_message))
        except Exception as e:
            print(f'decode failed at {(i+1)//8} bytes')
            #exit()


def _test_code_decode():
    """
    Test encoding decoding strategy before splitting in subroutines


    Parameters
    ----------
    None

    Returns
    -------
    None
    """
   
   
    """ 
    Use case selected to test utf-8 full range
    'A'  U+00041  1 byte  b'\x41'                →  01000001
    '§'  U+000A7  2 byte  b'\xc2\xa7'            →  11000010 10100111
    '€'  U+020AC  3 byte  b'\xe2\x82\xac'        →  11100010 10000010 10101100
    '𝄞'  U+1D11E  4 byte  b'\xf0\x9d\x84\x9e'   →  11110000 10011101 10000100 10011110 
    """
    text="A§€𝄞"
    #text='la pazza gioia di essere sani'
#     text='''Probabilmente uscì chiudendo dietro a se la porta verde
# Qualcuno si era alzato a preparargli in fretta un caffè d'orzo
# Non so se si girò, non era il tipo d'uomo che si perde'''
    #encode
    enc, avg_te= enc_str_to_list(text)
    
    #print(enc)
    # inserting errors
    rate=0.04
    ret_mess, flipped=msg_with_errors(rate, enc)
    #decode
    r_text, avg_td= dec_list_to_str(ret_mess)

    #print(r_text)
    diff=diff_in_mess(text,r_text)
    print(f'detected {diff} diff  in {len(text)} chars')
    event={}
    event['coding']='HAM'
    event['avg_td']=avg_td
    event['avg_te']=avg_te
    event['rate']=rate
    event['diff']=diff
    #['HAM',avg_te,avg_td,rate,diff]
    log(event,"test.csv" )

def _first_test():
    """
    First use coding - decoding

    ----------
    None

    Returns
    -------
    None
    """
    mystr="the mys"

    mesg, l =str_2_int(mystr)
    print(mystr,mesg)
    #encoded_message = hamming_codec.encode(0x4235, 16)
    encoded_message = hc.encode(mesg, l)
    print('ok=',encoded_message, len(encoded_message))

    msgerr, p=change_1_bit(encoded_message)
    print('ko=',msgerr, len(msgerr))
    print(encoded_message, len(encoded_message))
    decoded_message = hc.decode(int(encoded_message,2), len(encoded_message))
    decoded_msgerr =  hc.decode(int(msgerr,2), len(msgerr))
    print(decoded_message)
    print(decoded_msgerr)

    #hex(int(decoded_message,2))
    print("decode hex e int",hex(int(decoded_message,2)),int(decoded_message,2))
    final=int_2_str(int(decoded_message,2))
    final2=int_2_str(int(decoded_msgerr,2))
    print(final)
    print(final2)


   
def main():
    pass
    #_max_len_supported() # ok
    _test_code_decode() # ok
    #_first_test()

if __name__ == "__main__":
    main()