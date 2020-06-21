#!/usr/bin/env luajit
-- LuaQubits
-- (c) 2017 Nandakishore Santhi
-- LuaQubits is intended to be open-source once LACC'd
package.path = "lib/?.lua;" .. package.path

local qubits = require "qubits"

local function bernsteinVazirani(f, numQubits)
    --  Create a |-> state as the target qubit.
    local targetQubit = (qubits("|0>") - qubits("|1>")):normalize()
    local inputQubits = qubits.QState(numQubits)
    local initialState = inputQubits:tensorProduct(targetQubit)

    local inputBits = {from = 1, to = numQubits}
    local targetBit = 0
    return initialState
            :hadamard(inputBits)
            :applyFunction(inputBits, targetBit, f)
            :hadamard(inputBits)
            :measure(inputBits)
            :asBitString()
end

local function createHiddenStringFunction(hiddenString)
    local hiddenStringAsNumber = tonumber(hiddenString, 2)
    local numQubits = #hiddenString
    return function(x)
        local dotProduct = bit.band(x, hiddenStringAsNumber)
        local result = 0x0
        for i=0,numQubits-1 do result = bit.bxor(result, bit.band(bit.rshift(dotProduct, i), 0x1)) end
        return result
    end, numQubits
end

if #arg < 1 then print("Usage: " .. arg[0] .. " hiddenBinaryString\n") os.exit() end
local f, qubitSize = createHiddenStringFunction(arg[1])

local startTime = os.clock()
print("Hidden string is: \"" .. bernsteinVazirani(f, qubitSize) .. "\"")
local endTime = os.clock()

print("Time to complete: " .. (endTime-startTime) .. " (s)")
