local _,A=...
local B={lines={}};A.BoatLinks=B
local function overview(map) return map==947 or A.IsOverviewMap and A.IsOverviewMap(map) end
local function resolve(pin)
    return A.TransportLinks and A.TransportLinks.ForPin(pin) or {}
end
local function line(parent,used,ax,ay,bx,by,color,width)
    if used>=(B.limit or 1024) then return used end
    used=used+1;local item=B.lines[used]
    if not item then item=parent:CreateLine(nil,'OVERLAY');B.lines[used]=item end
    item:SetDrawLayer('OVERLAY',width>2 and 1 or 0)
    item:SetThickness(width);item:SetColorTexture(unpack(color))
    item:SetStartPoint('TOPLEFT',parent,ax,ay);item:SetEndPoint('TOPLEFT',parent,bx,by);item:Show()
    return used
end
local function draw(row,map,used,hover,completed,network)
    local V=A.JourneyView;local canvas=A.map:GetCanvas();local width,height=canvas:GetWidth(),canvas:GetHeight()
    local color=hover and {.55,.88,1,1} or network and {.3,.65,.9,.22} or completed and {.38,.48,.52,.35} or {.3,.75,1,.85}
    local path
    if map~=947 and not row.geometryUnknown then path=row.kind=='flight' and A.Flights and A.Flights.Path(row) or row.path end
    if map==947 or (hover or network) and (row.geometryUnknown or not path or #path<2) then
        -- Schematic world connection, not a claim about an in-world teleport spline.
        local ax,ay=V.Project(row.board,map);local bx,by=V.Project(row.arrival,map)
        if not ax or not bx then return used end
        ax,ay,bx,by=ax*width,-ay*height,bx*width,-by*height
        local dx,dy=bx-ax,by-ay;local length=math.sqrt(dx*dx+dy*dy)
        if length<1 then return used end
        for at=0,length,14 do
            if used>=(B.limit or 1024) then break end
            local finish=math.min(length,at+9)
            used=line(B.overlay,used,ax+dx*at/length,ay+dy*at/length,ax+dx*finish/length,ay+dy*finish/length,color,hover and 3 or network and 1 or 2)
        end
    elseif hover or network then
        -- Continent previews retain the real same-piece sailing geometry.
        local previous;local stride=network and math.max(1,math.ceil(#path/12)) or 1
        for i=2,#path do
            previous=previous or path[i-1]
            local a,b=previous,path[i]
            if b.breakBefore then previous=b
            elseif i%stride==0 or i==#path or path[i+1].breakBefore then
                local ax,ay=V.Project(a,map);local bx,by=V.Project(b,map)
                if ax and bx then used=line(B.overlay,used,ax*width,-ay*height,bx*width,-by*height,color,hover and 3 or 1) end
                previous=b
            end
        end
    end
    return used
end
function B.Update(plan)
    for _,item in ipairs(B.lines) do item:Hide() end
    local map=A.map and A.map:GetMapID()
    if not A.map or not A.map:IsShown() or not overview(map) then B.hover=nil;B.focus=nil;return end
    if B.hover and B.hover.map~=map then B.hover=nil end
    if B.focus and B.focus.map~=map then B.focus=nil end
    local V=A.JourneyView;if not V then return end
    if not B.overlay then
        B.overlay=CreateFrame('Frame',nil,A.map:GetCanvas());B.overlay:SetAllPoints(A.map:GetCanvas())
        B.overlay:EnableMouse(false);B.overlay:SetClipsChildren(true)
    end
    B.overlay:SetFrameLevel(V.LayerLevel(A.map:GetCanvas()))
    plan=plan or V.DisplayPlan()
    local used=0
    B.limit=384
    if A.db and A.db.showTransportLinks then
        for i,row in ipairs(A.TransportLinks.Visible(map)) do
            if i>48 then break end
            used=draw(row,map,used,false,false,true)
        end
    end
    B.limit=768
    if map==947 and A.db and A.db.showJourneyRoute and plan then
        for i,leg in ipairs(plan.legs or {}) do
            if leg.transport and A.TransportLinks.methods[leg.transport.kind] then
                used=draw(leg.transport,map,used,false,A.Journey and A.Journey.active==plan and i<(A.Journey.legIndex or 1))
            end
        end
    end
    local rows=resolve(B.focus and B.focus.pin or B.hover)
    B.limit=1024
    for _,row in ipairs(rows) do if not B.focus or B.focus.id==row.id then used=draw(row,map,used,true,false) end end
end
function B.Hover(pin)
    if not A.map or not overview(A.map:GetMapID()) or #resolve(pin)==0 then return false end
    B.hover=pin;B.Update();return true
end
function B.Focus(pin,id)
    if not A.map or not overview(A.map:GetMapID()) then return false end
    for _,row in ipairs(resolve(pin)) do if row.id==id then B.focus={pin=pin,id=id,map=A.map:GetMapID()};B.Update();return true end end
    return false
end
function B.Clear(pin)
    if not pin then B.focus=nil end
    if not pin or B.hover==pin then B.hover=nil;B.Update() end
end
local driver=CreateFrame('Frame',nil,UIParent);driver:SetSize(1,1);driver:EnableMouse(false)
local elapsed=0
driver:SetScript('OnUpdate',function(_,dt)
    local active=A.Journey and A.Journey.active and A.Journey.active.hasTransports
    elapsed=elapsed+dt;if elapsed<((B.hover or B.focus or active) and .2 or 1) then return end;elapsed=0
    if B.hover or B.focus or active or A.db and A.db.showTransportLinks and A.map and A.map:IsShown() then B.Update() end
end)
