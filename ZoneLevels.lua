local _,A=...
local cities={[1453]=true,[1454]=true,[1455]=true,[1456]=true,[1457]=true,[1458]=true}
function A.ZoneLevelRange(map)
    if cities[map] then return end
    local info=C_Map.GetMapInfo and C_Map.GetMapInfo(map)
    local zoneType=Enum and Enum.UIMapType and Enum.UIMapType.Zone or 3
    if info and info.mapType~=zoneType then return end
    if C_Map.GetMapLevels then
        local ok,lo,hi=pcall(C_Map.GetMapLevels,map)
        if ok and type(lo)=='number' and type(hi)=='number' and lo>0 and hi>=lo then return lo,hi,'Client map levels' end
    end
    local range=A.ZoneLevels and A.ZoneLevels[map]
    if range then return range[1],range[2],'Bundled zone recommendations' end
end
function A.ZoneTitle(map,name)
    local lo,hi=A.ZoneLevelRange(map)
    if not lo then return name end
    return name..' ('..lo..(lo~=hi and '–'..hi or '')..')'
end
function A.UpdateHoverZoneLabel(label)
    local map=A.map
    local info=C_Map.GetMapInfo and C_Map.GetMapInfo(map:GetMapID())
    local continentType=Enum and Enum.UIMapType and Enum.UIMapType.Continent or 2
    if not info or info.mapType~=continentType or not C_Map.GetMapInfoAtPosition then return end
    local areaType=MAP_AREA_LABEL_TYPE and MAP_AREA_LABEL_TYPE.AREA_NAME or 3
    local area=label.labelInfoByType and label.labelInfoByType[areaType]
    if not area or not area.name or label:GetHighestPriorityLabelInfo()~=area then return end
    local x,y=map:GetNormalizedCursorPosition()
    if not x or not y or x<0 or x>1 or y<0 or y>1 then return end
    local hovered=C_Map.GetMapInfoAtPosition(map:GetMapID(),x,y)
    if hovered and hovered.mapID~=map:GetMapID() and A.ZoneLevelRange(hovered.mapID) then
        label.Name:SetText(A.ZoneTitle(hovered.mapID,hovered.name))
    end
end
function A.AttachZoneLevels()
    for provider in pairs(A.map.dataProviders or {}) do
        local label=provider.Label
        if (type(label)=='table' or type(label)=='userdata') and label.Name and label.GetHighestPriorityLabelInfo and not label.mapperlyLevelsHooked then
            label.mapperlyLevelsHooked=true
            label:HookScript('OnUpdate',function(self) A.UpdateHoverZoneLabel(self) end)
        end
    end
end
