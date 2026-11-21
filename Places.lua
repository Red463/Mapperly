local _,A=...
function A.PlacesForMap(map)
    local result={}
    local hbd=LibStub('HereBeDragons-2.0',true)
    local function add(instance,x,y,name,category,description,direct,kind)
        if direct then if direct~=map then return end
        -- OpenMap stores game world north/east; HBD expects horizontal/vertical.
        elseif hbd then x,y=hbd:GetZoneCoordinatesFromWorldInstance(y,x,instance,map)
        else return end
        local p={map=map,x=x,y=y,name=name,category=category,description=description,kind=kind}
        if A.ValidPin(p) then result[#result+1]=p end
    end
    for _,v in ipairs(A.MapPlaces.instances) do
        local names={};for _,d in ipairs(v[4]) do names[#names+1]=d[2]..' ('..d[4]..'–'..d[5]..')' end
        add(v[1],v[2],v[3],table.concat(names,', '),'dungeon',nil,v.map)
    end
    for _,v in ipairs(A.MapPlaces.transports) do
        add(v[3],v[4],v[5],v[2],'transport',v[1]..' route: '..v[2],nil,v[1])
    end
    local faction=UnitFactionGroup('player')=='Alliance' and 1 or 2
    for _,v in pairs(A.MapFlights.nodes) do if v[5]==faction then add(v[2],v[3],v[4],v[1],'flight','Flight master; availability depends on discovered routes.') end end
    return result
end
