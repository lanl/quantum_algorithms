#!/usr/bin/env python3

from math import pi
from qiskit import QuantumProgram

# Creating Programs create your first QuantumProgram object instance.
qp = QuantumProgram()
qr = qp.create_quantum_register('qr', 5)
cr = qp.create_classical_register('cr', 5)
qc = qp.create_circuit('qaoa', [qr], [cr])

beta = 0.0
gamma = 2.0943951023931953
beta2 = 2.0943951023931953
gamma2 = 2.0943951023931953

# p.inst(
#     H(0), H(1),

#     # B
#     RX(2*beta, 0),
#     RX(2*beta, 1),

#     # C
#     X(0), PHASE(-gamma/2.0, 0), X(0), PHASE(-gamma/2.0, 0),
#     CNOT(0, 1), X(1), PHASE(gamma/2.0, 1), X(1), PHASE(-gamma/2.0, 1), CNOT(0, 1),

#     # B
#     RX(2*beta2, 0),
#     RX(2*beta2, 1),

#     # C
#     X(0), PHASE(-gamma2/2.0, 0), X(0), PHASE(-gamma2/2.0, 0),
#     CNOT(0, 1), X(1), PHASE(gamma2/2.0, 1), X(1), PHASE(-gamma2/2.0, 1), CNOT(0, 1),

# )


qc.h(qr[0])
qc.h(qr[1])

qc.u3(2*beta, -pi/2, pi/2, qr[0])
qc.u3(2*beta, -pi/2, pi/2, qr[1])

qc.x(qr[0])
qc.u1(-gamma/2.0, qr[0])
qc.x(qr[0])
qc.u1(-gamma/2.0, qr[0])
qc.cx(qr[0], qr[1])
qc.x(qr[1])
qc.u1(gamma/2.0, qr[1])
qc.x(qr[1])
qc.u1(-gamma/2.0, qr[1])
qc.cx(qr[0], qr[1])


qc.u3(2*beta2, -pi/2, pi/2, qr[0])
qc.u3(2*beta2, -pi/2, pi/2, qr[1])

qc.x(qr[0])
qc.u1(-gamma2/2.0, qr[0])
qc.x(qr[0])
qc.u1(-gamma2/2.0, qr[0])
qc.cx(qr[0], qr[1])
qc.x(qr[1])
qc.u1(gamma2/2.0, qr[1])
qc.x(qr[1])
qc.u1(-gamma2/2.0, qr[1])
qc.cx(qr[0], qr[1])

qc.measure(qr, cr)

result = qp.execute(['qaoa'], backend='local_qasm_simulator', shots=1000)

# Show the results
print(result)
print(result.get_data('qaoa')['counts'])

print(result.get_ran_qasm('qaoa'))
