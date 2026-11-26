local _,A=...
local cities={[1453]=true,[1454]=true,[1455]=true,[1456]=true,[1457]=true,[1458]=true}
local function clearHoverFishing(label)if A.UpdateHoverFishing then A.UpdateHoverFishing(label) end end
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
function A.PositionHoverZoneLabel(label,force)
    if not A.map or not A.map.ScrollContainer then return end
    if A.db.theme=='gatherly' then
        if not label.mapperlyOriginalLabelPoints then
            local points={};label.mapperlyOriginalLabelPoints=points
            for i=1,(label:GetNumPoints() or 1) do
                local point,relative,relativePoint,x,y=label:GetPoint(i)
                if point then points[#points+1]={point,relative,relativePoint,x,y} end
            end
        end
        if force or not label.mapperlyLabelOffsetApplied then
            local offset=A.FishingLabel and A.FishingLabel(A.map:GetMapID()) and -60 or -40
            label:ClearAllPoints();label:SetPoint('TOP',A.map.ScrollContainer,'TOP',0,offset)
            label.mapperlyLabelOffsetApplied=true
        end
    elseif label.mapperlyLabelOffsetApplied then
        label:ClearAllPoints()
        local points=label.mapperlyOriginalLabelPoints or {}
        for _,p in ipairs(points) do label:SetPoint(p[1],p[2],p[3],p[4],p[5]) end
        if #points==0 then label:SetPoint('TOP',A.map.ScrollContainer,'TOP',0,-10) end
        label.mapperlyLabelOffsetApplied=false
    end
end
function A.UpdateHoverZoneLabel(label)
    A.PositionHoverZoneLabel(label)
    local map=A.map
    local info=C_Map.GetMapInfo and C_Map.GetMapInfo(map:GetMapID())
    local continentType=Enum and Enum.UIMapType and Enum.UIMapType.Continent or 2
    if not info or info.mapType~=continentType or not C_Map.GetMapInfoAtPosition then clearHoverFishing(label);return end
    local areaType=MAP_AREA_LABEL_TYPE and MAP_AREA_LABEL_TYPE.AREA_NAME or 3
    local area=label.labelInfoByType and label.labelInfoByType[areaType]
    if not area or not area.name or label:GetHighestPriorityLabelInfo()~=area then clearHoverFishing(label);return end
    -- Match AreaLabelFrameMixin's input choice so our extra rows describe
    -- the same zone as the native controller or mouse hover caption.
    local gamepad=InputUtil and InputUtil.IsGamepadUIEnabled and InputUtil.IsGamepadUIEnabled()
        and (map.HasGamepadCursorInput and map:HasGamepadCursorInput()
            or map.IsCanvasMouseFocusOrPinFocus and not map:IsCanvasMouseFocusOrPinFocus())
    local x,y
    if gamepad then
        if map.GetNormalizedGamepadCursorPosition then x,y=map:GetNormalizedGamepadCursorPosition() end
    else x,y=map:GetNormalizedCursorPosition() end
    if not x or not y or x<0 or x>1 or y<0 or y>1 then clearHoverFishing(label);return end
    local hovered=C_Map.GetMapInfoAtPosition(map:GetMapID(),x,y)
    if hovered and hovered.mapID and hovered.mapID~=map:GetMapID() and hovered.name then
        label.Name:SetText(A.ZoneTitle(hovered.mapID,hovered.name))
        if A.UpdateHoverFishing then A.UpdateHoverFishing(label,hovered.mapID) end
    else clearHoverFishing(label) end
end
function A.AttachZoneLevels()
    for provider in pairs(A.map.dataProviders or {}) do
        local label=provider.Label
        if (type(label)=='table' or type(label)=='userdata') and label.Name and label.GetHighestPriorityLabelInfo then
            if not label.mapperlyLevelsHooked then
                label.mapperlyLevelsHooked=true
                label:HookScript('OnUpdate',function(self) A.UpdateHoverZoneLabel(self) end)
                label:HookScript('OnHide',clearHoverFishing)
            end
            A.PositionHoverZoneLabel(label,true)
        end
    end
end
