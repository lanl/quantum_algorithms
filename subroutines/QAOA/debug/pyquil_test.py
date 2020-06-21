#!/usr/bin/env python3

from math import pi
import numpy as np
import pyquil.quil as pq
import pyquil.api as api
from pyquil.gates import *
qvm = api.QVMConnection()
p = pq.Program()

#p.inst(H(0), CNOT(0, 1), MEASURE(0, 0), MEASURE(1, 1))

n_qubits = 2
beta = 0.5
gamma = 2.094

#p.inst( RX(beta, 0) )
#p.inst( H(0), PHASE(3.1415/2, 0), RX(beta, 0) )
#p.inst( H(0), PHASE(1.2, 0), H(0) )
#p.inst( H(0), RZ(-gamma, 0), H(0), MEASURE(0, 0) )
#p.inst( X(1), CNOT(0,1))

# good
# p.inst(
#     H(0), H(1),
#     RX(0,0), 
#     RX(0,1),
#     X(0), PHASE(-pi/3, 0), X(0), PHASE(-pi/3,0),
#     CNOT(0,1),
#     X(1), PHASE(pi/3,1), X(1), PHASE(-pi/3,1),
#     CNOT(0,1)
# )

# #good
# p.inst(
#     #H(0), H(1),
#     X(1),
#     RX(4*pi/3,0), 
#     RX(4*pi/3,1),
#     X(0), PHASE(-pi/3, 0), X(0), PHASE(-pi/3,0),
#     CNOT(0,1),
#     X(1), PHASE(pi/3,1), X(1), PHASE(-pi/3,1),
#     CNOT(0,1)
# )
# print(p)


# p.inst(
#     H(0), H(1),

#     # B
#     RX(2*beta, 0),
#     RX(2*beta, 1),

#     # C
#     X(0), PHASE(-gamma/2.0, 0), X(0), PHASE(-gamma/2.0, 0), # scale matrix by -gamma/2
#     CNOT(0, 1), RZ(-gamma, 1), CNOT(0, 1),

#     # B
#     RX(2*beta2, 0),
#     RX(2*beta2, 1),

#     # C
#     X(0), PHASE(-gamma2/2.0, 0), X(0), PHASE(-gamma2/2.0, 0), # math.pi/2.0 * B_1
#     CNOT(0, 1), RZ(-gamma2, 1), CNOT(0, 1),

#     MEASURE(0, 0), MEASURE(1, 1)
# )

# wf = qvm.wavefunction(p)
# print(wf)

# disp_format = '{0:0'+str(n_qubits)+'b}'
# for state_index in range(2**n_qubits):
#     print(disp_format.format(state_index), np.conj(wf[state_index])*wf[state_index])

result = qvm.run(p, [0], 1000)

state_count = {}
for state in result:
    k = tuple(state)
    if not k in state_count:
        state_count[k] = 0
    state_count[k] = state_count[k] + 1

for k in sorted(state_count.keys()):
    print(k,' ',state_count[k]/len(result))
