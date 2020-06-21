#!/usr/bin/env luajit
-- LuaQubits
-- (c) 2017 Nandakishore Santhi
-- LuaQubits is intended to be open-source once LACC'd
package.path = "lib/?.lua;" .. package.path

local qubits = require "qubits"

local function computeOrder(a, n)
    local numOutBits = math.ceil(math.log(n, 2))
    local numInBits = 2 * numOutBits
    local inputRange = 2^numInBits
    local outputRange = 2^numOutBits
    local accuracyRequiredForContinuedFraction = 1/(2 * (outputRange^2) )
    local outBits = {from = 0, to = numOutBits - 1}
    local inputBits = {from = numOutBits, to = numOutBits + numInBits - 1}
    local f = function(x) return qubits.Qmath:powerMod(a, x, n) end
    local f0 = f(0)

    -- This function contains the actual quantum computation part of the algorithm.
    -- It returns either the frequency of the function f or some integer multiple
    -- (where "frequency" is the number of times the period of f will fit into 2^numInputBits)
    local function determineFrequency(f)
        local qstate = qubits.QState(numInBits + numOutBits):hadamard(inputBits)
        qstate = qstate:applyFunction(inputBits, outBits, f)
        -- We do not need to measure the outBits, but it does speed up the simulation.
        qstate = qstate:measure(outBits).newState
        return qstate:qft(inputBits):measure(inputBits).result
    end

    -- Determine the period of f (i.e. find r such that f(x) = f(x+r).
    local function findPeriod()
        local bestSoFar = 1

        for attempts=0,(2*numOutBits-1) do
            --NOTE: Here we take advantage of the fact that, for Shor's algorithm, we know that f(x) = f(x+i)
            --ONLY when i is an integer multiple of the rank r.
            if f(bestSoFar) == f0 then return bestSoFar end

            local sample = determineFrequency(f)

            -- Each "sample" has a high probability of being approximately equal to some integer multiple of
            -- (inputRange/r) rounded to the nearest integer.
            -- So we use a continued fraction function to find r (or a divisor of r).
            local continuedFraction = qubits.Qmath:continuedFraction(sample/inputRange, accuracyRequiredForContinuedFraction)
            -- The denominator is a "candidate" for being r or a divisor of r (hence we need to find the least common multiple of several of these).
            local candidateDivisor = continuedFraction.denominator

            -- Reduce the chances of getting the wrong answer by ignoring obviously wrong results!
            if candidateDivisor > 1 and candidateDivisor <= outputRange then
                if f(candidateDivisor) == f0 then bestSoFar = candidateDivisor -- This is a multiple of the rank
                else
                    local lcm = qubits.Qmath:lcm(candidateDivisor, bestSoFar)
                    if lcm <= outputRange then bestSoFar = lcm end --This is a good candidate
                end
            end
        end
        return "failed" -- Giving up.
    end

    -- Step 2: compute the period of a^x mod n
    return findPeriod()
end

local function factor(n)
    if (n%2 == 0) then return 2 end -- Is even.  No need for any quantum computing!

    local powerFactor = qubits.Qmath:powerFactor(n)
    if (powerFactor > 1) then return powerFactor end -- Is a power factor.  No need for anything quantum!

    -- Make 8 attempts before giving up (may need fine tuning).
    for attempts=0,7 do
        -- Step 1: chose random number between 2 and n
        local randomChoice = 2 + math.floor(math.random() * (n - 2))
        local gcd = qubits.Qmath:gcd(randomChoice, n)
        if gcd > 1 then return gcd end -- Lucky guess. n  and randomly chosen randomChoice  have a common factor = gcd

        local r = computeOrder(randomChoice, n)

        -- Need a period with an even number.
        if r ~= "failed" and r%2 == 0 then
            local powerMod = qubits.Qmath:powerMod(randomChoice, r/2, n)
            local candidateFactor = qubits.Qmath:gcd(powerMod - 1, n)

            if candidateFactor > 1 and n%candidateFactor == 0 then return candidateFactor end
        end
    end
    return "failed"
end

if #arg < 1 then print("Usage: " .. arg[0] .. " integer\n") os.exit() end
local num = tonumber(arg[1])

local startTime = os.clock()
print("One factor of " .. arg[1] .. " is " .. tostring(factor(num)))
local endTime = os.clock()

print("Time to complete: " .. (endTime-startTime) .. " (s)")
