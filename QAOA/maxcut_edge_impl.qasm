OPENQASM 2.0;
include "qelib1.inc";

qreg q[2];
creg c[1];

cx q[1],q[0];
u1(-gamma) q[0];
cx q[1],q[0];
