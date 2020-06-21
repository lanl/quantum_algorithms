"""
findperiod.py

This python script is a first attempt to implement
quantum phase estimation to find the period of (a % N)
"""

#======================================================================#
#------------------------- Prepare Environment ------------------------#
#======================================================================#

# Checking the version of Python;
# The Quantum Experience currently only supports version 3
import sys
if sys.version_info < (3,0):
    raise Exception("Please use Python version 3 or greater.")
    
# Importing QISKit
import math
import sys
import numpy
from fractions import gcd
#sys.path.append("/Users/rzamora/qiskit-sdk-py/")
from qiskit import QuantumCircuit, QuantumProgram
import Qconfig

# Import basic plotting tools
from qiskit.tools.visualization import plot_histogram

#======================================================================#
#----------------------- Define Helper Functions ----------------------#
#======================================================================#

# Define a function to perform Cx%M, (Assume M=15, for now)
def CxModM(circ, qr1, q, p, C, M, t_, n_):
    """
    Apply Cx%M circuit with control qubit (qr1[p])
    circ - QISKit Circuit to use
    qr1  - Quantum CONTROL register
    q    - Quantum COMPUTE register
    p    - C indice: C = a^(2^p)
    C    - Multiplication Constant
    M    - Modulo Integer (Must be 15 for now)
    t_   - Num qubits in CONTROL register
    n_   - Num qubits in COMPUTE register
    """
    
    i = t_-1-p  # (using i in case I need to reverse order later)
    
    if(M==15):
    
        if(gcd(C,M) != 1):
            print("ERROR -- gcd(C,M) != 1!!")
            sys.exit(1)
        
        elif(C==1): return

        elif(C==2):
            # 0 <-> 3:
            circ.cswap(qr1[i],q[3],q[0])
            # 0 <-> 1:
            circ.cswap(qr1[i],q[1],q[0])
            # 1 <-> 2:
            circ.cswap(qr1[i],q[2],q[1])

        elif(C==4):
            # 0 <-> 2
            circ.cswap(qr1[i],q[2],q[0])
            # 1 <-> 3
            circ.cswap(qr1[i],q[3],q[1])

        elif(C==7):
            # X^n:
            for j in range(n_): circ.cx(qr1[i],q[j])
            # 1 <-> 2:
            circ.cswap(qr1[i],q[2],q[1])
            # 0 <-> 1:
            circ.cswap(qr1[i],q[1],q[0])
            # 0 <-> 3:
            circ.cswap(qr1[i],q[3],q[0])
        
        elif(C==8):
            # 0 <-> 1:
            circ.cswap(qr1[i],q[1],q[0])
            # 0 <-> 2:
            circ.cswap(qr1[i],q[2],q[0])
            # 0 <-> 3:
            circ.cswap(qr1[i],q[3],q[0])
        
        elif(C==11):
            # X^n:
            for j in range(n_): circ.cx(qr1[i],q[j])
            # 0 <-> 2:
            circ.cswap(qr1[i],q[2],q[0])
            # 1 <-> 3:
            circ.cswap(qr1[i],q[3],q[1])
        
        elif(C==13):
            # X^n:
            for j in range(n_): circ.cx(qr1[i],q[j])
            # 0 <-> 3:
            circ.cswap(qr1[i],q[3],q[0])
            # 0 <-> 1:
            circ.cswap(qr1[i],q[1],q[0])
            # 1 <-> 2:
            circ.cswap(qr1[i],q[2],q[1])

        elif(C==14):
            # X^n:
            for j in range(n_): circ.cx(qr1[i],q[j])

        else:
            print("ERROR -- C doesn't make sense!?")
            sys.exit(1)

    else:
        print("ERROR -- M must be 15 for now!!")
        sys.exit(1)

# Define a function to perform the INVERSE QFT
def qft_inv(circ, q, n_):
    """
    n-qubit QFT on q in circ.
    circ - QISKit Circuit to use
    q    - Quantum register
    n_   - number of qubits
    """
    
    #for j in range(n_):
    #    k = n_-1-j
    #    if(j!=k): circ.swap(q[j],q[k])
    
    for j in range(n_-1,-1,-1):
        circ.h(q[j])
        for k in range(j-1,-1,-1):
            circ.cu1(math.pi/float(2**(j-k)), q[j], q[k]).inverse()

def qft(circ, q, n_):
    """
    n-qubit QFT on q in circ.
    circ - QISKit Circuit to use
    q    - Quantum register
    n_   - number of qubits
    """
    for j in range(n_):
        for k in range(j):
            circ.cu1(math.pi/float(2**(j-k)), q[j], q[k])
        circ.h(q[j])

# Extended Euclidean
# (source: https://github.com/toddwildey/shors-python )
def extendedGCD(a, b):
	fractions = []
	while b != 0:
		fractions.append(a // b)
		tA = a % b
		a = b
		b = tA
	return fractions

# Continued Fractions
# (source: https://github.com/toddwildey/shors-python )
def cf(y, Q, N):
	fractions = extendedGCD(y, Q)
	depth = 2
	def partial(fractions, depth):
		c = 0
		r = 1
		for i in reversed(range(depth)):
			tR = fractions[i] * r + c
			c = r
			r = tR
		return c
	r = 0
	for d in range(depth, len(fractions) + 1):
		tR = partial(fractions, d)
		if tR == r or tR >= N:
			return r
		r = tR
	return r

#======================================================================#
#-------------------------- Quantum Program ---------------------------#
#======================================================================#
def findperiod(a, N, n):

    # Finding period (r) of a % N, with N=15
    n_qr1    = 2*n
    n_qr2    = n

    # Create QuantumProgram object, and set the APIToken and API url
    Q_program = QuantumProgram()
    Q_program.set_api(Qconfig.APItoken, Qconfig.config["url"])

    # Define quantum (q) and classical (c) registers,
    # and create the qft3 circuit
    qr1 = Q_program.create_quantum_register("qr1", n_qr1)
    qr2 = Q_program.create_quantum_register("qr2", n_qr2)
    cr1 = Q_program.create_classical_register("cr1", n_qr1)
    #cr2 = Q_program.create_classical_register("cr2", n_qr2)
    cmod15 = Q_program.create_circuit("cmod15", [qr1, qr2], [cr1])

    # Prepare the intput state of the controling register
    # by applying a hadamard to each qubit
    for j in range(n_qr1): cmod15.h(qr1[j])
    #cmod15.x(qr1[n_qr1-1])
    #cmod15.x(qr1[n_qr1-2])
    #cmod15.x(qr1[n_qr1-3])
    #cmod15.x(qr1[n_qr1-4])

    # Prepare the input state of the second register (state |1>)
    cmod15.x(qr2[n_qr2-1])
    #cmod15.x(qr2[n_qr2-2])
    #cmod15.x(qr2[n_qr2-3])
    #cmod15.x(qr2[n_qr2-4])

    # Loop
    for p in range(n_qr1):

        # Calculate next 'b' in the Ub to apply
        # ( Note: b = a^(2^p) % N )
        b = pow(a,pow(2,p),N)
        
        # Apply Ub:
        CxModM(cmod15, qr1, qr2, p, b, N, n_qr1, n_qr2)

    # Perform inverse QFT on first register
    qft_inv(cmod15, qr1, n_qr1)

    # Measure each qubit, storing the result in the classical register
    for i in range(n_qr1): cmod15.measure(qr1[i], cr1[i])
    #for i in range(n_qr2): cmod15.measure(qr2[i], cr2[i])

    # Print the QASM code to actually execute
    # (This QASM code is generated by qiskit)
    print("\nQASM Code to be executed by the local_qasm_simulator:\n")
    print(cmod15.qasm())

    if False:
        # Simulate the execution of the qft3 circuit
        simulate = Q_program.execute(["cmod15"], backend="local_qasm_simulator", shots=1024)
        # Print the result of the simulation
        print("Simulation Result:")
        print(simulate.get_counts("cmod15"))
        result = simulate.get_counts("cmod15")
    
    elif True:
        # Simulate the execution of the qft3 circuit
        simulate = Q_program.execute(["cmod15"], backend="ibmqx_qasm_simulator", shots=1024)
        
        # Print the result of the simulation
        print("Simulation Result:")
        print(simulate.get_counts("cmod15"))
        result = simulate.get_counts("cmod15")

        # Plot a histogram of the results
        plot_histogram(simulate.get_counts("cmod15"))

    else:
        if (a==7):
            result = {'10000000': 4, '10000001': 2, '10000010': 2, '10000011': 2, '10000100': 1, '10000110': 2, '10000111': 1, '10001000': 2, '10001001': 1, '10001010': 1, '10001011': 1, '10001100': 1, '10001110': 4, '10001111': 4, '10010000': 1, '10010001': 2, '10010010': 2, '10010100': 4, '10010101': 1, '10010110': 1, '10010111': 4, '10011000': 1, '10011001': 1, '10011011': 2, '10011100': 4, '10011101': 3, '10011110': 7, '10011111': 4, '10100000': 4, '10100001': 4, '10100010': 3, '10100011': 2, '10100101': 2, '10100110': 1, '10100111': 4, '10101000': 1, '10101010': 2, '10101011': 1, '10101100': 3, '10101110': 2, '10101111': 4, '10110000': 5, '10110001': 3, '10110010': 7, '10110011': 8, '10110100': 2, '10110110': 2, '10110111': 6, '10111000': 8, '10111001': 3, '10111010': 2, '10111011': 5, '10111100': 7, '10111101': 9, '10111110': 32, '10111111': 42, '11000000': 5, '11000001': 2, '11000010': 2, '11000011': 3, '11000100': 2, '11000110': 1, '11000111': 3, '11001000': 5, '11001001': 1, '11001010': 1, '11001101': 2, '11001110': 8, '11001111': 7, '11010000': 3, '11010010': 3, '11010011': 1, '11010101': 1, '11010110': 1, '11010111': 3, '11011000': 7, '11011010': 2, '11011100': 3, '11011101': 3, '11011110': 2, '11011111': 11, '11100000': 6, '11100001': 6, '11100010': 3, '11100011': 2, '11100100': 3, '11100101': 3, '11100110': 2, '11100111': 8, '11101001': 3, '11101011': 1, '11101101': 3, '11101110': 2, '11101111': 6, '11110000': 3, '11110001': 3, '11110010': 5, '11110011': 5, '11110100': 2, '11110111': 7, '11111000': 13, '11111001': 3, '11111010': 1, '11111011': 1, '11111100': 5, '11111101': 7, '11111110': 26, '11111111': 53, '00000100': 8, '01000001': 2, '01000000': 7, '01111000': 12, '01111001': 5, '00100000': 4, '00010100': 4, '00111100': 12, '00110000': 2, '01100000': 5, '00111101': 9, '00011110': 5, '00011111': 8, '00001100': 2, '00001101': 2, '01111011': 1, '01111010': 5, '01100011': 2, '01100010': 4, '00010111': 1, '00110011': 2, '00110010': 2, '00011101': 3, '00011100': 2, '00001111': 7, '00001110': 3, '01010110': 3, '01010111': 1, '00000000': 6, '00000001': 3, '00111010': 3, '00111011': 7, '01101010': 1, '01101011': 3, '01000100': 3, '01000101': 3, '00000101': 1, '00000011': 2, '00100100': 2, '01101001': 3, '01101000': 1, '00000010': 3, '00111001': 4, '00111000': 13, '00101110': 1, '00101111': 1, '01000111': 2, '01000110': 2, '01001110': 2, '01001111': 11, '01011100': 3, '01110010': 5, '01110011': 6, '00011000': 1, '00100111': 4, '00100110': 3, '00101101': 1, '00101100': 1, '01100001': 3, '00011010': 1, '01001100': 1, '01011111': 13, '01011110': 4, '01010101': 1, '01010100': 3, '01110001': 2, '01110000': 3, '01010000': 4, '01010001': 1, '01110100': 9, '01110101': 1, '01111110': 31, '01111111': 39, '01101100': 3, '00110110': 3, '00110111': 1, '01100110': 1, '01100111': 4, '00010010': 2, '00001010': 2, '00001011': 3, '01010011': 1, '01010010': 3, '01011101': 3, '01011010': 1, '01011011': 1, '01111101': 13, '01111100': 9, '00101000': 3, '00101001': 2, '01101111': 8, '01101110': 1, '00010001': 1, '00010000': 3, '00111110': 27, '00110100': 3, '01100101': 2, '01100100': 1, '00001000': 3, '00111111': 52, '01001000': 6, '01001001': 1, '01011000': 2, '00101011': 1, '01110110': 2, '00100010': 1, '00100011': 2, '01000010': 4, '01000011': 4, '00110001': 2}
        if (a==11):
            result = {'00000111': 6, '11111100': 12, '11000101': 4, '11100000': 5, '11111110': 63, '11101010': 6, '01100010': 1, '10100001': 7, '10111100': 4, '00001010': 3, '11111111': 69, '10111111': 12, '00110111': 6, '01101001': 3, '10110000': 1, '01100000': 1, '00011100': 7, '01111111': 63, '00111111': 18, '00000110': 6, '11011110': 4, '10101011': 1, '10001111': 1, '11010010': 2, '00100010': 4, '00111110': 18, '11001011': 1, '11111001': 9, '11111000': 18, '00110110': 3, '00011110': 15, '01100111': 6, '01111101': 14, '11000111': 2, '10110101': 2, '00010001': 8, '01101010': 1, '11111101': 14, '01111110': 46, '00101100': 1, '10101010': 4, '10011110': 4, '10111110': 16, '01001110': 8, '00000100': 5, '10001001': 3, '11100110': 9, '01010111': 5, '00001110': 7, '00010000': 5, '00010110': 3, '01101110': 3, '00011111': 15, '01110100': 4, '01001101': 3, '11001110': 8, '11011111': 4, '10010000': 2, '11100111': 8, '11110001': 9, '01111100': 15, '10101110': 2, '10100111': 4, '01101000': 1, '00001001': 5, '01010101': 2, '11000110': 3, '01000101': 3, '00100000': 2, '01000100': 8, '00000010': 4, '00001011': 3, '01110001': 2, '11110011': 11, '10100000': 3, '11110010': 6, '01010000': 2, '00101101': 2, '10010001': 3, '01011110': 2, '01000111': 2, '01111001': 9, '11000000': 4, '11110110': 3, '10000010': 3, '00100011': 4, '00111000': 1, '10110001': 2, '11100101': 3, '10011111': 3, '11101100': 2, '00011000': 2, '10111101': 9, '10010111': 2, '10000001': 3, '11100001': 3, '11110100': 7, '10111001': 4, '00000000': 8, '00001000': 6, '10000110': 2, '01110111': 2, '11111010': 5, '00010111': 4, '01011111': 6, '00010010': 7, '01110011': 5, '11010110': 1, '11011010': 2, '11101110': 3, '11101011': 3, '00001111': 2, '11100100': 2, '01010010': 1, '10000111': 3, '11000001': 3, '00100110': 1, '01110000': 3, '00000001': 7, '00111101': 4, '10110011': 4, '10001000': 2, '00110101': 2, '01000001': 4, '01100001': 4, '11010111': 2, '11010011': 3, '01010110': 2, '11011101': 4, '11100010': 1, '10111000': 1, '01111011': 4, '01110101': 2, '11100011': 9, '00111100': 3, '11110111': 1, '01010011': 1, '10001110': 5, '11101111': 3, '10010110': 1, '10000000': 4, '01011101': 1, '01001111': 2, '01111010': 4, '10010011': 1, '00010100': 2, '10000011': 3, '00011010': 1, '10010100': 2, '01011010': 1, '10101111': 3, '01001000': 3, '10100011': 1, '00100100': 2, '01101011': 1, '00010011': 3, '10001011': 2, '00111001': 2, '10110010': 2, '11110101': 3, '00111010': 2, '01000000': 4, '11011000': 1, '01001010': 3, '01101101': 2, '01110010': 6, '00100001': 4, '01011011': 1, '00101010': 2, '00100111': 1, '11001111': 6, '10100110': 1, '10101001': 1, '00101001': 1, '10100101': 2, '01011001': 1, '00101111': 5, '11110000': 5, '11101001': 2, '00110011': 1, '00010101': 2, '10111010': 1, '01100110': 2, '11001000': 2, '01110110': 1, '00011001': 1, '10010010': 1, '11001100': 2, '01111000': 5, '00011101': 1, '00000011': 2, '01100101': 1, '10111011': 1, '01100100': 4, '00110010': 1, '11001001': 1, '00101110': 2, '11011100': 2, '00001101': 2, '01001001': 2, '11011011': 1, '00100101': 1, '01001011': 1, '10011100': 1, '01101100': 1, '10100100': 1, '00110000': 1, '11111011': 1, '11101000': 1, '11000010': 1, '01000010': 1, '11101101': 1, '10001101': 1, '10000100': 1, '00000101': 1}

    #sys.exit(0)
    
    rslt1=0
    rslt2=0
    rslt3=0
    rslt4=0
    dist=0
    
    inputNumBits = (2 * n) - 1
    inputNumBits += 1 if ((1 << inputNumBits) < (N * N)) else 0
    Q = 1 << inputNumBits
    
    for key, val in result.items():
    
        dist += pow(val, 2)
    
        decimal1 = 0
        for bit in key:
            decimal1 = decimal1*2 + int(bit)
        rslt1 += decimal1 * val
        
        decimal2 = 0
        for bit in reversed(key):
            decimal2 = decimal2*2 + int(bit)
        rslt2 += decimal2 * val
    
        i=0
        decimal3 = 0.0
        for bit in key:
            i+=1
            decimal3 += (int(bit) / pow(2, i))
        rslt3 += decimal3 * val
        
        i=0
        decimal4 = 0.0
        for bit in reversed(key):
            i+=1
            decimal4 += (int(bit) / pow(2, i))
        rslt4 += decimal4 * val
        
    dist = math.sqrt(dist)
    rslt1=rslt1/1024
    rslt2=rslt2/1024
    rslt3=rslt3/1024
    rslt4=rslt4/1024
    
    print(rslt1)
    print(rslt2)
    print(rslt3)
    print(rslt4)
    
    print(cf(rslt1, Q, N))
    print(cf(rslt2, Q, N))
    print(cf(rslt3, Q, N))
    print(cf(rslt4, Q, N))

#======================================================================#
#-------------------------------- MAIN --------------------------------#
#======================================================================#
if __name__ == "__main__":

    # Finding period (r) of a % N, with N=15
    # Assume we need n=4 qubits to represent N=15
    a = 7
    N = 15
    n = 4
    findperiod(a, N, n)
