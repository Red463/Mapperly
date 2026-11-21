local _,A=...
A.ServicePins={}
local signatures={}
function A.LoadServices(map)
    map=map or (A.map and A.map:GetMapID())
    if not map then return end
    local hbd=LibStub('HereBeDragons-2.0',true)
    if not hbd then return end
    local faction=UnitFactionGroup('player')=='Horde' and 'H' or 'A'
    local signature=faction..':'..tostring(hbd.mapData and hbd.mapData[map])
    if signatures[map]==signature then return end
    local pins={}
    for _,row in ipairs(A.BundledServices or {}) do
        if not row.access or row.access:find(faction,1,true) then
            local x,y=hbd:GetZoneCoordinatesFromWorldInstance(row.y,row.x,row.instance,map)
            local p={map=map,x=x,y=y,name=row.name,category=row.category,id=row.id,access=row.access,
                description='Bundled Mapperly location (Forever database snapshot).'}
            if A.ValidPin(p) then pins[#pins+1]=p end
        end
    end
    A.ServicePins[map]=pins
    if (hbd.mapData and hbd.mapData[map]) or #pins>0 then signatures[map]=signature end
end
function A.PinsForMap(map)
    A.LoadServices(map)
    local pins={};local faction=UnitFactionGroup('player')=='Horde' and 'H' or 'A'
    for _,source in ipairs({A.PlacesForMap(map),A.ServicePins[map] or {},A.db.observed,A.db.notes}) do
        for _,p in ipairs(source) do
            if A.ValidPin(p) and p.map==map and (not p.access or p.access:find(faction,1,true)) then
                local duplicate=false
                if p.category=='mail' or p.category=='inn' or p.category=='flight' then
                    for _,other in ipairs(pins) do
                        if other.category==p.category and math.abs(other.x-p.x)<=.003 and math.abs(other.y-p.y)<=.003 then duplicate=true;break end
                    end
                end
                if not duplicate then pins[#pins+1]=p end
            end
        end
    end
    if C_Map.GetMapLinksForMap then
        for _,v in ipairs(C_Map.GetMapLinksForMap(map) or {}) do
            if v.position then
                local x,y=v.position:GetXY()
                local p={map=map,x=x,y=y,name=v.name or 'Zone exit',category='border',target=v.linkedUiMapID}
                if A.ValidPin(p) then pins[#pins+1]=p end
            end
        end
    end
    return pins
end
