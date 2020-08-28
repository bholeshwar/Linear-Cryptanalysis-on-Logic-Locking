import numpy as np
import math
import pandas as pd
import random
def binar(y,z):
    return [int(x) for x in list(bin(y).split('b')[1].zfill(z))]

def checkforone(comb,tc):
    lhs=0
    
    for i in range(15):
        #print(int(tc[i])
        lhs = int(lhs) ^ int(comb[i]*tc[i])
        
    rhs = comb[15]*tc[15]
    return int(lhs == rhs)

def check(comb,test):
    count=0
    for i in test:
        count = count + checkforone(comb,i)
        
    return count





# class circuit1:
# 	def __init__(self, x1, x2, x3, x4, x5, x6, x7)

def original(L):
    #takes as input the 10 bits of input to circuit, in order
    a1 = L[0]
    a2 = L[1]
    a3 = L[2]
    a4 = L[3]
    a5 = L[4]
    a6 = L[5]
    a7 = L[6]
    a8 = L[7]
    a9 = L[8]
    a10 = L[9]

    x1 = (a1 and a3) or ((not a2) and a4)
    x2 = (not (a5 and a3)) and (not a6)
    x3 = (not(a7 or a8)) and a9
    return ((not a10) and (x2 or x3)) or (not x1)


def circuit(L):
    #Input: first 10 elements of input list are the 10 bits of input to the circuit, next 5 bits represent the key bits
    a1 = L[0]
    a2 = L[1]
    a3 = L[2]
    a4 = L[3]
    a5 = L[4]
    a6 = L[5]
    a7 = L[6]
    a8 = L[7]
    a9 = L[8]
    a10 = L[9]
    k1 = L[10]
    k2 = L[11]
    k3 = L[12]
    k4 = L[13]
    k5 = L[14]


    x1 = ((a1 and a3) or ((not a2) and a4))^k1
    x2 = not(((not (a5 and (not(a3 ^ k2)))) and ((not a6) ^ k4))^k3)
    x3 = (not(a7 or a8)) and (a9 ^ k5)
    return ((not a10) and (x2 or x3)) or (not x1)



def generate(p, k):
    texts = np.zeros((2**(p+k), p+k+2))
    for i in range(2**15):
        binary = [int(x) for x in list(bin(i)[2:].zfill(15))]
        ptxt = binary[:p]
        key = binary[-k:]
        x = original(ptxt)
        y = circuit(ptxt + key)
        texts[i] = (np.array(ptxt + key + [y, x]))
    return np.array(texts)


def random_generate(p, k, n):
    texts = generate(p, k)
    L = np.zeros((n, 2**(p+k+2)))
    idx = np.array(np.random.permutation(2**(p+k))[:n])
    L = []
    for i in range(n):
#         L.append(texts[idx])
        L.append(np.array(texts[idx[i]]))
    return np.array(L)






test = random_generate(10,5,1000)
inlist = []
for i in range(2<<14):
    for j in [0,1]:
        x=binar(i,15)
        x.append(j)
        inlist.append(x)
       
Lat = []

for i in range(2<<15):
    if i%2 == 0:
        x = check(inlist[i],test)
        y = check(inlist[i+1],test)
        print(i,x-500,y-500)
        Lat.append([x-500,y-500])

        
#inlist

df = pd.DataFrame(Lat)
df.to_csv("LAT.csv",sep='\t')
Lat[0][0] = 0
A = np.abs(Lat)
ind = np.argmax(A)
row = int(ind/2)
col = ind%2
print(col)
print(row)


