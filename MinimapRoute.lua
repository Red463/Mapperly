-- Projection/clipping follows our Gatherly minimap route implementation.
local _,A=...
local R={lines={}};A.MinimapRoute=R
local function number(v) return not (issecretvalue and issecretvalue(v)) and type(v)=='number' and v==v and math.abs(v)<math.huge end
function R.Project(wx,wy,px,py,radius,width,height,facing)
    local east,north=px-wx,wy-py -- HBD's horizontal world axis increases west.
    local c,s=math.cos(facing),math.sin(facing)
    return (east*c+north*s)/radius*width/2,(-east*s+north*c)/radius*height/2
end
function R.Clip(x1,y1,x2,y2,width,height,shape)
    local rx,ry=width*.47,height*.47
    local dx,dy=x2-x1,y2-y1
    if shape=='SQUARE' then
        local lo,hi=0,1
        for _,edge in ipairs({{-dx,x1+rx},{dx,rx-x1},{-dy,y1+ry},{dy,ry-y1}}) do
            local p,q=edge[1],edge[2]
            if p==0 then if q<0 then return end
            elseif p<0 then lo=math.max(lo,q/p)
            else hi=math.min(hi,q/p) end
            if lo>hi then return end
        end
        return x1+dx*lo,y1+dy*lo,x1+dx*hi,y1+dy*hi
    end
    -- An inscribed ellipse is safe for round and unknown/hybrid minimap masks.
    local ax,ay=x1/rx,y1/ry;local vx,vy=dx/rx,dy/ry
    local aa=vx*vx+vy*vy
    if aa==0 then if ax*ax+ay*ay<=1 then return x1,y1,x2,y2 end;return end
    local bb=2*(ax*vx+ay*vy);local cc=ax*ax+ay*ay-1;local disc=bb*bb-4*aa*cc
    if disc<0 then return end
    local lo=math.max(0,(-bb-math.sqrt(disc))/(2*aa));local hi=math.min(1,(-bb+math.sqrt(disc))/(2*aa))
    if lo>hi then return end
    return x1+dx*lo,y1+dy*lo,x1+dx*hi,y1+dy*hi
end
local function arrowGap(x1,y1,x2,y2)
    local dx,dy=x2-x1,y2-y1;local length2=dx*dx+dy*dy
    if length2<.000001 then return {} end
    local mid=-(x1*dx+y1*dy)/length2
    local cross=x1*dy-y1*dx;local disc=64-cross*cross/length2
    if disc<=0 then return {{x1,y1,x2,y2}} end
    local span=math.sqrt(disc/length2);local lo,hi=math.max(0,mid-span),math.min(1,mid+span)
    if lo>=hi then return {{x1,y1,x2,y2}} end
    local pieces={}
    if lo>0 then pieces[#pieces+1]={x1,y1,x1+dx*lo,y1+dy*lo} end
    if hi<1 then pieces[#pieces+1]={x1+dx*hi,y1+dy*hi,x2,y2} end
    return pieces
end
local function world(p,hbd)
    if number(p.worldX) and number(p.worldY) and number(p.instance) then return p.worldX,p.worldY,p.instance end
    local ok,x,y,instance=pcall(hbd.GetWorldCoordinatesFromZone,hbd,p.x,p.y,p.mapID or p.map)
    if ok and number(x) and number(y) and number(instance) then return x,y,instance end
end
function R.Update()
    for _,line in ipairs(R.lines) do line:Hide() end
    if not A.db or not A.JourneyView then return end
    -- Direct-bearing map lines follow the player even with the map reopened.
    if A.Navigation and A.Navigation.target and not (A.Journey and A.Journey.active) and A.map and A.map:IsShown() then A.JourneyView.Refresh() end
    if not A.db.showMinimapRoute or not Minimap or not Minimap:IsShown() then return end
    local plan=A.JourneyView.DisplayPlan()
    if not plan or #plan.points>2049 then return end
    local hbd=LibStub and LibStub('HereBeDragons-2.0',true)
    if not hbd or not hbd.GetPlayerWorldPosition or not C_Minimap or not C_Minimap.GetViewRadius then return end
    local ok,px,py,instance=pcall(hbd.GetPlayerWorldPosition,hbd)
    local good,radius=pcall(C_Minimap.GetViewRadius)
    if not ok or not number(px) or not number(py) or not number(instance) or not good or not number(radius) or radius<=0 then return end
    local width,height=Minimap:GetWidth(),Minimap:GetHeight()
    if not number(width) or not number(height) or width<=0 or height<=0 then return end
    local facing=0
    local readable,rotating=pcall(function() return GetCVar and GetCVar('rotateMinimap') end)
    if not readable or issecretvalue and issecretvalue(rotating) then return end
    local ignore=false
    if C_Minimap.IsRotateMinimapIgnored then
        local valid,result=pcall(C_Minimap.IsRotateMinimapIgnored)
        if not valid or issecretvalue and issecretvalue(result) then return end
        ignore=result==true
    end
    if rotating=='1' and not ignore then
        local valid,result=pcall(function() return GetPlayerFacing and GetPlayerFacing() end)
        if not valid or not number(result) then return end
        facing=result
    end
    local shape='ROUND'
    if GetMinimapShape then local valid,result=pcall(GetMinimapShape);if valid and type(result)=='string' then shape=result end end
    if not R.overlay then
        R.overlay=CreateFrame('Frame',nil,Minimap);R.overlay:SetAllPoints(Minimap);R.overlay:EnableMouse(false)
        R.overlay:SetClipsChildren(true)
    end
    if R.overlay:GetParent()~=Minimap then R.overlay:SetParent(Minimap);R.overlay:SetAllPoints(Minimap) end
    R.overlay:SetFrameLevel(Minimap:GetFrameLevel()+2)
    local used=0
    for i=1,#plan.points-1 do
        local ax,ay,ai=world(plan.points[i],hbd);local bx,by,bi=world(plan.points[i+1],hbd)
        if ai==instance and bi==instance then
            local x1,y1=R.Project(ax,ay,px,py,radius,width,height,facing)
            local x2,y2=R.Project(bx,by,px,py,radius,width,height,facing)
            x1,y1,x2,y2=R.Clip(x1,y1,x2,y2,width,height,shape)
            if x1 then
                for _,piece in ipairs(arrowGap(x1,y1,x2,y2)) do
                    used=used+1
                    local line=R.lines[used]
                    if not line then line=R.overlay:CreateLine(nil,'OVERLAY');R.lines[used]=line;line:SetThickness(1.5);line:SetColorTexture(1,.77,.18,.85) end
                    line:SetStartPoint('CENTER',R.overlay,piece[1],piece[2]);line:SetEndPoint('CENTER',R.overlay,piece[3],piece[4]);line:Show()
                end
            end
        end
    end
end
local driver=CreateFrame('Frame',nil,UIParent)
driver:SetSize(1,1);driver:SetPoint('TOPLEFT',UIParent,'TOPLEFT',0,0);driver:EnableMouse(false)
local elapsed=0
driver:SetScript('OnUpdate',function(_,dt) elapsed=elapsed+dt;if elapsed>=.1 then elapsed=0;R.Update() end end)
driver:Show()
