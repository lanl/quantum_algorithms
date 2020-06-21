#======================================================================#
#----------  Finding period (r) of a % N, with N=15  ------------------#
#======================================================================#
def findperiod(a, N=15, nqubits1, nqubits2):

    # Create QuantumProgram object, and define registers and circuit
    Q_program = QuantumProgram()
    qr1 = Q_program.create_quantum_register("qr1", nqubits1)
    qr2 = Q_program.create_quantum_register("qr2", nqubits2)
    cr1 = Q_program.create_classical_register("cr1", nqubits1)
    cmod15 = Q_program.create_circuit("cmod15", [qr1, qr2], [cr1])

    # Apply a hadamard to each qubit in register 1
    # and prepare state |1> in regsiter 2
    for j in range(nqubits1): cmod15.h(qr1[j])
    cmod15.x(qr2[nqubits2-1])

    # Loop over qubits in register 1
    for p in range(nqubits1):

        # Calculate next 'b' in the Ub to apply
        # ( Note: b = a^(2^p) % N ).
        # Then apply Ub
        b = pow(a,pow(2,p),N)
        CxModM(cmod15, qr1, qr2, p, b, N, nqubits1, nqubits2)

    # Perform inverse QFT on first register
    qft_inv(cmod15, qr1, nqubits1)

    # Measure each qubit, storing the result in the classical register
    for i in range(n_qr1): cmod15.measure(qr1[i], cr1[i])

