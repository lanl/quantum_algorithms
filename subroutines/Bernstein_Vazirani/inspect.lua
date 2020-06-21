--REMARK: This is a pure Lua module
--
--Recursively print arbitrary Lua tables/data
local repeats = string.rep
local formats = string.format
local function inspect(data, showHidden, limit, level, s, keepLast)
    local showHidden = showHidden or false --Show [[meta]]?
    local limit = limit or 2 --Stop at level 2
    local level = level or 1 --Start at level 1
    local s = s or {} --Table of string pieces
    local keepLast = keepLast or false --Keep last entry in s?

    local typeof = type(data)
    if (typeof ~= "table") then
        if typeof == "string" then
            s[#s+1] = formats("%q", data)
            s[#s+1] = "\n"
        else
            s[#s+1] = tostring(data)
            s[#s+1] = "\n"
        end
    else
        if (level > limit) then
            s[#s+1] = "{...}"
            s[#s+1] = "\n"
        else
            --Recursively print table
            s[#s+1] = "{\n"
            local indent = repeats(" ", 2*level)

            --Print attributes
            for k,v in pairs(data) do
                s[#s+1] = indent .. tostring(k) .. ": "
                inspect(v, showHidden, limit, level+1, s, true)
            end

            if showHidden then
                --Print metamethods
                local mt = getmetatable(data)
                if mt then
                    s[#s+1] = indent .. "[[meta]]: "
                    inspect(mt, showHidden, limit, level+1, s, true)
                end
            end

            indent = repeats(" ", 2*(level-1))
            s[#s+1] = indent .. "}"
            s[#s+1] = "\n"
        end
    end
    if not keepLast then s[#s] = "" end
    return table.concat(s)
end	
return inspect
