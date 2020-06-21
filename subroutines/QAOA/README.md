# Scripts

- util - utilities for checking connection and translating data
- debug - tools debugging quantum circuits
- basic - very basic protype implementations of maxcut-qaoa

# Setup

```
pip3 install qiskit
pip3 install pyquil
pip3 install argparse
```

`remote_test.py` assumes the existence of a file `_config`, a JSON document
of the form,
```
{
    "qx_url":"https://quantumexperience.ng.bluemix.net/api",
    "qx_token":"<your qx token>"
}
```

# Graphs

The naming convention is `<max_node>_<num_edge>_<id>`.  `qh` indicates qubist hamiltonians and `qx` indicates ibmqx chips.

# Other

qiskit api docs - https://www.qiskit.org/documentation/index.html
pyquil api docs - http://pyquil.readthedocs.io/en/stable/

