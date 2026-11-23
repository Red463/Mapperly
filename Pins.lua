local _, A = ...
local media='Interface\\AddOns\\Mapperly\\Media\\Markers\\'
local textures={mail='Mail',inn='Hearthstone',dungeon='Dungeon',flight='FlightMaster',transport='Boat',portal='Portal',border='ZoneExit',notes='Note',quest='Quest',navigation='Destination'}
for key,name in pairs({enemy='Enemy',chest='Chest',poi='POI',scenic='Scenic',building='Building',danger='Danger',camp='Camp',meeting='Meeting',resource='Resource',fishing='Fishing',cave='Cave',travel='Travel'}) do textures['note_'..key]='Note'..name end
local transports={boat='Boat',zeppelin='Zeppelin',airship='Airship'}
function A.SetPinTexture(texture,category,kind,size)
    texture:SetTexCoord(0,1,0,1)
    local name=category=='transport' and transports[kind] or nil
    local directory=media..(size and (size<=24 and 'Small\\' or 'Medium\\') or '')
    if type(texture.SetSnapToPixelGrid)=='function' then texture:SetSnapToPixelGrid(true) end
    if type(texture.SetTexelSnappingBias)=='function' then texture:SetTexelSnappingBias(0) end
    if not texture:SetTexture(directory..(name or textures[category] or textures.notes)) then texture:SetTexture('Interface\\Minimap\\Tracking\\Innkeeper') end
end
A.pinPool={}
function A.IsOverviewMap(map)
    local info=C_Map.GetMapInfo and C_Map.GetMapInfo(map)
    local continent=Enum and Enum.UIMapType and Enum.UIMapType.Continent or 2
    return info and type(info.mapType)=='number' and info.mapType<=continent or false
end
-- Register through MapCanvas so the native manager owns layer, scale and position.
-- Raw canvas children are not registered pins and can sit under the detail layers.
MapperlyMapPinMixin={}
function MapperlyMapPinMixin:ShouldMouseButtonBePassthrough(button)
    -- Native AcquirePin recalculates this after OnAcquired, including reused pins.
    -- Notes and navigation destinations own right-click; other pins retain map navigation.
    return button=='RightButton' and not (self.data and (self.data.category=='notes' or self.data.category=='navigation'))
end
function MapperlyMapPinMixin:OnLoad()
    self:UseFrameLevelType('PIN_FRAME_LEVEL_AREA_POI')
    self:SetScalingLimits(1,1,1)
    self:RegisterForClicks('LeftButtonUp','RightButtonUp')
end
function MapperlyMapPinMixin:OnAcquired(data)
    self.data=data
    -- HBD/Gatherly resource nodes use AREA_POI. GOSSIP is the next native tier,
    -- below active quests and group/player arrows, and survives native relayering.
    self:UseFrameLevelType(data.category=='navigation' and 'PIN_FRAME_LEVEL_WAYPOINT_LOCATION' or A.IsOverviewMap(data.map) and 'PIN_FRAME_LEVEL_AREA_POI' or 'PIN_FRAME_LEVEL_GOSSIP')
    self:SetSize(A.db.iconSize,A.db.iconSize)
    self:SetPosition(data.x,data.y)
    A.SetPinTexture(self.icon,data.category=='notes' and data.icon or data.category,data.kind,A.db.iconSize)
    if A.map.AddMaskableTexture then A.map:AddMaskableTexture(self.icon) end
end
local function tooltip(self)
    self.hoverBaseLevel=self:GetFrameLevel()
    self:SetFrameLevel(self.hoverBaseLevel+20)
    GameTooltip:SetOwner(self,'ANCHOR_RIGHT');GameTooltip:SetText(self.data.name)
    if self.data.category=='dungeon' then GameTooltip:Show();return end
    if self.data.group and self.data.group~='' then GameTooltip:AddLine(self.data.group,1,.82,0) end
    if self.data.description and self.data.description~='' then GameTooltip:AddLine(self.data.description,1,1,1,true) end
    GameTooltip:AddLine(string.format('%.1f, %.1f',self.data.x*100,self.data.y*100),.8,.8,.8)
    if self.data.target then GameTooltip:AddLine('Click to open destination map.') end
    if self.data.category=='notes' then GameTooltip:AddLine('Click to edit; Shift-click to share; right-click to remove.') end
    if self.data.category=='navigation' then GameTooltip:AddLine('Left-click to edit; right-click to stop navigation.') end
    if A.TransportLinks and #A.TransportLinks.ForPin(self.data)>0 then GameTooltip:AddLine('Click to choose a travel destination.',1,.82,0) end
    GameTooltip:AddLine('Alt-right-click to navigate here.',1,.82,0)
    GameTooltip:Show()
end
function MapperlyMapPinMixin:OnMouseEnter()
    tooltip(self)
    if A.BoatLinks then A.BoatLinks.Hover(self.data) end
end
function MapperlyMapPinMixin:OnMouseLeave()
    if A.BoatLinks then A.BoatLinks.Clear(self.data) end
    if self.hoverBaseLevel then self:SetFrameLevel(self.hoverBaseLevel);self.hoverBaseLevel=nil end
    GameTooltip:Hide()
end
function MapperlyMapPinMixin:OnReleased()
    if self.data and A.BoatLinks then A.BoatLinks.Clear(self.data) end
    if self.hoverBaseLevel then self:SetFrameLevel(self.hoverBaseLevel);self.hoverBaseLevel=nil end
    if GameTooltip:IsOwned(self) then GameTooltip:Hide() end
end
function MapperlyMapPinMixin:OnClick(button)
    local p=self.data
    if IsControlKeyDown and IsControlKeyDown() then
        -- Own pins override the native OnClick: explicitly pass ping clicks on.
        local click=MapCanvasMixin and MapCanvasMixin.MouseAction and MapCanvasMixin.MouseAction.Click or 3
        if A.map and A.map.ProcessGlobalPinMouseActionHandlers and A.map:ProcessGlobalPinMouseActionHandlers(click,button) then return end
        if A.map and A.map.ProcessCanvasClickHandlers then A.map:ProcessCanvasClickHandlers(button,p.x,p.y) end
        return
    elseif A.IsWaypointClick and A.IsWaypointClick(button) then
        if A.MarkWaypointHandled then A.MarkWaypointHandled() end
        A.Navigation.ToPin(p.category=='navigation' and A.Navigation.target or p)
    elseif p.category=='navigation' then
        if button=='RightButton' then A.Navigation.Stop() else A.ShowNavigationInput(A.Navigation.target and A.Navigation.target.map) end
    elseif button=='LeftButton' and A.TransportLinks and A.TransportLinks.Show(p) then return
    elseif p.target then A.map:SetMapID(p.target)
    elseif p.category=='notes' then
        if button=='RightButton' then
            A.RemoveNote(p)
            GameTooltip:Hide()
            A.RefreshPins()
        elseif IsShiftKeyDown() then A.Share(p)
        else A.ShowNote(p.map,p.x,p.y,p) end
    end
end
function A.RefreshPins()
    A.map:RemoveAllPinsByTemplate('MapperlyMapPinTemplate')
    A.pinPool={}
    local map=A.map:GetMapID();if not map then return end
    local list=A.PinsForMap(map)
    local overview=A.IsOverviewMap(map)
    for _,p in ipairs(list) do if p.map==map and A.db.filters[p.category] and (not overview or A.db.continentFilters[p.category]) then
            local f=A.map:AcquirePin('MapperlyMapPinTemplate',p)
            A.pinPool[#A.pinPool+1]=f
    end end
    local destination=A.Navigation and A.Navigation.PinForMap(map)
    if destination then A.pinPool[#A.pinPool+1]=A.map:AcquirePin('MapperlyMapPinTemplate',destination) end
end
function A.Share(p)
    local text=string.format('%s (map %d, %.1f, %.1f)',p.name,p.map,p.x*100,p.y*100)
    if ChatEdit_InsertLink then ChatEdit_InsertLink(text) end
end
