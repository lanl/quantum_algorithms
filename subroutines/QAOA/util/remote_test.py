#!/usr/bin/env python3

# Example from https://github.com/QISKit/qiskit-sdk-py

import json
from qiskit import QuantumProgram

with open('_config') as data_file:    
    config = json.load(data_file)
assert('qx_token' in config)
assert('qx_url' in config)

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

# add measure to see the state
qc.measure(qr, cr)

# Compiled  and execute in the local_qasm_simulator

qp.set_api(config['qx_token'], config['qx_url'])
print('backends: {}'.format(qp.available_backends()))

result = qp.execute(['superposition'], backend='ibmqx_qasm_simulator', shots=1000)

# Show the results
print(result)
print(result.get_data('superposition'))

