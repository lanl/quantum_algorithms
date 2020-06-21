-- LuaQubits
-- (c) 2017 Nandakishore Santhi
-- LuaQubits is intended to be open-source once LACC'd
-- Code is inspired by JSQubits https://github.com/davidbkemp/jsqubits
local inspect = require('inspect')
local bit = require('bit')
local bnot, band, bor, bxor, lshift, rshift = bit.bnot, bit.band, bit.bor, bit.bxor, bit.lshift, bit.rshift

--Allow strings to be indexed as: line[1], line(1, 2) etc.
getmetatable('').__index = function(str,i) return (type(i) == 'number' and string.sub(str,i,i) or string[i]) end
getmetatable('').__call = function(str,i,j)
    if type(i)~='table' then return string.sub(str, i, j)
    else
        local t = {}
        for k,v in ipairs(i) do t[k] = string.sub(str, v, v) end
        return table.concat(t)
    end
end

--Forward declarations for all Classes
local qubits = {}
local Qmath = {}
local Complex = {}
local Measurement = {}
local StateWithAmplitude = {}
local QState = {}

--Some convenience functions
local function round(num)
    if num >= 0 then return math.floor(num+0.5)
    else return math.ceil(num-0.5) end
end

local function roundTowardsZero(value)
    return (value >=0) and math.floor(value) or math.ceil(value)
end

local function approximatelyInteger(x)
    return math.abs(x - round(x)) < qubits.roundToZero
end

local function cloneArray(a)
    local result = {}
    for i,v in pairs(a) do result[i] = v end
    return result
end

local function instanceOf(object, klass)
    return (type(object) == 'table') and (getmetatable(object) == klass)
end

local function indexOf(t, object)
    if type(t) == 'table' then
        for key,val in pairs(t) do
            if object == val then return key end
        end
        return nil
    else error("indexOf() expects table for first argument, " .. type(t) .. " given") end
end

local function slice(t, first, last, step)
    if type(t) == 'table' then
        local sliced = {}
        --Assumes [0] base indexing
        local index = 0
        for i=(first or 0),(last and (last-1) or #t),(step or 1) do
            sliced[index] = t[i]
            index = index + 1
        end
        --print(inspect(t), first, last, step, inspect(sliced))
        return sliced
    else error("slice() expects table for first argument, " .. type(t) .. " given") end
end

local function padState(state, numBits)
    local paddingLength = numBits - #state
    --print("padState(): ", type(state), paddingLength, state, numBits, #state)
    for i=0,paddingLength-1 do
        state = '0' .. state
    end
    return state
end

local function createBitMask(bits)
    local mask
    if bits then
        mask = 0
        for i=0,#bits do mask = mask + lshift(1, bits[i]) end
    end
    return mask
end

local function toBinString(n, numBits)
    -- returns a table of bits, most significant first.
    local num, bits = n, numBits or math.max(1, select(2, math.frexp(n)))
    local t = {} -- will contain the bits
    for b = bits, 1, -1 do --Assumes "bits < 32"
        t[b] = num%2
        num = rshift((num - t[b]), 1)
    end
    return table.concat(t)
end

local function parseBitString(bitString)
    -- Strip optional 'ket' characters to support |0101>
    local bitString = bitString:gsub("^|", ""):gsub(">$", "")
    return {value = tonumber(bitString, 2), length = #bitString}
end

local function sparseAssign(array, index, value)
    -- Try to avoid assigning values and try to make zero exactly zero.
    if value:magnitude() > qubits.roundToZero then array[index] = value end
end

local function convertBitQualifierToBitRange(bits, numBits)
    if bits == nil then
        error("bit qualification must be supplied")
    elseif bits == qubits.ALL then
        return {from = 0, to = numBits-1}
    elseif type(bits) == 'number' then
        return {from = bits, to = bits}
    elseif bits.from ~= nil and bits.to ~= nil then
        if bits.from > bits.to then error("bit range must have 'from' being less than or equal to 'to'") end
        return bits
    else error("bit qualification must be either: a number, qubits.ALL, or {from: n, to: m}") end
end

local function validateControlAndTargetBitsDontOverlap(controlBits, targetBits)
    -- TODO: Find out if it would sometimes be faster to put one of the bit collections into a hash-set first.
    -- Also consider allowing validation to be disabled.
    for i=0,#controlBits do
        local controlBit = controlBits[i]
        for j=0,#targetBits do
            if controlBit == targetBits[j] then error("control and target bits must not be the same nor overlap") end
        end
    end
end

local function chooseRandomBasisState(qState)
    local randomNumber = math.random()
    local randomStateString
    local accumulativeSquareAmplitudeMagnitude = 0
    --print("qState: " .. inspect(qState))
    qState:each(function(stateWithAmplitude)
        --print("stateWithAmplitude: " .. inspect(stateWithAmplitude))
        local magnitude = stateWithAmplitude.amplitude:magnitude()
        accumulativeSquareAmplitudeMagnitude = accumulativeSquareAmplitudeMagnitude + (magnitude^2)
        randomStateString = stateWithAmplitude.index
        if accumulativeSquareAmplitudeMagnitude > randomNumber then return false end
    end)
    --print(randomStateString)
    return tonumber(randomStateString)
end

local function bitRangeAsArray(low, high)
    if low > high then erro("bit range must have 'from' being less than or equal to 'to'") end
    local result = {}
    local index = 0
    for i=low,high do
        result[index] = i
        index = index + 1
    end
    return result
end

local function convertBitQualifierToBitArray(bits, numBits)
    --print("convertBitQualifierToBitArray(): ", bits, numBits)
    if bits == nil then error("bit qualification must be supplied")
    elseif type(bits) == 'number' then return {[0] = bits}
    elseif bits == qubits.ALL then return bitRangeAsArray(0, numBits-1)
    elseif bits.from ~= nil and bits.to ~= nil then return bitRangeAsArray(bits.from, bits.to)
    elseif type(bits) == 'table' then return bits
    else error("bit qualification must be either: a number, an array of numbers, qubits.ALL, or {from: n, to: m}") end
end

--Class definitions follow
--Qmath class
Qmath.__index = Qmath
setmetatable(Qmath, Qmath)

-- Return x^y mod m
function Qmath:powerMod(x, y, m)
    if (y == 0) then return 1
    elseif (y == 1) then return x
    else
        local result = (self:powerMod(x, math.floor(y/2), m) ^ 2) % m
        if y%2 == 1 then result = (x * result) % m end
        return result
    end
end

-- Return x such that n = x^y for some prime number x, or otherwise return 0.
function Qmath:powerFactor(n)
    local log2n = math.log(n, 2)
    -- Try values of root_y(n) starting at log2n and working your way down to 2.
    local y = math.floor(log2n)
    if log2n == y then return 2
    else
        y = y - 1
        while y > 1 do
            local x = math.pow(n, 1/y)
            if approximatelyInteger(x) then return round(x) end
            y = y - 1
        end
        return 0
    end
end

-- Greatest common divisor
function Qmath:gcd(a, b)
    while b ~= 0 do
        local c = a % b
        a = b
        b = c
    end
    return a
end

-- Least common multiple
function Qmath:lcm(a, b)
    return a * b / self:gcd(a, b)
end

--[[
    Find the continued fraction representation of a number.
    @param the value to be converted to a continued faction.
    @param the precision with which to compute (eg. 0.01 will compute values until the fraction is at least as precise as 0.01).
    @return An object {quotients: quotients, numerator: numerator, denominator: denominator} where quotients is
    an array of the quotients making up the continued fraction whose value is within the specified precision of the targetValue,
    and where numerator and denominator are the integer values to which the continued fraction evaluates.
]]
function Qmath:continuedFraction(targetValue, precision)
        local firstValue, remainder
        if math.abs(targetValue) >= 1 then
            firstValue = roundTowardsZero(targetValue)
            remainder = targetValue - firstValue
        else
            firstValue = 0
            remainder = targetValue
        end
        local twoAgo = {
            numerator = 1,
            denominator = 0,
        }
        local oneAgo = {
            numerator = firstValue,
            denominator = 1,
        }
        local quotients = {
            firstValue,
        }

        while (math.abs(targetValue - (oneAgo.numerator / oneAgo.denominator)) > precision) do
            local reciprocal = 1 / remainder
            local quotient = roundTowardsZero(reciprocal)
            remainder = reciprocal - quotient
            table.insert(quotients, quotient)
            local current = {
                numerator = quotient * oneAgo.numerator + twoAgo.numerator,
                denominator = quotient * oneAgo.denominator + twoAgo.denominator,
            }
            twoAgo = oneAgo
            oneAgo = current
        end

        local numerator = oneAgo.numerator
        local denominator = oneAgo.denominator
        if oneAgo.denominator < 0 then
            numerator = -numerator
            denominator = -denominator
        end
        return {
            quotients = quotients,
            numerator = numerator,
            denominator = denominator,
        }
end

-- Find the special solutions to the mod-2 equation Ax=0 for matrix a.
local function specialSolutions(a, width, pivotColumnIndexes)
    -- Add to results, special solutions corresponding to the specified non-pivot column colIndex.
    local function specialSolutionForColumn(a, pivotColumnIndexes, colIndex, pivotNumber)
        local columnMask = lshift(1, colIndex)
        local specialSolution = columnMask
        for rowIndex=0,pivotNumber-1 do
            if band(a[rowIndex], columnMask) ~= 0 then
                specialSolution = specialSolution + lshift(1, pivotColumnIndexes[rowIndex])
            end
        end
        return specialSolution
    end

    local results = {}
    local pivotNumber = 0
    local nextPivotColumnIndex = pivotColumnIndexes[pivotNumber]
    for colIndex=width-1,0 do
        if colIndex == nextPivotColumnIndex then
            pivotNumber = pivotNumber + 1
            nextPivotColumnIndex = pivotColumnIndexes[pivotNumber]
        else
            table.insert(results, specialSolutionForColumn(a, pivotColumnIndexes, colIndex, pivotNumber))
        end
    end
    return results
end

--[[
    Find the null space in modulus 2 arithmetic of a matrix of binary values
    @param a matrix of binary values represented using an array of numbers
    whose bit values are the entries of a matrix rowIndex.
    @param width the width of the matrix.
]]
function Qmath:findNullSpaceMod2(a, width)
    -- Reduce 'a' to reduced row echelon form, and keep track of which columns are pivot columns in pivotColumnIndexes.
    local function makeReducedRowEchelonForm(a, width, pivotColumnIndexes)
        -- Try to make row pivotRowIndex / column colIndex a pivot swapping rows if necessary
        local function attemptToMakePivot(a, colIndex, pivotRowIndex)
            local colBitMask=lshift(1, colIndex)
            if band(colBitMask, a[pivotRowIndex]) ~= 0 then return end
            for rowIndex=pivotRowIndex+1,#a do --TODO: Verify
                if band(colBitMask, a[rowIndex]) ~= 0 then --Swap row with pivot
                    local tmp = a[pivotRowIndex]
                    a[pivotRowIndex] = a[rowIndex]
                    a[rowIndex] = tmp
                    return
                end
            end
        end

        -- Zero out the values above and below the pivot (using mod 2 arithmetic).
        local function zeroOutAboveAndBelow(a, pivotColIndex, pivotRowIndex)
            local pivotRow = a[pivotRowIndex]
            local colBitMask = lshift(1, pivotColIndex)
            for rowIndex=0,#a do
                if ((rowIndex ~= pivotRowIndex) and (band(colBitMask, a[rowIndex]) ~= 0)) then
                    a[rowIndex] = bxor(a[rowIndex], pivotRow)
                end
            end
        end

        local pivotRowIndex = 0
        for pivotColIndex=width-1,0 do
            attemptToMakePivot(a, pivotColIndex, pivotRowIndex)
            local colBitMask=lshift(1, pivotColIndex)
            if band(colBitMask, a[pivotRowIndex]) ~= 0 then
                pivotColumnIndexes[pivotRowIndex] = pivotColIndex
                zeroOutAboveAndBelow(a, pivotColIndex, pivotRowIndex)
                pivotRowIndex = pivotRowIndex + 1
            end
        end
    end

    local aCopy = cloneArray(a)
    local pivotColumnIndexes = {}
    makeReducedRowEchelonForm(aCopy, width, pivotColumnIndexes)
    return specialSolutions(aCopy, width, pivotColumnIndexes)
end

--Complex class
Complex.__index = Complex
setmetatable(Complex, Complex)

function Complex:__call(real, imaginary)
    return setmetatable({real = real or 0, imaginary = imaginary or 0}, Complex)
end

function Complex:__add(other)
    if type(other) == 'number' then return Complex(self.real + other, self.imaginary)
    elseif type(self) == 'number' then return Complex(other.real + self, other.imaginary)
    else return Complex(self.real + other.real, self.imaginary + other.imaginary) end
end
Complex.add = Complex.__add

function Complex:__sub(other)
    if type(other) == 'number' then return Complex(self.real - other, self.imaginary)
    elseif type(self) == 'number' then return Complex(other.real - self, other.imaginary)
    else return Complex(self.real - other.real, self.imaginary - other.imaginary) end
end
Complex.subtract = Complex.__sub

function Complex:__unm()
    return Complex(-self.real, -self.imaginary)
end
Complex.negate = Complex.__unm

function Complex:__mul(other)
    if type(other) == 'number' then return Complex(self.real * other, self.imaginary * other)
    elseif type(self) == 'number' then return Complex(other.real * self, other.imaginary * self)
    else return Complex(self.real * other.real - self.imaginary * other.imaginary,
                    self.real * other.imaginary + self.imaginary * other.real)
    end
end
Complex.multiply = Complex.__mul

function Complex:conjugate()
    return Complex(self.real, -self.imaginary)
end

function Complex:__tostring()
    if self.imaginary == 0 then return tostring(self.real) end
    local imaginaryString
    if self.imaginary == 1 then
        imaginaryString = 'i'
    elseif self.imaginary == -1 then
        imaginaryString = '-i'
    end
    if self.real == 0 then return imaginaryString end
    if imaginaryString then
        return self.real .. imaginaryString
    else
        imaginaryString = self.imaginary .. 'i'
    end
    local sign = (self.imaginary < 0) and "" or "+"
    return self.real .. sign .. imaginaryString
end

function Complex:format(options)
    local realValue = self.real
    local imaginaryValue = self.imaginary
    if (options and options.decimalPlaces ~= nil) then
        local roundingMagnitude = 10^options.decimalPlaces
        realValue = round(realValue * roundingMagnitude) / roundingMagnitude
        imaginaryValue = round(imaginaryValue * roundingMagnitude) / roundingMagnitude
    end
    local objectToFormat = Complex(realValue, imaginaryValue)
    return tostring(objectToFormat)
end

function Complex:magnitude()
    return math.sqrt(self.real * self.real + self.imaginary * self.imaginary)
end

function Complex:phase()
    return math.atan2(self.imaginary, self.real)
end

function Complex:__eq(other)
    if not instanceOf(other, Complex) then return false end
    return (self.real == other.real) and (self.imaginary == other.imaginary)
end

local function Real(val)
    return Complex(val, 0)
end

Complex.ZERO = Complex(0, 0)
Complex.ONE = Complex(1, 0)
Complex.SQRT2 = Real(math.sqrt(2))
Complex.SQRT1_2 = Real(math.sqrt(1/2))

-- Measurement class
Measurement.__index = Measurement
setmetatable(Measurement, Measurement)

function Measurement:__call(numBits, result, newState)
    return setmetatable({numBits = numBits, result = result, newState = newState}, Measurement)
end

function Measurement:__tostring()
    return "{result: " .. self.result .. ", newState: " .. self.newState + "}"
end

function Measurement:asBitString()
    --print("asBitString():", self.result, self.numBits)
    return padState(toBinString(self.result), self.numBits)
end

-- StateWithAmplitude class
StateWithAmplitude.__index = StateWithAmplitude
setmetatable(StateWithAmplitude, StateWithAmplitude)

function StateWithAmplitude:__call(numBits, index, amplitude)
    return setmetatable({numBits = numBits, index = index, amplitude = amplitude}, StateWithAmplitude)
end

function StateWithAmplitude:asNumber()
    --print("StateWithAmplitude:asNumber(): " .. inspect(self))
    return tonumber(self.index) --FIXME: tonumber() not needed?
end

function StateWithAmplitude:asBitString()
    return padState(toBinString(tonumber(self.index)), self.numBits) --FIXME: tonumber() not needed?
end

-- QState class
QState.__index = QState
setmetatable(QState, QState)

function QState:__call(numBits, amplitudes)
    if not numBits then error("QState() must be supplied with the number of bits (optionally with amplitudes table as well)") end
    local amplitudes = amplitudes or {[0] = Complex.ONE} --Start from [0] or [1]?

    return setmetatable({numBits = numBits, amplitudes = amplitudes}, QState)
end

function QState:amplitude(basisState)
    local numericIndex = (type(basisState) == 'string') and parseBitString(basisState).value or basisState
    return self.amplitudes[numericIndex] or Complex.ZERO
end

function QState:each(callBack)
    if type(callBack) ~= "function" then error("Must supply a callback function to QState:each()") end
    --print("amplitudes = " .. inspect(self.amplitudes))
    for index,amplitude in pairs(self.amplitudes) do --FIXME: Use pairs()?
        --print("each: " .. inspect(index))
        local returnValue = callBack(StateWithAmplitude(self.numBits, index, amplitude))
        -- NOTE: Want to continue on void and null returns!
        if returnValue == false then break end
    end
end

function QState:fromBits(bitString)
    local parsedBitString = parseBitString(bitString)
    local amplitudes = {}
    amplitudes[parsedBitString.value] = Complex.ONE
    --print("fromBits(): " .. parsedBitString.length .. "\namplitudes = " .. inspect(amplitudes))
    return QState(parsedBitString.length, amplitudes)
end

function QState:__mul(other)
    local state, amount
    if instanceOf(other, QState) then state, amount = other, self
    else state, amount = self, other end

    if type(amount) == 'number' then amount = Real(amount) end --amount is to be a complex number

    local amplitudes = {}
    state:each(function(oldAmplitude) amplitudes[oldAmplitude.index] = oldAmplitude.amplitude * amount end)
    return QState(state.numBits, amplitudes)
end
QState.multiply = QState.__mul

function QState:__add(otherState)
    local amplitudes = {}
    self:each(function(stateWithAmplitude) amplitudes[stateWithAmplitude.index] = stateWithAmplitude.amplitude end)
    otherState:each(function(stateWithAmplitude)
        local existingValue = amplitudes[stateWithAmplitude.index] or Complex.ZERO
        amplitudes[stateWithAmplitude.index] = stateWithAmplitude.amplitude + existingValue
    end)
    return QState(self.numBits, amplitudes)
end
QState.add = QState.__add

function QState:__unm()
    return (-1)*self
end

function QState:__sub(otherState)
    return self + (-otherState)
end
QState.subtract = QState.__sub

function QState:tensorProduct(otherState)
    local amplitudes = {}
    self:each(function(basis1WithAmplitude)
        otherState:each(function(basis2WithAmplitude)
            --print(inspect(basis1WithAmplitude) .. '\n' .. inspect(basis2WithAmplitude))
            local newBasisState = lshift(basis1WithAmplitude:asNumber(), otherState.numBits) + basis2WithAmplitude:asNumber()
            local newAmplitude = basis1WithAmplitude.amplitude * basis2WithAmplitude.amplitude
            amplitudes[newBasisState] = newAmplitude
        end)
    end)
    return QState(self.numBits + otherState.numBits, amplitudes)
end
QState.kron = QState.tensorProduct

function QState:controlledHadamard(controlBits, targetBits)
    return self:controlledApplicatinOfqBitOperator(controlBits, targetBits, function(amplitudeOf0, amplitudeOf1)
        local newAmplitudeOf0 = (amplitudeOf0 + amplitudeOf1) * Complex.SQRT1_2
        local newAmplitudeOf1 = (amplitudeOf0 - amplitudeOf1) * Complex.SQRT1_2
        return {amplitudeOf0 = newAmplitudeOf0, amplitudeOf1 = newAmplitudeOf1}
    end)
end

function QState:hadamard(targetBits)
    return self:controlledHadamard(nil, targetBits)
end

function QState:controlledXRotation(controlBits, targetBits, angle)
    return self:controlledApplicatinOfqBitOperator(controlBits, targetBits, function(amplitudeOf0, amplitudeOf1)
        local halfAngle = angle / 2
        local cos = Real(math.cos(halfAngle))
        local negative_i_sin = Complex(0, -math.sin(halfAngle))
        local newAmplitudeOf0 = (amplitudeOf0 * cos) + (amplitudeOf1 * negative_i_sin)
        local newAmplitudeOf1 = (amplitudeOf0 * negative_i_sin) + (amplitudeOf1 * cos)
        return {amplitudeOf0 = newAmplitudeOf0, amplitudeOf1 = newAmplitudeOf1}
    end)
end

function QState:rotateX(targetBits, angle)
    return self:controlledXRotation(nil, targetBits, angle)
end

function QState:controlledYRotation(controlBits, targetBits, angle)
    return self:controlledApplicatinOfqBitOperator(controlBits, targetBits, function(amplitudeOf0, amplitudeOf1)
        local halfAngle = angle / 2
        local cos = Real(math.cos(halfAngle))
        local sin = Real(math.sin(halfAngle))
        local newAmplitudeOf0 = (amplitudeOf0 * cos) - (amplitudeOf1 * sin)
        local newAmplitudeOf1 = (amplitudeOf0 * sin) + (amplitudeOf1 * cos)
        return {amplitudeOf0 = newAmplitudeOf0, amplitudeOf1 = newAmplitudeOf1}
    end)
end

function QState:rotateY(targetBits, angle)
    return self:controlledYRotation(nil, targetBits, angle)
end

function QState:controlledZRotation(controlBits, targetBits, angle)
    return self:controlledApplicatinOfqBitOperator(controlBits, targetBits, function(amplitudeOf0, amplitudeOf1)
        local halfAngle = angle / 2
        local cos = Real(math.cos(halfAngle))
        local i_sin = Complex(0, math.sin(halfAngle))
        local newAmplitudeOf0 = amplitudeOf0 * (cos - i_sin)
        local newAmplitudeOf1 = amplitudeOf1 * (cos + i_sin)
        return {amplitudeOf0 = newAmplitudeOf0, amplitudeOf1 = newAmplitudeOf1}
    end)
end

function QState:rotateZ(targetBits, angle)
    return self:controlledZRotation(nil, targetBits, angle)
end

function QState:controlledR(controlBits, targetBits, angle)
    return self:controlledApplicatinOfqBitOperator(controlBits, targetBits, function(amplitudeOf0, amplitudeOf1)
        local cos = Real(math.cos(angle))
        local i_sin = Complex(0, math.sin(angle))
        local newAmplitudeOf0 = amplitudeOf0
        local newAmplitudeOf1 = amplitudeOf1 * (cos + i_sin)
        return {amplitudeOf0 = newAmplitudeOf0, amplitudeOf1 = newAmplitudeOf1}
    end)
end

function QState:r(targetBits, angle)
    return self:controlledR(nil, targetBits, angle)
end
QState.R = QState.r

function QState:controlledX(controlBits, targetBits)
    return self:controlledApplicatinOfqBitOperator(controlBits, targetBits, function(amplitudeOf0, amplitudeOf1)
        return {amplitudeOf0 = amplitudeOf1, amplitudeOf1 = amplitudeOf0}
    end)
end
QState.cNot = QState.controlledX

function QState:x(targetBits)
    return self:controlledX(nil, targetBits)
end
QState.Not = QState.x
QState.X = QState.x

function QState:controlledY(controlBits, targetBits)
    return self:controlledApplicatinOfqBitOperator(controlBits, targetBits,  function(amplitudeOf0, amplitudeOf1)
        return {amplitudeOf0 = (amplitudeOf1 * Complex(0, -1)), amplitudeOf1 = (amplitudeOf0 * Complex(0, 1))}
    end)
end

function QState:y(targetBits)
    return self:controlledY(nil, targetBits)
end
QState.Y = QState.y

function QState:controlledZ(controlBits, targetBits)
    return self:controlledApplicatinOfqBitOperator(controlBits, targetBits, function(amplitudeOf0, amplitudeOf1)
        return {amplitudeOf0 = amplitudeOf0, amplitudeOf1 = -amplitudeOf1}
    end)
end

function QState:z(targetBits)
    return self:controlledZ(nil, targetBits)
end
QState.Z = QState.z

function QState:controlledS(controlBits, targetBits)
    -- Note this could actually be implemented as controlledR(controlBits, targetBits, PI/2)
    return self:controlledApplicatinOfqBitOperator(controlBits, targetBits, function(amplitudeOf0, amplitudeOf1)
        return {amplitudeOf0 = amplitudeOf0, amplitudeOf1 = amplitudeOf1 * Complex(0, 1)}
    end)
end

function QState:s(targetBits)
    return self:controlledS(nil, targetBits)
end
QState.S = QState.s

function QState:controlledT(controlBits, targetBits)
    -- Note this could actually be implemented as controlledR(controlBits, targetBits, PI/4)
    local SQRT1_2 = math.sqrt(1/2)
    local expPiOn4 = Complex(SQRT1_2, SQRT1_2)
    return self:controlledApplicatinOfqBitOperator(controlBits, targetBits, function(amplitudeOf0, amplitudeOf1)
        return {amplitudeOf0 = amplitudeOf0, amplitudeOf1 = amplitudeOf1 * expPiOn4}
    end)
end

function QState:t(targetBits)
    return self:controlledT(nil, targetBits)
end
QState.T = QState.t

function QState:controlledSwap(controlBits, targetBit1, targetBit2)
    local newAmplitudes = {}
    if controlBits ~= nil then controlBits = convertBitQualifierToBitArray(controlBits, self.numBits) end
    -- TODO: make sure targetBit1 and targetBit2 are not contained in controlBits.
    local controlBitMask = createBitMask(controlBits)
    local bit1Mask = lshift(1, targetBit1)
    local bit2Mask = lshift(1, targetBit2)
    self:each(function(stateWithAmplitude)
        local state = stateWithAmplitude:asNumber()
        local newState = state
        if ((controlBits == nil) or (band(state, controlBitMask) == controlBitMask)) then
            local newBit2 = lshift(rshift(band(state, bit1Mask), targetBit1), targetBit2)
            local newBit1 = lshift(rshift(band(state, bit2Mask),  targetBit2), targetBit1)
            newState = band(state, bor(bor(band(bnot(bit1Mask), bnot(bit2Mask)), newBit1), newBit2))
        end
        newAmplitudes[newState] = stateWithAmplitude.amplitude
    end)
    return QState(self.numBits, newAmplitudes)
end

function QState:swap(targetBit1, targetBit2)
    return self:controlledSwap(nil, targetBit1, targetBit2)
end

-- Toffoli takes one or more control bits (conventionally two) and one target bit.
function QState:toffoli(...)
    local args = {...}
    if #args < 2 then error("At least one control bit and a target bit must be supplied to calls to toffoli()") end
    local targetBit = table.remove(args)
    local controlBits = args
    return self:controlledX(controlBits, targetBit)
end

function QState:controlledApplicatinOfqBitOperator(controlBits, targetBits, qbitFunction)
    local function applyToOneBit(controlBits, targetBit, qbitFunction, qState)
        local newAmplitudes = {}
        local statesThatCanBeSkipped = {}
        local targetBitMask = lshift(1, targetBit)
        local controlBitMask = createBitMask(controlBits)
        qState:each(function(stateWithAmplitude)
            local state = stateWithAmplitude:asNumber()
            if statesThatCanBeSkipped[stateWithAmplitude.index] then return end
            statesThatCanBeSkipped[bxor(state, targetBitMask)] = true
            local indexOf1 = bor(state, targetBitMask)
            local indexOf0 = indexOf1 - targetBitMask
            if (controlBits == nil) or (band(state, controlBitMask) == controlBitMask) then
                local result = qbitFunction(qState:amplitude(indexOf0), qState:amplitude(indexOf1))
                sparseAssign(newAmplitudes, indexOf0, result.amplitudeOf0)
                sparseAssign(newAmplitudes, indexOf1, result.amplitudeOf1)
            else
                sparseAssign(newAmplitudes, indexOf0, qState:amplitude(indexOf0))
                sparseAssign(newAmplitudes, indexOf1, qState:amplitude(indexOf1))
            end
        end)

        return QState(qState.numBits, newAmplitudes)
    end

    --print("controlledApplicationOfqBitOperator(): " .. self.numBits .. "\nState = " .. inspect(self))
    local targetBitArray = convertBitQualifierToBitArray(targetBits, self.numBits)
    --print("targetBits: ", inspect(targetBits))
    --print("targetBitArray: ", inspect(targetBitArray))
    local controlBitArray = nil
    if controlBits ~= nil then
        controlBitArray = convertBitQualifierToBitArray(controlBits, self.numBits)
        validateControlAndTargetBitsDontOverlap(controlBitArray, targetBitArray)
    end
    local result = self
    for i=0,#targetBitArray do
        local targetBit = targetBitArray[i]
        --print("i: ", i, "targetBit: ", targetBit)
        result = applyToOneBit(controlBitArray, targetBit, qbitFunction, result)
    end
    --print("result: ", inspect(result))
    return result
end

function QState:applyFunction(inputBits, targetBits, functionToApply)
    local function validateTargetBitRangesDontOverlap(controlBits, targetBits)
        if ((controlBits.to >= targetBits.from) and (targetBits.to >= controlBits.from)) then
            error("control and target bits must not be the same nor overlap")
        end
    end

    local qState = self
    local inputBitRange = convertBitQualifierToBitRange(inputBits, self.numBits)
    local targetBitRange = convertBitQualifierToBitRange(targetBits, self.numBits)
    validateTargetBitRangesDontOverlap(inputBitRange, targetBitRange)
    local newAmplitudes = {}
    local statesThatCanBeSkipped = {}
    local highBitMask = lshift(1, inputBitRange.to + 1) - 1
    local targetBitMask = lshift(lshift(1, 1 + targetBitRange.to - targetBitRange.from) - 1, targetBitRange.from)

    self:each(function(stateWithAmplitude)
        local state = stateWithAmplitude:asNumber()
        if statesThatCanBeSkipped[stateWithAmplitude.index] then return end
        local input = rshift(band(state, highBitMask), inputBitRange.from)
        local result = band(lshift(functionToApply(input), targetBitRange.from), targetBitMask)
        local resultingState = bxor(state, result)
        if resultingState == state then
            sparseAssign(newAmplitudes, state, stateWithAmplitude.amplitude)
        else
            statesThatCanBeSkipped[resultingState] = true
            sparseAssign(newAmplitudes, state, qState:amplitude(resultingState))
            sparseAssign(newAmplitudes, resultingState, stateWithAmplitude.amplitude)
        end
    end)

    return QState(self.numBits, newAmplitudes)
end

function QState:normalize()
    local amplitudes = {}
    local sumOfMagnitudeSqaures = 0
    self:each(function(stateWithAmplitude)
        local magnitude = stateWithAmplitude.amplitude:magnitude()
        sumOfMagnitudeSqaures = sumOfMagnitudeSqaures + (magnitude^2)
    end)

    local scale = Real(1 / math.sqrt(sumOfMagnitudeSqaures))
    self:each(function(stateWithAmplitude)
        amplitudes[stateWithAmplitude.index] = stateWithAmplitude.amplitude:multiply(scale)
    end)

    return QState(self.numBits, amplitudes)
end

function QState:measure(bits)
    local numBits = self.numBits
    local bitArray = convertBitQualifierToBitArray(bits, numBits)
    local chosenState = chooseRandomBasisState(self)
    --print("chosenState: ", chosenState)
    local bitMask = createBitMask(bitArray)
    local maskedChosenState = band(chosenState, bitMask)

    local newAmplitudes = {}
    self:each(function(stateWithAmplitude)
        local state = stateWithAmplitude:asNumber()
        if band(state, bitMask) == maskedChosenState then
            newAmplitudes[state] = stateWithAmplitude.amplitude
        end
    end)

    -- Measurement outcome is the "value" of the measured bits.
    -- It probably only makes sense when the bits make an adjacent block.
    local measurementOutcome = 0
    --print("bitArray: ", inspect(bitArray))
    --print("numBits: ", numBits)
    for bitIndex=numBits-1,0,-1 do
        --print("bitIndex: ", bitIndex)
        if indexOf(bitArray, bitIndex) ~= nil then
            measurementOutcome = lshift(measurementOutcome, 1)
            --print("bitIndex: ", bitIndex, "measurementOutcome: ", measurementOutcome)
            if band(chosenState, lshift(1, bitIndex)) ~= 0 then
                measurementOutcome = measurementOutcome + 1
            end
        end
    end

    local newState = QState(self.numBits, newAmplitudes):normalize()
    --print("measurementOutcome: ", measurementOutcome)
    --print("bitArray.length: ", #bitArray+1)
    return Measurement(#bitArray+1, measurementOutcome, newState)
end

function QState:qft(targetBits)
    local function qft(qstate, targetBits)
        local bitIndex = targetBits[0]
        if #targetBits > 1 then --FIXME: Check indexing starts at 0
            qstate = qft(qstate, slice(targetBits, 1))
            for index=1,#targetBits do
                local otherBitIndex = targetBits[index]
                local angle = 2 * math.pi / lshift(1, (index + 1))
                qstate = qstate:controlledR(bitIndex, otherBitIndex, angle)
            end
        end
        return qstate:hadamard(bitIndex)
    end

    local function reverseBits(qstate, targetBits)
        while #targetBits > 1 do
            qstate = qstate:swap(targetBits[0], targetBits[#targetBits])
            targetBits = slice(targetBits, 1, #targetBits)
        end
        return qstate
    end

    local targetBitArray = convertBitQualifierToBitArray(targetBits, self.numBits)
    local newState = qft(self, targetBitArray)
    return reverseBits(newState, targetBitArray)
end

function QState:__eq(other)
    local function lhsAmplitudesHaveMatchingRhsAmplitudes(lhs, rhs)
        local result = true
        lhs:each(function(stateWithAmplitude)
            if stateWithAmplitude.amplitude ~= rhs:amplitude(stateWithAmplitude:asNumber()) then
                result = false
                return false
            end
        end)
        return result
    end

    if not other then return false end
    if not instanceOf(other, QState) then return false end
    if self.numBits ~= other.numBits then return false end
    return lhsAmplitudesHaveMatchingRhsAmplitudes(self, other) and lhsAmplitudesHaveMatchingRhsAmplitudes(other, self)
end

function QState:__tostring()
    local function formatAmplitude(amplitude, formatFlags)
        local amplitudeString = amplitude:format(formatFlags)
        return ((amplitudeString == '1') and '' or ('(' .. amplitudeString .. ')'))
    end

    local function compareStatesWithAmplitudes(a, b)
        return (a:asNumber() < b:asNumber())
    end

    local function sortedNonZeroStates(qState)
        local nonZeroStates = {}
        qState:each(function(stateWithAmplitude)
            table.insert(nonZeroStates, stateWithAmplitude)
        end)
        table.sort(nonZeroStates, compareStatesWithAmplitudes)
        return nonZeroStates
    end

    local result, formatFlags, nonZeroStates, stateWithAmplitude
    result = ''
    formatFlags = {decimalPlaces = 4}
    nonZeroStates = sortedNonZeroStates(self)
    for i=1,#nonZeroStates do
        if result ~= '' then result = result .. " + " end
        stateWithAmplitude = nonZeroStates[i]
        result = result .. formatAmplitude(stateWithAmplitude.amplitude, formatFlags) .. "|" .. stateWithAmplitude:asBitString() .. ">"
    end
    return result
end

--Module qubits
qubits.__index = qubits
setmetatable(qubits, qubits)

qubits.__call = function(cls, bitString) --Constructor
    return cls.QState:fromBits(bitString)
end

qubits.ZERO = Complex.ZERO
qubits.ONE = Complex.ONE
qubits.ALL = 'ALL'

qubits.roundToZero = 1e-8 --Amplitudes smaller than this are rounded off to zero

qubits.Qmath = Qmath
qubits.Complex = Complex
qubits.Real = Real
qubits.Measurement = Measurement
qubits.StateWithAmplitude = StateWithAmplitude
qubits.QState = QState

return qubits
