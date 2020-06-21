#!/usr/bin/env python3
def frange(start, stop, steps):
    inc = (stop-start)/float(steps)
    i = start
    while i < stop:
        yield i
        i += inc

import math
import numpy as np
import pyquil.quil as pq
import pyquil.api as api
from pyquil.gates import *
qvm = api.QVMConnection()

#beta = 0.5
# gamma = 1.3

# for beta in frange(0.0, math.pi, 5):
#     for gamma in frange(0.0, 2*math.pi, 5):
#         n_qubits = 2
#         p = pq.Program()
#         p.inst(
#             #H(0), H(1),
#             H(0), RZ(beta, 0), H(0),
#             H(1), RZ(beta, 1), H(1),
#             X(0), PHASE(gamma/2, 0),
#             X(0), PHASE(gamma/2, 0),
#             CNOT(0, 1), RZ(gamma/2, 1), CNOT(0, 1)
#         )

#         #print(p)
#         print('')
#         print(beta, ' ', gamma)
#         wf = qvm.wavefunction(p)
#         print(wf)
#         #print(wf.amplitudes)
#         for state_index in range(2**n_qubits):
#             print(state_index, np.conj(wf[state_index])*wf[state_index])
#         #print(qvm.run(p, [0, 1], 100))

# beta = 0.5
# gamma = 0.5#math.pi*3/2


# n_qubits = 2
# p = pq.Program()
# p.inst(
#     H(0), H(1),
#     #, X(1), X(2), X(3),
#     #NOT(0)#, NOT(1)
#     #X(0),

#     # X(0), PHASE(math.pi/2, 0),
#     # X(0), PHASE(math.pi/2, 0),
#     # CNOT(0, 1), RZ(math.pi/2, 1), 
#     # CNOT(0, 1)
#     #X(1),

#     # B (WORKING!)
#     RX(2*beta, 0),
#     RX(2*beta, 1),

#     # C
#     #X(1),X(1),
#     #X(0), PHASE(gamma/2.0, 0), X(0), PHASE(gamma/2.0, 0), # math.pi/2.0 * B_1
#     #X(1), PHASE(gamma/2.0, 1), X(1), PHASE(gamma/2.0, 1), # math.pi/2.0 * B_1
#     #RZ(-gamma, 0), RZ(-gamma, 1),

#     #C (WORKING!)
#     #X(1),X(0),
#     X(0), PHASE(-gamma/2.0, 0), X(0), PHASE(-gamma/2.0, 0), # math.pi/2.0 * B_1
#     CNOT(0, 1), RZ(-gamma, 1), CNOT(0, 1)

#     #PHASE(gamma/2.0, 0)
#     #RZ(gamma, 0)
# )

# #print(p)
# print('')
# #print(beta, ' ', gamma)
# wf = qvm.wavefunction(p)
# print(wf)
# #print(wf.amplitudes)
# for state_index in range(2**n_qubits):
#     print(state_index+1, np.conj(wf[state_index])*wf[state_index])
# #print(qvm.run(p, [0, 1], 100))


# # WORKING
# for beta in frange(0.0, math.pi, 10):
#     for gamma in frange(0.0, 2*math.pi, 10):
#         n_qubits = 2
#         p = pq.Program()
#         p.inst(
#             H(0), H(1),

#             # B
#             RX(2*beta, 0),
#             RX(2*beta, 1),

#             # C
#             X(0), PHASE(-gamma/2.0, 0), X(0), PHASE(-gamma/2.0, 0), # math.pi/2.0 * B_1
#             CNOT(0, 1), RZ(-gamma, 1), CNOT(0, 1),
#         )

#         #print(p)
#         print('')
#         #print(beta, ' ', gamma)
#         wf = qvm.wavefunction(p)
#         print(wf)
#         #print(wf.amplitudes)
#         for state_index in range(2**n_qubits):
#             print(state_index+1, np.conj(wf[state_index])*wf[state_index])
#         #print(qvm.run(p, [0, 1], 100))


# WORKING
for beta in frange(0.0, math.pi, 3):
    for gamma in frange(0.0, 2*math.pi, 3):
        for beta2 in frange(0.0, math.pi, 3):
            for gamma2 in frange(0.0, 2*math.pi, 3):
                n_qubits = 2
                p = pq.Program()
                p.inst(
                    H(0), H(1),

                    # B
                    RX(2*beta, 0),
                    RX(2*beta, 1),

                    # C
                    X(0), PHASE(-gamma/2.0, 0), X(0), PHASE(-gamma/2.0, 0), # scale matrix by -gamma/2
                    CNOT(0, 1), RZ(-gamma, 1), CNOT(0, 1),

                    # B
                    RX(2*beta2, 0),
                    RX(2*beta2, 1),

                    # C
                    X(0), PHASE(-gamma2/2.0, 0), X(0), PHASE(-gamma2/2.0, 0), # math.pi/2.0 * B_1
                    CNOT(0, 1), RZ(-gamma2, 1), CNOT(0, 1)
                )

                #print(p)
                print('')
                #print(beta, ' ', gamma)
                wf = qvm.wavefunction(p)
                print(wf)
                #print(wf.amplitudes)
                disp_format = '{0:0'+str(n_qubits)+'b}'
                for state_index in range(2**n_qubits):
                    print(disp_format.format(state_index), np.conj(wf[state_index])*wf[state_index])
                #print(qvm.run(p, [0, 1], 100))

