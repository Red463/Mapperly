local _,A=...
local L={};A.TransportLinks=L
L.methods={boat='Boat',zeppelin='Zeppelin',airship='Airship',flight='Flight'}
function L.Available()
    local rows={}
    for _,edge in ipairs(A.Transports and A.Transports.Edges() or {}) do
        local row=edge.transport
        if row and L.methods[row.kind] then rows[#rows+1]=row end
    end
    table.sort(rows,function(a,b) return (a.toName or a.name or '')..a.id<(b.toName or b.name or '')..b.id end)
    return rows
end
function L.IdentifyFlight(instance,north,east)
    local best,distance
    for id,node in pairs(A.FlightData and A.FlightData.nodes or {}) do
        local d=node.world and A.TravelNetwork.Distance(node.world,{worldX=east,worldY=north,instance=instance})
        if d and d<=60 and (not distance or d<distance) then best=id;distance=d end
    end
    return best
end
function L.ForPin(pin)
    local result={}
    if not pin or (pin.category~='transport' and pin.category~='flight') then return result end
    if A.db and (not A.db.filters[pin.category] or (pin.map==947 or A.IsOverviewMap(pin.map)) and not A.db.continentFilters[pin.category]) then return result end
    local rows=L.Available();local source
    if pin.transportID then for _,row in ipairs(rows) do if row.id==pin.transportID then source=row;break end end end
    for _,row in ipairs(rows) do
        local match=pin.category=='flight' and pin.flightNodeID and row.kind=='flight' and row.fromNodeID==pin.flightNodeID
        if pin.category=='transport' and source and row.kind==source.kind then
            local d=A.TravelNetwork.Distance(row.board,source.board);match=d and d<=20
        end
        if match then result[#result+1]=row end
    end
    return result
end
function L.Visible(map)
    local rows={}
    for _,row in ipairs(L.Available()) do
        local category=row.kind=='flight' and 'flight' or 'transport'
        local x,y
        if A.JourneyView then x,y=A.JourneyView.Project(row.board,map) end
        if A.db.filters[category] and A.db.continentFilters[category] and x and y and x>=0 and x<=1 and y>=0 and y<=1 then rows[#rows+1]=row end
    end
    return rows
end
function L.Act(pin,id,navigate)
    for _,row in ipairs(L.ForPin(pin)) do if row.id==id then
        local p={map=row.b.mapID,x=row.b.x,y=row.b.y,name=row.toName or row.name or 'Destination'}
        if navigate then return A.Navigation.ToPin(p) end
        return A.JourneyView.Preview(p)
    end end
    return nil,'This connection is no longer available. Check travel settings, recorded flights and flight funds.'
end
