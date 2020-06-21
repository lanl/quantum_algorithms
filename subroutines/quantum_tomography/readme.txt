use: julia qtml.jl arguments.csv

modify arguments in arguments.csv
[data file name], [gradient descent step size], [number of iterations]

data file has the following structure:
[empirical frequency], [projection state as a vector written in the computational basis]

note: vectors don't have to be normalized as in the provided example,
the normalization will be done automatically