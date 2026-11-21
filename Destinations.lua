local _,A=...
local D={};A.Destinations=D
local function copy(p)
    if not A.ValidPin(p) then return end
    local name=p.name:sub(1,120)
    if name:match('^%s*$') then name='Waypoint' end
    return {map=p.map,x=p.x,y=p.y,name=name}
end
local function same(a,b)
    return a.map==b.map and math.abs(a.x-b.x)<.000001 and math.abs(a.y-b.y)<.000001
end
local function removeMatch(list,p)
    for i=#list,1,-1 do if same(list[i],p) then table.remove(list,i) end end
end
function D.Normalize()
    for _,key in ipairs({'savedDestinations','destinationHistory'}) do
        local clean={}
        for _,p in ipairs(A.ArrayValues(A.db[key])) do
            local record=copy(p)
            if record then
                local duplicate=false
                for _,old in ipairs(clean) do if same(old,record) then duplicate=true;break end end
                if not duplicate then clean[#clean+1]=record end
            end
            if key=='destinationHistory' and #clean>=20 then break end
        end
        A.db[key]=clean
    end
end
function D.Save(p)
    local record=copy(p);if not record then return false end
    removeMatch(A.db.savedDestinations,record)
    table.insert(A.db.savedDestinations,1,record);return record
end
function D.Remove(p)
    for i,v in ipairs(A.db.savedDestinations) do if v==p then table.remove(A.db.savedDestinations,i);return true end end
    return false
end
function D.Update(original,p)
    local record=copy(p);if not record then return false end
    local found=false
    for _,v in ipairs(A.db.savedDestinations) do if v==original then found=true;break end end
    if not found then return false end
    D.Remove(original);removeMatch(A.db.savedDestinations,record)
    table.insert(A.db.savedDestinations,1,record);return record
end
function D.Remember(p)
    local record=copy(p);if not record then return false end
    local list=A.db.destinationHistory
    removeMatch(list,record);table.insert(list,1,record)
    while #list>20 do table.remove(list) end
    return record
end
function D.ClearHistory() A.db.destinationHistory={} end
