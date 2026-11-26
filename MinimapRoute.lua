-- Projection/clipping follows our Gatherly minimap route implementation.
local _,A=...
local R={lines={},directions={},fragments={}};A.MinimapRoute=R
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
function R.Update()
    local style=A.RouteStyle
    style.HideLines(R.lines);style.HideLines(R.fragments);style.Hide(R.directions)
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
    local segments={};local split=true
    local marks={minimap=true,spacing=35,limit=1,size=4.5,thickness=1.6,strokeWidth=2.5,anchor='CENTER',inside=function(x,y)
        return x*x+y*y>=144 and R.Clip(x,y,x,y,width,height,shape)~=nil
    end}
    local function append(x1,y1,x2,y2,kind,fromPlayer)
        x1,y1,x2,y2=R.Clip(x1,y1,x2,y2,width,height,shape)
        if not x1 then split=true;return end
        local pieces=arrowGap(x1,y1,x2,y2)
        if #pieces==0 then split=true end
        for j,piece in ipairs(pieces) do
            local slot=#segments+1
            if not R.lines[slot] then R.lines[slot]=R.overlay:CreateLine(nil,'OVERLAY') end
            piece.base=R.lines[slot];piece.kind=kind;piece.split=split or j>1
            piece.fromPlayer=fromPlayer and j==1
            segments[slot]=piece;split=false
        end
    end
    local progress=A.RouteProgress
    local active,fraction=progress.Split(plan,hbd,px,py,instance)
    local current=active or progress.Segment(plan)
    local x1,y1
    for j,point in ipairs(plan.points) do
        local wx,wy,wi=progress.World(point,hbd)
        local x2,y2
        if wi==instance then x2,y2=R.Project(wx,wy,px,py,radius,width,height,facing) end
        if x1 and x2 and not point.breakBefore then
            local i=j-1
            if i==active and fraction>0 then
                local x=x1+(x2-x1)*fraction;local y=y1+(y2-y1)*fraction
                append(x1,y1,x,y,'completed')
                if fraction<1 then append(x,y,x2,y2,'ahead',true) end
            else
                local kind=style.Kind(plan,i)
                local fromPlayer=i==current and kind=='ahead' and x1*x1+y1*y1<=64
                append(x1,y1,x2,y2,kind,fromPlayer)
            end
        else split=true end
        x1,y1=x2,y2
    end
    style.Render(segments,R.directions,R.fragments,R.overlay,marks)
end
local driver=CreateFrame('Frame',nil,UIParent)
driver:SetSize(1,1);driver:SetPoint('TOPLEFT',UIParent,'TOPLEFT',0,0);driver:EnableMouse(false)
local elapsed=0
driver:SetScript('OnUpdate',function(_,dt) elapsed=elapsed+dt;if elapsed>=.1 then elapsed=0;R.Update() end end)
driver:Show()
