from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit import Aer, execute

n_steps =  4          #Number of steps

#Defining the shift gate

shift_q =  QuantumRegister(3)                               #3 qubit register
shift_circ = QuantumCircuit (shift_q, name='shift_circ')    #Circuit for shift operator
shift_circ.ccx (shift_q[0],  shift_q[1], shift_q[2])        #Toffoli gate
shift_circ.cx ( shift_q[0], shift_q[1] )                    #CNOT gate
shift_circ.x ( shift_q[0] )
shift_circ.x ( shift_q[1] )
shift_circ.ccx (shift_q[0],  shift_q[1], shift_q[2])
shift_circ.x ( shift_q[1] )
shift_circ.cx ( shift_q[0], shift_q[1] )

shift_gate = shift_circ.to_instruction()          #Convert the circuit to a gate

q = QuantumRegister (3, name='q')                 #3 qubit register
c = ClassicalRegister (3, name='c')               #3 bit classical register
circ = QuantumCircuit (q,c)                       #Main circuit
for i in range(n_steps):
    circ.h (q[0])                                 #Coin step
    circ.append (shift_gate, [q[0],q[1],q[2]])    #Shift step
    
circ.measure ([q[0],q[1],q[2]], [c[0],c[1],c[2]]) 







