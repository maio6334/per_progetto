#!/usr/bin/env python

import numpy as np
from pyldpc import make_ldpc, decode, get_message, encode
from shared_funct import ber_to_snr

   #text=read_file('inferno_c1.txt')
    #print(len(text))
    #text=text[:380]
text="A§€𝄞"
#text='ABCDEF'
    #text='la pazza gioia di essere sani'
    #text='''Probabilmente uscì chiudendo dietro a se la porta verde
    # Qualcuno si era alzato a preparargli in fretta un caffè d'orzo
    # Non so se si girò, non era il tipo d'uomo che si perde'''

n = 21 # this must set k=8
d_v = 2
d_c = 3
seed = np.random.RandomState(42)

H, G = make_ldpc(n, d_v, d_c, seed=seed, systematic=True, sparse=True)
n,k = G.shape
print("Number of coded bits:", k)

errors = []
ber= np.linspace(0.01, 0.10 , 20)
print(ber)
snrs=[ber_to_snr(b) for b  in ber]
#print(snr)

#def char_to_bitarray(c:int)

# from text to flat array
bits=np.array([ e>>i & 1 for e in text.encode() for i in range(8)])
# split every byte into columns
bits2=bits.reshape((-1,k)).T

#code
snr=snrs[0]
y = encode(G, bits2, snr, seed=seed)
#decode
D = decode(H, y, snr)
error = 0.
x=[]
for i in range(D.shape[1]):
    x.append(get_message(G, D[:, i]))
total=np.concatenate(x) # it is flattened if  axis= none
pass
    #error += abs(v - x).sum() / (k * n_trials)
#errors.append(error)





# back to linear array
#tbits=bits2.flatten('F')
tbits=total
#print(f'bits4 {tbits}')
a=[]
a3=[]
for l in range(len(tbits)//8):
    c=tbits[l*8:8*(l+1)]
    d=0
    for i in range(8):
        d=d |(c[i]<<i)
    a.append(d)
    a3.append(int(np.packbits(c,bitorder='little'))) # int needed to cast as int otherwhise array

t=bytearray(a).decode() 
t3=bytearray(a3).decode()



exit()

v = np.arange(k) % 2  # fixed k bits message
n_trials = 5  # number of transmissions with different noise
V = np.tile(v, (n_trials, 1)).T  # stack v in columns
pass
