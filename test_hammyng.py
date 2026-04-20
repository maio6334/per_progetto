#!/usr/bin/env python3

import hamming_codec  as hc
from commonhelp  import change_1_bit, str_2_int, int_2_str
import numpy as np

def test_max_len():
    mesg=0x0
    for i in range(32):
        mesg=(mesg<<1)+1
        l=4*(len(hex(mesg))-2) # number of bit
        print(f"i={i} msg={hex(mesg)}, l={l}")
        try:
            encoded_message = hc.encode(mesg, l)
            print(encoded_message, len(encoded_message))
        except Exception as e:
            print(f'encode failed at {l//8} bytes')
            exit()
        try:
            decoded_message = hc.decode(int(encoded_message,2), len(encoded_message))
            print(encoded_message, len(encoded_message))
        except Exception as e:
            print(f'decode failed at {l//8} bytes')
            exit()


def test_code_decode():
    """ 
    'A'  U+00041  1 byte  b'\x41'                →  01000001
    '§'  U+000A7  2 byte  b'\xc2\xa7'            →  11000010 10100111
    '€'  U+020AC  3 byte  b'\xe2\x82\xac'        →  11100010 10000010 10101100
    '𝄞'  U+1D11E  4 byte  b'\xf0\x9d\x84\x9e'   →  11110000 10011101 10000100 10011110 
    """
    text="A§€𝄞"
    #text='la pazza gioia di essere sani'
    enc=[]
    for m in range(len(text)):
        l=len(text[m].encode())*8
        print(l)
        x=ord(text[m])
        print(x)
        enc.append(hc.encode(ord(text[m]),l))
    print(enc)
    
    # error routine
    rate=0.03
    total_mess=''.join(enc)
    total_bit=len(total_mess)
    num_err=int(round(total_bit*rate,0))
    split_pos=[0]
    for i in range(len(enc)):
        split_pos.append(split_pos[i]+len(enc[i]))
    print(f'rate={rate}, total_bit={total_bit},num_err={num_err}')
    rng = np.random.default_rng(12345) # init random generator
    pos_err = rng.integers(low=0, high=total_bit-1, size=num_err)
    print(pos_err)
    # for pos in pos_err:
    #     print(f'bit flipping position={pos}')
    #     f= '1' if total_mess[pos]=='0' else '0'
    #     total_mess= total_mess[:pos] + f+ total_mess[pos+1:]
    ret_mess=[]
    for i in range(len(split_pos)):
        to=-1 if i==len(split_pos) else split_pos[i+1]
        ret_mess.append(total_mess[split_pos[i]:to])
    
    print(enc,ret,sep='\n')
    exit()
    r=[]
    for i in range(len(enc)):
        d = hc.decode(int(enc[i],2), len(enc[i]))
        r.append(chr(int(d,2)))
    
    r=''.join(r)
    print(r)
    for i in range(len(text)):
        if r[i]!=text[i]:
            print(f'ko al carattere {i}')
        

def first_test():
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


def dummy():
    exit()
    a=[mystr[i:i+5] for i in range(0,len(mystr),5)]
    c=''.join(a)

    ad={i//5:mystr[i:i+5] for i in range(0,len(mystr),5)}
    f=[ad[x] for x in ad]
    f=''.join(f)
    cd=''.join([ad[x] for x in ad])
    print(ad)
   
def main():
    #test_max_len()
    test_code_decode()
    #first_test()

if __name__ == "__main__":
    main()