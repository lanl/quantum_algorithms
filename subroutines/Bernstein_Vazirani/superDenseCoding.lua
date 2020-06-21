#!/usr/bin/env luajit
-- LuaQubits
-- (c) 2017 Nandakishore Santhi
-- LuaQubits is intended to be open-source once LACC'd
package.path = "lib/?.lua;" .. package.path

local qubits = require "qubits"

-- The bits to be sent to Alice are set in the string called input:
local input = "10"

local startTime = os.clock()

-- First, create a pair of entangled qubits
local state = qubits('|00>'):hadamard(0):cNot(0, 1)

-- Assume that qubit 0 is sent to Bob, and that qubit 1 is sent to Alice.

-- Alice prepares her qubit (qubit 1)
local alice = 1
if (input[1] == '1') then state = state:z(alice) end
if (input[2] == '1') then state = state:x(alice) end

-- Alice sends her qubit to Bob.

-- Bob recovers the input bit values.
local bob = 0 -- Bob's qubit
state = state:cNot(alice, bob):hadamard(alice)
print("Input string was: " .. state:measure("ALL"):asBitString())

local endTime = os.clock()
print("Time taken: " .. (endTime - startTime) .. " (s)")
