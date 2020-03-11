include "qelib1.inc";
qreg q[3];
creg c[2];

u1(pi) q[1];
h q[2];
cx q[2],q[1];
u1(pi) q[1];
u2(pi/4,pi) q[2];
cx q[2],q[1];
u1(-pi/4) q[1];
cx q[2],q[1];
u1(pi/4+ (4*pi/2) ) q[1];
u2(2* (4*pi/2) ,0) q[2];
cx q[2],q[0];
cx q[1],q[0];
u1( 2*(4*pi/2) ) q[0];
cx q[1],q[0];
cx q[2],q[0];
u2(3*pi/4,pi) q[2];
cx q[2],q[1];
u1(pi/4) q[1];
cx q[2],q[1];
u2(0,3*pi/4) q[1];

measure q[1] -> c[0];
measure q[2] -> c[1];
