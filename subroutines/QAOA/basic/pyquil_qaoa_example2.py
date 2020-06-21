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

# WORKING
for beta in frange(0.0, math.pi, 5):
    for gamma in frange(0.0, 2*math.pi, 5):
        for beta2 in frange(0.0, math.pi, 5):
            for gamma2 in frange(0.0, 2*math.pi, 5):
                n_qubits = 3
                p = pq.Program()
                p.inst(
                    H(0), H(1), H(2),

                    # B
                    RX(2*beta, 0),
                    RX(2*beta, 1),
                    RX(2*beta, 2),

                    # C
                    X(0), PHASE(-gamma/2.0, 0), X(0), PHASE(-gamma/2.0, 0), # scale matrix by -gamma/2
                    CNOT(0, 1), RZ(-gamma, 1), CNOT(0, 1),

                    X(1), PHASE(-gamma/2.0, 1), X(1), PHASE(-gamma/2.0, 1), # scale matrix by -gamma/2
                    CNOT(1, 2), RZ(-gamma, 2), CNOT(1, 2),

                    X(2), PHASE(-gamma/2.0, 2), X(2), PHASE(-gamma/2.0, 2), # scale matrix by -gamma/2
                    CNOT(2, 0), RZ(-gamma, 0), CNOT(2, 0),

                    # B
                    RX(2*beta2, 0),
                    RX(2*beta2, 1),
                    RX(2*beta2, 2),

                    # C
                    X(0), PHASE(-gamma2/2.0, 0), X(0), PHASE(-gamma2/2.0, 0), # math.pi/2.0 * B_1
                    CNOT(0, 1), RZ(-gamma2, 1), CNOT(0, 1),

                    X(1), PHASE(-gamma2/2.0, 1), X(1), PHASE(-gamma2/2.0, 1), # math.pi/2.0 * B_1
                    CNOT(1, 2), RZ(-gamma2, 2), CNOT(1, 2),

                    X(2), PHASE(-gamma2/2.0, 2), X(2), PHASE(-gamma2/2.0, 2), # math.pi/2.0 * B_1
                    CNOT(2, 0), RZ(-gamma2, 0), CNOT(2, 0)
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

