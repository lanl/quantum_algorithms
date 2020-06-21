import numpy as np
from math import sqrt

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

# testing

def printQBs(q1,q2):
    print('q1')
    print(q1)
    print('q2')
    print(q2)

def test(q1,q2,Or):
    q12 = np.kron(q1,q2)
    print()
    printQBs(q1,q2)
    print('q12')
    print(q12)
    print('res')
    print (Or*q12)

X1 = np.kron(X,I)
X2 = np.kron(I,X)

#Or = X1*X2*CZ12*X2*X1 # A=00
Or = X1*CZ12*X1 # A=01
#Or = X2*CZ12*X2 # A=10
#Or = CZ12 # A=11

print()
print(Or)

up = np.mat([1,0]).T
down = X*up

#0 A=00
q1 = up
q2 = up
test(q1,q2,Or)

#1 A=01
q1 = up
q2 = down
test(q1,q2,Or)

#2 A=10
q1 = down
q2 = up
test(q1,q2,Or)

#3 A=11
q1 = down
q2 = down
test(q1,q2,Or)