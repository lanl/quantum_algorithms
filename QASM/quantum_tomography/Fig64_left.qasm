OPENQASM 2.0;
include "qelib1.inc";
gate nG0(param) q  {
  h q;
}

qreg q[5];
creg c[5];

h q[0];
x q[1];
cx q[0],q[1];
sdg q[0];
h q[0];
measure q[0] -> c[0];
measure q[1] -> c[1];
