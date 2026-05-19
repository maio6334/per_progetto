#!/usr/bin/env python3

import hashlib
import numpy as np

m1 = hashlib.sha256()
m2 = hashlib.sha256()
m3 = hashlib.sha256()
l=[10,20,30,40]
na=np.array(l)
m=memoryview(na)

m1.update(na)
m2.update(m)
m1h=m1.digest()
m2h=m2.digest()
print(m1h==m2h)