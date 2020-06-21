from qiskit import QuantumProgram
import Qconfig
import math
import numpy as np

""" 3 qbit Grover's Algorithm"""

def binary(x):
    return [int(b) for b in bin(x)[2:]]

def ccx(qc,a,b,c):
    """ CCX was not available on ibmqx4, only on the simulators"""
    qc.h(c)
    qc.cx(b, c)
    qc.tdg(c)
    qc.cx(a, c)
    qc.t(c)
    qc.cx(b, c)
    qc.tdg(c)
    qc.cx(a, c)
    qc.t(b)
    qc.t(c)
    qc.h(c)
    qc.cx(a, b)
    qc.t(a)
    qc.tdg(b)
    qc.cx(a, b)

# def cccx(qc, ctl1, ctl2, ctl3, tgt, ancilla):
#     """ 3-bit Toffoli gate using a borrowed ancilla qbit"""
#     qc.ccx(ctl1, ctl2, ancilla)
#     qc.ccx(ancilla, ctl3, tgt)
#     qc.ccx(ctl1, ctl2, ancilla)
#     qc.ccx(ancilla, ctl3, tgt)

def ccz(qc, ctl1, ctl2, tgt):
    qc.h(tgt)
    ccx(qc, ctl1, ctl2, tgt)
    qc.h(tgt)

def wbits_to_x(wbits_in, qc, x):
    wbits = wbits_in.copy()
    wbits.reverse()
    wbits.extend([0]*(3 - len(wbits)))
    #print(wbits)
    for i in range(3):
        if wbits[i] == 0:
            qc.x(x[i])

def oracle_w(w, qc, x):
    wbits = binary(w)

    wbits_to_x(wbits, qc, x)
    ccz(qc, x[2], x[1], x[0])
    wbits_to_x(wbits, qc, x)

def reflect_00(qc, qr):
    qc.x(qr)
    ccz(qc, qr[2], qr[1], qr[0])
    qc.x(qr)

def reflect_psipsi(qc, qr):
    qc.h(qr)
    reflect_00(qc, qr)
    qc.h(qr)

def grover_iter(w, qc, qr):
    oracle_w(w, qc, qr)
    reflect_psipsi(qc, qr)

def grover(w, n_iters, qc, qr):
    qc.h(qr)
    for i in range(0,n_iters):
        grover_iter(w, qc, qr)

n = 3
N = 2**n
n_iters = math.floor(math.pi * math.sqrt(N)/4)
#n_iters = 2
print('n_iters', n_iters)

qp = QuantumProgram()

qr = qp.create_quantum_register("qr", n)

cr = qp.create_classical_register("cr", n)

qc = qp.create_circuit("qc", [qr], [cr])

w = 6
print('w:', w)

grover(w, n_iters, qc, qr)
qc.measure(qr, cr)

print(qc.qasm())

#simulator = 'local_qasm_simulator'
#simulator = 'ibmqx_qasm_simulator'
simulator = 'ibmqx4'
#shots = 512*N            # Number of shots to run the program (experiment)) maximum is 8192 shots.
shots = 1000
print('shots:', shots)
max_credits = 3          # Maximum number of credits to spend on executions.
qp.set_api(Qconfig.APItoken, Qconfig.config['url']) # set the APIToken and API url

#print(qp.online_backends())
result = qp.execute(["qc"], backend=simulator, max_credits=max_credits, shots=shots, timeout=240, silent=False)

# Show the results
print(result)
result_get_data = result.get_data("qc")
print(result_get_data)

#counts = result_get_data['counts']
