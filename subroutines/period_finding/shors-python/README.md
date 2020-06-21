shors-python
============

Implementation of Shor's algorithm in Python 3.X.

Shor's algorithm performs integer factorization on a quantum computer, which can break many asymmetric (public/private key) cryptosystems, such as RSA or Diffie–Hellman. Many secure protocols, including HTTPS, SSH, and TLS, rely on these cryptosystems to guarantee encryption and authenticity.  In mathematical terms, Shor's solves the hidden subgroup problem for finite Abelian groups. In layman's terms, Shor's algorithm could expose encrypted information, such as passwords, credit cards, or other confidential items, transmitted over the Internet.  This implementation simulates a quantum circuit using state vectors and unitary mappings.

For more information, see http://en.wikipedia.org/wiki/Shor's_algorithm

## Usage

```shell
  python shors.py [-p|--periods PERIODS] [-a|--attempts ATTEMPTS] [-n|--neighborhood NEIGHBORHOOD] [-v|--verbose] N
```

Where:

 - PERIODS is the number of successful circuit rounds to run before finding the GCD of their results
 - ATTEMPTS is the number of attempted circuit simulations to run per round
 - NEIGHBORHOOD is the range of values to check near the circuit output register, given as a percentage of N
 - N is the composite, positive integer to factor

To see a list of options available from the command line, use:

```shell
  python shors.py --help
```
