local _,A=...
function A.FishingRange(map)
    local data=A.FishingLevelsData;local row=data and data.maps[map]
    if not row then return end
    local info=C_Map.GetMapInfo and C_Map.GetMapInfo(map)
    local zone=Enum and Enum.UIMapType and Enum.UIMapType.Zone or 3
    if info and type(info.mapType)=='number' and info.mapType~=zone then return end
    return row.minimum,row.recommended,row.maximum or row.minimum,row.recommendedMaximum or row.recommended,row
end
function A.FishingLabel(map)
    local lo,rec,hi,highRec=A.FishingRange(map)
    if not lo then return end
    local minimum=lo==hi and tostring(lo) or lo..'–'..hi
    local recommended=rec==highRec and tostring(rec) or rec..'–'..highRec
    return 'Fishing: '..minimum..'+ · Recommended: '..recommended
end
local function hoverDescription(label,fishing)
    local description=label.Description
    if type(description)~='table' and type(description)~='userdata' then return end
    if fishing then
        if not label.mapperlyDescriptionPoints then
            local points={};label.mapperlyDescriptionPoints=points
            for i=1,(description:GetNumPoints() or 1) do
                local point,relative,anchor,x,y=description:GetPoint(i)
                if point then points[#points+1]={point,relative,anchor,x,y} end
            end
        end
        description:ClearAllPoints();description:SetPoint('TOP',fishing,'BOTTOM',0,-6)
    elseif label.mapperlyDescriptionPoints then
        description:ClearAllPoints()
        for _,point in ipairs(label.mapperlyDescriptionPoints) do description:SetPoint(unpack(point)) end
        label.mapperlyDescriptionPoints=nil
    end
end
function A.UpdateHoverFishing(label,map)
    local f=label.mapperlyFishing
    if not map then
        label.mapperlyFishingMap=nil
        if f then f:Hide() end
        hoverDescription(label)
        return
    end
    local scale=label:GetScale()
    if type(scale)~='number' or scale~=scale or scale<=0 or scale==math.huge then scale=1 end
    local width=math.max(1,A.map.ScrollContainer:GetWidth()-48)/scale
    if f and label.mapperlyFishingMap==map and f:IsShown() and f:GetWidth()==width and f.mapperlyScale==scale then return end
    local caption=A.FishingLabel(map)
    if not caption then return A.UpdateHoverFishing(label) end
    if not f then
        -- A decorative child of the native hover label: no mouse region or
        -- tracking/tooltip hooks that could interfere with map navigation.
        f=label:CreateFontString(nil,'OVERLAY','GameFontHighlightSmall');label.mapperlyFishing=f
        f.mapperlyBaseFont={f:GetFont()}
        f:SetJustifyH('CENTER');f:SetWordWrap(false)
        f:SetTextColor(1,1,1,1);f:SetShadowColor(0,0,0,1);f:SetShadowOffset(1,-1)
    end
    local font=f.mapperlyBaseFont
    if type(font[1])=='string' then f:SetFont(font[1],14/scale,font[3]) end
    f:ClearAllPoints();f:SetPoint('TOP',label.Name,'BOTTOM',0,-6/scale);f:SetHeight(22/scale)
    label.mapperlyFishingMap=map;f.mapperlyScale=scale;f:SetWidth(width);f:SetText(caption);f:Show()
    hoverDescription(label,f)
end
local function tooltip(f)
    local lo,rec,hi,highRec,row=A.FishingRange(f.mapID)
    if not lo then return end
    GameTooltip:SetOwner(f,'ANCHOR_BOTTOM')
    GameTooltip:SetText('Fishing skill')
    GameTooltip:AddLine('Minimum to fish: '..lo..(lo~=hi and '–'..hi or '')..'.',1,1,1,true)
    GameTooltip:AddLine('Recommended for reliable catches: '..rec..(rec~=highRec and '–'..highRec or '')..'.',1,1,1,true)
    if row.waters then GameTooltip:AddLine('Varies by water. '..row.waters,1,.82,0,true) end
    GameTooltip:AddLine('Includes lure skill bonuses. Pools and special waters may differ.',.8,.8,.8,true)
    GameTooltip:Show()
end
function A.UpdateFishingHeading()
    if not A.map or not A.zoneHeadingHost then return end
    local id=A.map:GetMapID();local caption=id and A.FishingLabel(id)
    local f=A.fishingHeading
    if not caption then
        if f then f:Hide() end
    else
        if not f then
            f=CreateFrame('Frame',nil,A.zoneHeadingHost);A.fishingHeading=f
            f:EnableMouse(false);f:EnableMouseMotion(true)
            f.text=f:CreateFontString(nil,'OVERLAY','GameFontHighlightSmall')
            f.text:SetAllPoints(f);f.text:SetWordWrap(false)
            f.text:SetTextColor(1,1,1,1);f.text:SetShadowColor(0,0,0,1);f.text:SetShadowOffset(1,-1)
            f:SetScript('OnEnter',tooltip)
            local function hide(self)if GameTooltip:IsOwned(self) then GameTooltip:Hide() end end
            f:SetScript('OnLeave',hide);f:SetScript('OnHide',hide)
        end
        f.mapID=id;f.text:SetText(caption);f:ClearAllPoints()
        local width=f.text:GetStringWidth()
        if type(width)~='number' or width~=width or width<=0 then width=#caption*7 end
        local viewport=A.map.ScrollContainer
        f:SetSize(math.max(1,math.min(width+8,viewport:GetWidth()-48)),18)
        if A.db.theme=='gatherly' then
            f:SetPoint('TOP',viewport,'TOP',0,-34);f.text:SetJustifyH('CENTER')
        else
            f:SetPoint('TOPLEFT',viewport,'TOPLEFT',12,-6);f.text:SetJustifyH('LEFT')
        end
        f:Show()
        if GameTooltip:IsOwned(f) and f:IsVisible() then tooltip(f) end
    end
    -- Native subzone/continent hover captions occupy a separate row.
    if A.PositionHoverZoneLabel then
        for provider in pairs(A.map.dataProviders or {}) do
            local label=provider.Label
            if (type(label)=='table' or type(label)=='userdata') and label.Name and label.GetHighestPriorityLabelInfo then A.PositionHoverZoneLabel(label,true) end
        end
    end
end
