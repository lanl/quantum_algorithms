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

# Good values of beta,gamma
# 0.0 ,  2.094  :  2.094 ,  2.094


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
                    #CNOT(0, 1), RZ(-gamma, 1), CNOT(0, 1),
                    #CNOT(0, 1), X(1), PHASE(gamma/2.0, 1), X(1), PHASE(-gamma/2.0, 1), CNOT(0, 1),
                    CNOT(1, 0), X(1), PHASE(gamma/2.0, 1), X(1), PHASE(-gamma/2.0, 1), CNOT(1, 0),

                    # B
                    RX(2*beta2, 0),
                    RX(2*beta2, 1),

                    # C
                    X(0), PHASE(-gamma2/2.0, 0), X(0), PHASE(-gamma2/2.0, 0), # math.pi/2.0 * B_1
                    #CNOT(0, 1), RZ(-gamma2, 1), CNOT(0, 1),
                    #CNOT(0, 1), X(1), PHASE(gamma2/2.0, 1), X(1), PHASE(-gamma2/2.0, 1), CNOT(0, 1),
                    CNOT(1, 0), X(1), PHASE(gamma2/2.0, 1), X(1), PHASE(-gamma2/2.0, 1), CNOT(1, 0),

                    #MEASURE(0, 0),
                    #MEASURE(1, 1)
                )

                print('')
                print('')
                print(beta, ', ', gamma, ' : ', beta2, ', ', gamma2)

                print(p)
                #print('')

                wf = qvm.wavefunction(p)
                print(wf)
                #print(wf.amplitudes)

                disp_format = '{0:0'+str(n_qubits)+'b}'
                for state_index in range(2**n_qubits):
                    print(disp_format.format(state_index), np.conj(wf[state_index])*wf[state_index])

                # result = qvm.run(p, [0, 1], 1000)
                # #print(result)
                # state_count = {}
                # for state in result:
                #     k = tuple(state)
                #     if not k in state_count:
                #         state_count[k] = 0
                #     state_count[k] = state_count[k] + 1

                # print('')
                # for k in sorted(state_count.keys()):
                #     print(k,' ',state_count[k]/len(result))


