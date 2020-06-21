include "qelib1.inc";
qreg q[5];
creg c[5];

x q[0];
h q[1];
h q[2];
h q[0];

h q[0];
cx q[1],q[0];
tdg q[0];
cx q[2],q[0];
t q[0];
cx q[1],q[0];
tdg q[0];
cx q[2],q[0];
t q[0];
tdg q[1];
h q[0];
cx q[2],q[1];
tdg q[1];
cx q[2],q[1];
s q[1];
t q[2];

h q[1];
h q[2];
x q[1];
x q[2];
h q[1];
cx q[2],q[1];
h q[1];
x q[1];
x q[2];
h q[1];
h q[2];
measure q[1] -> c[1];
measure q[2] -> c[2];

