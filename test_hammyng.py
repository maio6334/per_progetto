#!/usr/bin/env python3

import hamming_codec  as hc
from commonhelp  import change_1_bit, str_2_int, int_2_str


#mesg=0x777777777777
mystr="the mys"
mystr="the mysteriuos train appearing so blue in the sky"

a=[mystr[i:i+5] for i in range(0,len(mystr),5)]
c=''.join(a)

ad={i//5:mystr[i:i+5] for i in range(0,len(mystr),5)}
f=[ad[x] for x in ad]
f=''.join(f)
cd=''.join([ad[x] for x in ad])


print(ad)

exit()
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
