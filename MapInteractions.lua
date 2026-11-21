local _,A=...
local function controlDown() return IsControlKeyDown and IsControlKeyDown() end
local hoveredPoint
function A.IsWaypointClick(button)
    return button=='RightButton' and IsAltKeyDown and IsAltKeyDown() and not controlDown() and not (IsShiftKeyDown and IsShiftKeyDown())
end
local function point(map,x,y,name)
    local info=C_Map.GetMapInfo and C_Map.GetMapInfo(map)
    return {map=map,x=x,y=y,name=name or (info and info.name or 'Waypoint')}
end
function A.HandleMapClick(map,button,x,y)
    -- Leave Ctrl entirely to the game's ping system, including Ctrl+Alt chords.
    if controlDown() then return false end
    local waypoint=A.IsWaypointClick(button)
    local note=button=='LeftButton' and IsAltKeyDown and IsAltKeyDown() and not (IsShiftKeyDown and IsShiftKeyDown())
    if not waypoint and not note then return false end
    local p=waypoint and hoveredPoint(map) or nil
    p=p or point(map:GetMapID(),x,y)
    if A.ValidPin(p) then
        if waypoint then
            if A.MarkWaypointHandled then A.MarkWaypointHandled() end
            A.Navigation.ToPin(p)
        else A.ShowNote(p.map,p.x,p.y) end
    end
    -- Consume modifier clicks before native waypoint, zone-navigation or zoom handlers.
    return true
end
local function mouseFocus()
    if GetMouseFoci then local list=GetMouseFoci();return list and list[1] end
    if GetMouseFocus then return GetMouseFocus() end
end
hoveredPoint=function(map)
    local focus=mouseFocus();local frame=focus
    local canvas=map:GetCanvas();local inside=false;local record;local name
    for _=1,16 do
        if not frame then break end
        local data=type(frame.node)=='table' and frame.node or type(frame.data)=='table' and frame.data
        if not name and data and type(data.name)=='string' then name=data.name end
        if not record and type(frame.GetMap)=='function' and type(frame.GetPosition)=='function' then
            local ok,owner=pcall(frame.GetMap,frame)
            if ok and owner==map then
                local valid,x,y=pcall(frame.GetPosition,frame)
                if valid then local p=point(map:GetMapID(),x,y,name);if A.ValidPin(p) then record=p end end
            end
        end
        if frame==canvas then inside=true;break end
        frame=frame:GetParent()
    end
    if not inside then return end
    if not record then local x,y=map:GetNormalizedCursorPosition();record=point(map:GetMapID(),x,y,name) end
    if name then record.name=name end
    if A.ValidPin(record) then return record,focus end
end
local function start(p)
    -- GLOBAL_MOUSE_UP can follow the native pin handler for the same click.
    local active=A.Navigation.target
    if active and active.map==p.map and math.abs(active.x-p.x)<.000001 and math.abs(active.y-p.y)<.000001 then return end
    A.Navigation.ToPin(p)
end
function A.AttachMapInteractions(map)
    local pressed
    A.MarkWaypointHandled=function() if pressed then pressed.handled=true end end
    if map.AddCanvasClickHandler then map:AddCanvasClickHandler(A.HandleMapClick,1000) end
    if map.AddGlobalPinMouseActionHandler then
        map:AddGlobalPinMouseActionHandler(function(owner,action,button)
            local click=MapCanvasMixin and MapCanvasMixin.MouseAction and MapCanvasMixin.MouseAction.Click or 3
            if action~=click or not A.IsWaypointClick(button) then return false end
            local p=hoveredPoint(owner)
            if p then A.MarkWaypointHandled();start(p);return true end
            return false
        end,1000)
    end
    -- Some addons put a raw button inside a native/HBD pin and bypass its click
    -- handlers. Observe their Alt-right-clicks without replacing addon scripts.
    local events=CreateFrame('Frame');A.waypointMouseEvents=events
    events:RegisterEvent('GLOBAL_MOUSE_DOWN');events:RegisterEvent('GLOBAL_MOUSE_UP')
    events:SetScript('OnEvent',function(_,event,button)
        if event=='GLOBAL_MOUSE_DOWN' then
            pressed=nil
            if A.IsWaypointClick(button) and map:IsShown() then
                local p,focus=hoveredPoint(map)
                if p then local x,y=GetCursorPosition();pressed={x=x,y=y,map=map:GetMapID(),focus=focus,pin=p} end
            end
        elseif button=='RightButton' then
            local down=pressed
            if not down or not A.IsWaypointClick(button) or not map:IsShown() or down.map~=map:GetMapID() then pressed=nil;return end
            local x,y=GetCursorPosition()
            if math.abs(x-down.x)>4 or math.abs(y-down.y)>4 then pressed=nil;return end
            local p,focus=hoveredPoint(map)
            if p and focus==down.focus then
                -- Let the current native click finish before a refresh releases pins.
                -- Overridden OnClick methods may bypass the native global dispatcher.
                C_Timer.After(0,function()
                    if not down.handled then start(down.pin) end
                    if pressed==down then pressed=nil end
                end)
            else pressed=nil end
        end
    end)
end
