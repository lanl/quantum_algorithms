import numpy as np
from math import sqrt
import scipy.linalg

"""See https://quantumexperience.ng.bluemix.net/qx/tutorial?sectionId=8443c4f713521c10b1a56a533958286b&pageIndex=1"""

I = np.eye(2)
Zero = np.zeros_like(I)

H = 1./sqrt(2.0) * np.mat('1 1; 1 -1')
X = np.mat('0 1; 1 0')
Y = 1j * np.mat('0 -1; 1 0')
Z = np.mat('1 0; 0 -1')
S = np.mat([[1,0],[0,1j]])
Sdag = np.conj(S)
#T = np.mat([[1,0],[0,(1+1j)/sqrt(2)]])
T = np.mat([[1,0],[0,np.exp(1j*np.pi/4)]])
Tdag = np.conj(T)

# Controlled-Not, or Controlled-X
CX12 = np.mat([[1,0,0,0],[0,0,0,1],[0,0,1,0],[0,1,0,0]])

# Controlled-Z
CZ12 = np.kron(H,I)*CX12*np.kron(H,I)
Z2 = np.kron(H,I)*np.kron(X,I)*np.kron(H,I)

A = np.exp(3j*np.pi/8)*X*S*H*T*H*Sdag
B = np.exp(-1j*np.pi/8)*S*H*Tdag*H*Sdag*H*S*H
C = np.exp(-1j*np.pi/4)*H*S*H
alpha = np.mat([[1,0],[0,-1j]])
CH12 = np.kron(A,alpha)*CZ12*np.kron(B,I)*CZ12*np.kron(C,I)
#CH12 = np.kron(X*S*H*T,I)*CX12*np.kron(T*H,I)*CX12*np.kron(Sdag*H,S)

print()
print('CH12')
print(np.round(CH12,decimals=4))

# testing the Controlled-Hadamard gate, CH12

up = np.mat([1,0]).T
down = X*up

q1 = up
q2 = up
q12 = np.kron(q2,q1)
print()
print('q12')
print(q12)
print(np.round(CH12*q12,decimals=4))
print(np.round(np.kron(H*q2,q1),decimals=4))

q1 = down
q2 = up
q12 = np.kron(q2,q1)
print()
print('q12')
print(q12)
print(np.round(CH12*q12,decimals=4))
print(np.round(np.kron(H*q2,q1),decimals=4))

# Approximate sqrt(T)

sqrtT = H * T * H * T * H * S * T * H * T * H * S * T * H * T * H * T * H
global_phase = sqrtT[0,0]
print('global_phase: ', global_phase)
sqrtT = sqrtT / global_phase

print()
print('sqrtT')
print(sqrtT)
#print('sqrtT^2')
#print(sqrtT*sqrtT)
#print('T')
#print(T)

#this prints the sqrt of all of T's entries, not the sqrt(T)
#print(np.sqrt(T))

print('scipy.linalg.sqrtm(T)')
print(scipy.linalg.sqrtm(T))

