#!/usr/bin/env python

import numpy as np
from pyldpc import make_ldpc, decode, get_message, encode

   #text=read_file('inferno_c1.txt')
    #print(len(text))
    #text=text[:380]
text="A§€𝄞"
    #text='la pazza gioia di essere sani'
    #text='''Probabilmente uscì chiudendo dietro a se la porta verde
    # Qualcuno si era alzato a preparargli in fretta un caffè d'orzo
    # Non so se si girò, non era il tipo d'uomo che si perde'''

n = 30 # 30
d_v = 2
d_c = 3
seed = np.random.RandomState(42)

H, G = make_ldpc(n, d_v, d_c, seed=seed, systematic=True, sparse=True)

n, k = G.shape
print("Number of coded bits:", k)

errors = []
snrs = np.linspace(-2, 10, 20)
