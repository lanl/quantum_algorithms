#!/usr/bin/env python3

# Example from https://github.com/QISKit/qiskit-sdk-py

from qiskit import QuantumProgram

# Creating Programs create your first QuantumProgram object instance.
qp = QuantumProgram()

# Creating Registers create your first Quantum Register called 'qr' with 2 qubits
qr = qp.create_quantum_register('qr', 2)
# create your first Classical Register called 'cr' with 2 bits
cr = qp.create_classical_register('cr', 2)
# Creating Circuits create your first Quantum Circuit called 'qc' involving your Quantum Register 'qr' 
# and your Classical Register 'cr'
qc = qp.create_circuit('superposition', [qr], [cr])

# add the H gate in the Qubit 0, we put this Qubit in superposition
qc.h(qr[0])
qc.y(qr[0])

# add measure to see the state
qc.measure(qr, cr)

# Compiled  and execute in the local_qasm_simulator

#print(qp.get_qasm('superposition'))

result = qp.execute(['superposition'], backend='local_qasm_simulator', shots=1)

# Show the results
print(result)
print(result.get_data('superposition'))
