local _,A=...
local N={};A.Navigation=N
local tau=2*math.pi
local function number(v)
    if issecretvalue and issecretvalue(v) then return false end
    return type(v)=='number' and v==v and v~=math.huge and v~=-math.huge
end
local function normalize(a) return (a+math.pi)%tau-math.pi end
function N.Bearing(dx,dy)
    if math.atan2 then return math.atan2(dx,dy) end
    if dy==0 then return dx>=0 and math.pi/2 or -math.pi/2 end
    return math.atan(dx/dy)+(dy<0 and (dx>=0 and math.pi or -math.pi) or 0)
end
function N.SmoothAngle(current,target,elapsed)
    if not number(target) then return current end
    if not number(current) then return normalize(target) end
    if not number(elapsed) or elapsed<=0 then return current end
    return normalize(current+normalize(target-current)*(1-math.exp(-18*elapsed)))
end
function N.Parse(x,y)
    x,y=tonumber(x),tonumber(y)
    if not number(x) or not number(y) or x<0 or x>100 or y<0 or y>100 then return nil,'Enter X and Y coordinates between 0 and 100.' end
    return x/100,y/100
end
local function library() return LibStub and LibStub('HereBeDragons-2.0',true) end
local function refresh()
    if A.map and A.RefreshPins then A.RefreshPins() end
    if A.UpdateButtonStates then A.UpdateButtonStates() end
end
local function facing()
    if not GetPlayerFacing then return end
    local ok,v=pcall(GetPlayerFacing)
    if ok and number(v) then return v end
end
local function rotate(f,angle)
    f.renderAngle=angle;f.icon:SetRotation(angle);f.shadow:SetRotation(angle)
end
local function waiting(reason)
    local f=N.frame
    f.bearing=nil;f.renderAngle=nil;f.icon:Hide();f.shadow:Hide()
    f.label:SetFontObject('GameFontNormal');f.label:SetText(reason);f:Show()
end
function N.Build()
    if N.frame then return end
    local f=CreateFrame('Frame','MapperlyNavigationArrow',UIParent);N.frame=f
    f:SetSize(200,108);f:SetPoint('CENTER',UIParent,'CENTER',180,140)
    f:SetFrameStrata('LOW');f:SetMovable(true);f:SetClampedToScreen(true);f:EnableMouse(true);f:RegisterForDrag('LeftButton')
    local anchor=A.db.navigationAnchor
    if anchor then f:ClearAllPoints();f:SetPoint(anchor.point,UIParent,anchor.relativePoint,anchor.x,anchor.y) end
    f:SetScript('OnMouseDown',function(self,button) if button=='LeftButton' then self.wasDragged=false end end)
    f:SetScript('OnDragStart',function(self) self.wasDragged=true;self:StartMoving() end)
    f:SetScript('OnDragStop',function(self)
        self:StopMovingOrSizing()
        local point,_,relativePoint,x,y=self:GetPoint()
        if number(x) and number(y) then A.db.navigationAnchor={point=point,relativePoint=relativePoint,x=x,y=y} end
    end)
    f:SetScript('OnMouseUp',function(self,button)
        if button=='RightButton' then N.Stop()
        elseif button=='LeftButton' and not self.wasDragged and A.ShowNavigationInput then A.ShowNavigationInput(N.target and N.target.map) end
    end)
    f.shadow=f:CreateTexture(nil,'ARTWORK',nil,0);f.shadow:SetTexture('Interface\\AddOns\\Mapperly\\Media\\GuideArrow');f.shadow:SetSize(48,48);f.shadow:SetVertexColor(0,0,0,.7)
    f.icon=f:CreateTexture(nil,'ARTWORK',nil,1);f.icon:SetTexture('Interface\\AddOns\\Mapperly\\Media\\GuideArrow');f.icon:SetSize(48,48);f.icon:SetPoint('TOP',f,'TOP',0,0)
    f.shadow:SetPoint('CENTER',f.icon,'CENTER',2,-2)
    f.label=f:CreateFontString(nil,'OVERLAY','GameFontNormalLarge');f.label:SetPoint('TOP',f,'TOP',0,-54);f.label:SetWidth(200);f.label:SetJustifyH('CENTER')
    f.destination=f:CreateFontString(nil,'OVERLAY','GameFontHighlightSmall');f.destination:SetPoint('TOP',f,'TOP',0,-78);f.destination:SetWidth(200);f.destination:SetWordWrap(false);f.destination:SetJustifyH('CENTER')
    f:SetScript('OnEnter',function(self)
        GameTooltip:SetOwner(self,'ANCHOR_RIGHT');GameTooltip:SetText('Mapperly navigation')
        if N.target then GameTooltip:AddLine(string.format('%s: %.4f, %.4f',N.target.zone,N.target.x*100,N.target.y*100),1,.82,0,true) end
        GameTooltip:AddLine('Straight-line direction; terrain and travel routes are not calculated.',1,1,1,true)
        GameTooltip:AddLine('Drag to move. Left-click to edit. Right-click to stop.',1,.82,0,true);GameTooltip:Show()
    end)
    f:SetScript('OnLeave',function() GameTooltip:Hide() end)
    f:SetScript('OnHide',function(self) self.bearing=nil;self.renderAngle=nil end)
    local elapsed=0
    f:SetScript('OnUpdate',function(_,dt)
        elapsed=elapsed+dt
        if elapsed>=.1 then elapsed=0;N.Tick() end
        N.Animate(dt)
    end)
    f:Hide()
end
function N.Start(map,x,y,name)
    local nx,ny=N.Parse(x,y)
    if nx==nil then return nil,ny end
    map=tonumber(map)
    if not number(map) or map<1 or map%1~=0 then return nil,'Choose a map before entering coordinates.' end
    local hbd=library()
    if not hbd or type(hbd.GetWorldCoordinatesFromZone)~='function' then return nil,'Map coordinates are not available yet. Try again shortly.' end
    local ok,wx,wy,instance=pcall(hbd.GetWorldCoordinatesFromZone,hbd,nx,ny,map)
    if not ok or not number(wx) or not number(wy) or not number(instance) then return nil,'This map cannot be used for navigation. Open a zone or continent map.' end
    local info=C_Map.GetMapInfo and C_Map.GetMapInfo(map)
    local zone=info and info.name or 'Map '..map
    name=type(name)=='string' and name:sub(1,120) or zone
    if name:match('^%s*$') then name=zone end
    N.target={map=map,x=nx,y=ny,worldX=wx,worldY=wy,instance=instance,category='navigation',name=name,zone=zone}
    if A.Destinations then A.Destinations.Remember(N.target) end
    N.Build()
    N.frame.bearing=nil;N.frame.renderAngle=nil
    N.frame.destination:SetText(string.format('%s (%.1f, %.1f)',name,nx*100,ny*100))
    N.Tick();refresh();return true
end
function N.ToPin(pin)
    if not A.ValidPin(pin) then return nil,'This marker has no usable map coordinates.' end
    local ok,reason=N.Start(pin.map,pin.x*100,pin.y*100,pin.name)
    if not ok and A.Print then A.Print(reason) end
    return ok,reason
end
function N.Stop(arrived)
    N.target=nil
    if N.frame then N.frame:Hide() end
    GameTooltip:Hide();refresh()
    if arrived and A.Print then A.Print('Arrived at your navigation destination.') end
end
function N.Tick()
    local target=N.target
    if not target then if N.frame then N.frame:Hide() end;return end
    local hbd=library()
    if not hbd or type(hbd.GetPlayerWorldPosition)~='function' then waiting('Position unavailable');return end
    local ok,px,py,instance=pcall(hbd.GetPlayerWorldPosition,hbd)
    if not ok or not number(px) or not number(py) or not number(instance) then waiting('Position unavailable');return end
    if instance~=target.instance then waiting('Different continent / instance');return end
    local dx,dy=target.worldX-px,target.worldY-py
    local distance=math.sqrt(dx*dx+dy*dy)
    if not number(distance) then waiting('Position unavailable');return end
    if distance<=10 then N.Stop(true);return end
    local heading=facing()
    if heading==nil then waiting('Direction unavailable');return end
    local f=N.frame
    f.bearing=N.Bearing(dx,dy)
    f.label:SetFontObject('GameFontNormalLarge')
    f.label:SetText(string.format('%d yd',math.floor(distance+.5)))
    if f.renderAngle==nil then rotate(f,normalize(f.bearing-heading)) end
    f.icon:Show();f.shadow:Show();f:Show()
end
function N.Animate(elapsed)
    local f=N.frame
    if not f or not f:IsShown() or not number(f.bearing) then return end
    local heading=facing()
    if heading==nil then waiting('Direction unavailable');return end
    rotate(f,N.SmoothAngle(f.renderAngle,f.bearing-heading,elapsed))
end
function N.PinForMap(map)
    local target=N.target
    if not target then return end
    local x,y
    if map==target.map then x,y=target.x,target.y
    else
        local hbd=library()
        if not hbd or type(hbd.GetZoneCoordinatesFromWorldInstance)~='function' then return end
        local ok,px,py=pcall(hbd.GetZoneCoordinatesFromWorldInstance,hbd,target.worldX,target.worldY,target.instance,map)
        if ok then x,y=px,py end
    end
    if not number(x) or not number(y) or x<0 or x>1 or y<0 or y>1 then return end
    return {map=map,x=x,y=y,name=target.name,category='navigation'}
end
