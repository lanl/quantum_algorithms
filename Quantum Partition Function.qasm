include "qelib1.inc";

qreg q[5];
creg c[5];

h q[0];
h q[1];
u1(-pi) q[0];
u1(pi) q[1];
barrier q[0],q[1],q[2],q[3],q[4];
h q[0];
u1(pi/4) q[1];
cx q[1],q[0];
u1(-pi/4) q[0];
cx q[1],q[0];
u1(pi/4) q[0];
h q[1];
cx q[1],q[0];
h q[0];
h q[1];
cx q[1],q[0];
h q[0];
h q[1];
cx q[1],q[0];
measure q[0] -> c[0];
measure q[1] -> c[1];
