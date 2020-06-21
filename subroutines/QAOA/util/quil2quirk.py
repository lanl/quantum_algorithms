# helper functions to conver quil commands to matricies that can be loaded into quirk.

# load with exec(open("quil2quirk.py").read())

from math import cos
from math import sin

def RX(theta):
    m = [
        [complex(cos(theta/2.0), 0.0),  complex(0, sin(-theta/2.0))],
        [complex(0.0, sin(-theta/2.0)), complex(cos(theta/2.0), 0.0)]
    ]
    return m

def RY(theta):
    m = [
        [complex(cos(theta/2.0), 0.0), complex(sin(-theta/2.0), 0.0)],
        [complex(sin(theta/2.0), 0.0), complex(cos(theta/2.0), 0.0)]
    ]
    return m

def RZ(theta):
    m = [
        [complex(cos(-theta/2.0), sin(-theta/2.0)), complex(0,0)],
        [complex(0,0), complex(cos(theta/2.0), sin(theta/2.0))]
    ]
    return m

def PHASE(theta):
    m = [
        [complex(1,0), complex(0,0)],
        [complex(0,0), complex(cos(theta), sin(theta))]
    ]
    return m

def quirk(m):
    print(m)
    print(m[0][0].imag, 'i + ', m[0][0].real, ', ', m[0][1].imag, 'i + ', m[0][1].real, ', ', m[1][0].imag, ' i + ', m[1][0].real, ', ', m[1][1].imag, 'i + ', m[1][1].real)
