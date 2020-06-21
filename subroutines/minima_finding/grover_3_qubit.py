#!/bin/env python3

from qiskit import QuantumProgram
import math
from Qconfig import api_token, url
import json

''' 3 qubit Grover's algorithm with known marked element.  I am heavily borrowing from 
https://gitlab.lanl.gov/QuantumProgramming2017/q-network-flows/blob/master/Grover/grover3.py
'''


def ccx(qc, ct1, ct2, tgt):
    '''
    Perform a control-control-not on the quantum circuit.  This switches the
    target qubit (0\mapsto 1\mapsto 0) if the first two control qubits are both 1.

    Inputs
        qc  :   the quantum circuit
        ct1 :   the first control qubit
        ct2 :   the second control qubit
        tgt :   the target qubit
    '''
    qc.h(tgt)
    qc.cx(ct2, tgt)
    qc.tdg(tgt)
    qc.cx(ct1, tgt)
    qc.t(tgt)
    qc.cx(ct2, tgt)
    qc.tdg(tgt)
    qc.cx(ct1, tgt)
    qc.t(ct2)
    qc.t(tgt)
    qc.h(tgt)
    qc.cx(ct1, ct2)
    qc.t(ct1)
    qc.tdg(ct2)
    qc.cx(ct1, ct2)

def ccz(qc, ct1, ct2, tgt):
    '''
    Perform a control-control-Z on the quantum circuit.  This changes the phase
    of the target qubit (x\mapsto -x) if the first two control qubits
    are both 1.

    Inputs
        qc  :   the quantum circuit
        ct1 :   the first control qubit
        ct2 :   the second control qubit
        tgt :   the target qubit
    '''
    qc.h(tgt)
    ccx(qc, ct1, ct2, tgt)
    qc.h(tgt)

def reflect_00(qc, qr):
    '''
    Reflect quantum register around |0>^{\bigotimes 3}.
    '''
    qc.x(qr)
    ccz(qc, qr[2], qr[1], qr[0])
    qc.x(qr)

def reflect_psipsi(qc, qr):
    '''
    Reflect quantum register around the equi-superposition state.
    '''
    qc.h(qr)
    reflect_00(qc, qr)
    qc.h(qr)

def grover_oracle_marked(qc, qr, marked):
    '''
    Perform the Grover Oracle U_f.  Let
            u:= (1/\sqrt{7})\sum_{x \ne marked} |x> and
            m:= |marked>.
    Then U_f corresponds to a rotation about |u> in the |u>, |m> plane:
    U_f: \alpha |u> + \beta |m> \mapsto \alpha |u> - \beta |m> 

    Inputs
        qc      :   the quantum circuit
        qr      :   the registers holding the quantum input
        marked  :   the marked indice in binary
    '''
    marked.reverse()
    marked.extend([0]*(3-len(marked)))
    marked.reverse()
    #print("Marked binary: %s"%marked)
    for register in range(3):
        if marked[register] == 0:
            qc.x(qr[register])
    ccz(qc, qr[2], qr[1], qr[0])
    for register in range(3):
        if marked[register] == 0:
            qc.x(qr[register])

def grover_oracle_minima(qc, qr, value):
    '''
    Perform a Grover Oracle U_f which returns (hopefully!) x \leq value.
    '''
    for i in range(0,value+1):
        marked_i = [int(b) for b in bin(i)[2:]]
        grover_oracle_marked(qc,qr,marked_i)

def grover_iteration(qc, qr, oracle, value):
    oracle(qc, qr, value)
    reflect_psipsi(qc, qr)

def grover_search(qc, qr, n_iterations, oracle, value):
    qc.h(qr)
    for i in range(0, n_iterations):
        grover_iteration(qc, qr, oracle, value=value)


if __name__ == '__main__':
    #simulator = 'ibmqx_qasm_simulator'
    #simulator = 'local_qasm_simulator'
    simulator = 'ibmqx4'
    shots = 1000
    timeout = 240
    for marked_int in range(8):
        qp = QuantumProgram()
        qr = qp.create_quantum_register("qr", 3)
        cr = qp.create_classical_register("cr", 3)
        qc = qp.create_circuit("qc", [qr], [cr])
        # build the program
        # marked search
        # algorithm = 'Grover Marked'
        # print('\nMarked: %d'%marked_int)
        # marked_binary = [int(b) for b in bin(marked_int)[2:]]
        # n = math.floor(math.pi * math.sqrt(8)/4)
        # grover_search(qc, qr, n_iterations=n, oracle=grover_oracle_marked, value=marked_binary)
        # minima search
        value = marked_int
        algorithm = 'Grover Minima'
        n = math.floor(math.pi * math.sqrt(8/(value+1)) /4)
        #n=1
        print("%s for %d with %d iterations"%(algorithm, value, n))
        grover_search(qc, qr, n_iterations=n, oracle=grover_oracle_minima, value=value)
        qc.measure(qr, cr)
        qp.set_api(api_token, url)
        # run
        result = qp.execute(["qc"], backend=simulator, shots=shots, timeout=timeout, silent=False)
        data = result.get_data("qc")
        print(data['counts'])
        data['Algorithm'] = algorithm
        data['Value'] = value
        data['simulator'] = simulator
        data['n_iterations'] = n
        with open('grover_data.json', 'a') as fh:
            print(json.dumps(data), file=fh)

