from qiskit import QuantumProgram
import json

with open("config.json") as configfile:
    config = json.load(configfile)

Q = QuantumProgram()
Q.set_api(config["mytoken"], config["url"])
qr = Q.create_quantum_register("qr", 3)
cr = Q.create_classical_register("cr", 3)
qc = Q.create_circuit("andgate", [qr], [cr])

def tiffoli(qc, r0, r1, r2):
    qc.h(r2)
    qc.cx(r1, r2)
    qc.tdg(r2)
    qc.cx(r0, r2)
    qc.t(r2)
    qc.cx(r1, r2)
    qc.tdg(r2)
    qc.cx(r0, r2)
    qc.t(r1)
    qc.t(r2)
    qc.h(r2)
    qc.cx(r1, r2)
    qc.h(r1)
    qc.h(r2)
    qc.cx(r1, r2)
    qc.h(r1)
    qc.h(r2)
    qc.cx(r1, r2)
    qc.cx(r0, r2)
    qc.t(r0)
    qc.tdg(r2)
    qc.cx(r0, r2)
    qc.cx(r1, r2)
    #instead of the qc.cx(r2, r1) below, we use 4 hadamard gates and a cx(r1, r2)
    qc.h(r1)
    qc.h(r2)
    qc.cx(r1, r2)
    qc.h(r1)
    qc.h(r2)
    #qc.cx(r2, r1)
    qc.cx(r1, r2)

def testtiffolihelper(tiffun, rs):
    Q = QuantumProgram()
    qr = Q.create_quantum_register("qr", 3)
    cr = Q.create_classical_register("cr", 3)
    qc = Q.create_circuit("tiffolitest", [qr], [cr])
    if rs[2] == 1:
        goodresult = str(1 - rs[1] * rs[0]) + str(rs[1]) + str(rs[0])
    else:
        goodresult = str(rs[1] * rs[0]) + str(rs[1]) + str(rs[0])
    for i in range(3):
        if rs[i] == 1:
            qc.x(qr[i])
    tiffun(qc, qr[0], qr[1], qr[2])
    qc.measure(qr, cr)
    result = Q.execute(["tiffolitest"], backend="local_qasm_simulator", shots=100).get_data("tiffolitest")
    return goodresult in result["counts"] and result["counts"][goodresult] == 100

def testtiffoli(tifffun):
    testtiffolihelper(tifffun, [0, 0, 0]) or print("test tiffloi failed at 0")
    testtiffolihelper(tifffun, [0, 0, 1]) or print("test tiffloi failed at 1")
    testtiffolihelper(tifffun, [0, 1, 0]) or print("test tiffloi failed at 2")
    testtiffolihelper(tifffun, [0, 1, 1]) or print("test tiffloi failed at 3")
    testtiffolihelper(tifffun, [1, 0, 0]) or print("test tiffloi failed at 4")
    testtiffolihelper(tifffun, [1, 0, 1]) or print("test tiffloi failed at 5")
    testtiffolihelper(tifffun, [1, 1, 0]) or print("test tiffloi failed at 6")
    testtiffolihelper(tifffun, [1, 1, 1]) or print("test tiffloi failed at 7")

def grover(oracle, qc, x0, x1, q):
    #this implements the oracle
    oracle(qc, x0, x1, q)
    #now implement the grover operator
    qc.h(x0)
    qc.h(x1)
    qc.x(x0)
    qc.x(x1)
    qc.h(x1)
    qc.cx(x0, x1)
    qc.h(x1)
    qc.x(x0)
    qc.x(x1)
    qc.h(x0)
    qc.h(x1)
    qc.h(q)

testtiffoli(tiffoli)

b0 = qr[2]
b1 = qr[1]
b2 = qr[0]
qc.x(b2)#put b2 in state |1>
qc.h(b0)#put b0 in (|0>+|1>)/sqrt(2)
qc.h(b1)#put b1 in (|0>+|1>)/sqrt(2)
qc.h(b2)#put b2 in state (|0>-|1>)/sqrt(2)
for i in range(1):#apply the oracle/grover operator in a loop
    grover(tiffoli, qc, b0, b1, b2)
qc.measure(qr, cr)
print(Q.get_qasm("andgate"))
print(Q.available_backends())
#result = Q.execute(["andgate"], backend="ibmqx_qasm_simulator", shots=1024)
result = Q.execute(["andgate"], backend="ibmqx4", shots=1024)
print(result)
print(result.get_data("andgate"))
