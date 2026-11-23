local _,A=...
local R={rows={}};A.RouteSteps=R
local function label(text) return type(text)=='string' and text or '' end
function R.Describe(leg)
    local t=leg and leg.transport
    if t and t.automaticTram then return 'Ride the tram and exit the '..label(t.toName)..' portal','note_travel','tram' end
    if t then
        local destination=label(t.toName):match('^%s*([^,]+)') or 'the destination'
        local methods={flight='Fly',boat='Boat',zeppelin='Zeppelin',airship='Airship',tram='Tram',lift='Lift'}
        local method=methods[t.kind]
        local icon=t.kind=='flight' and 'flight' or (t.kind=='tram' or t.kind=='lift') and 'note_travel' or method and 'transport' or 'note_travel'
        return (method or 'Travel')..' to '..destination,icon,t.kind
    end
    return label(leg and leg.name),'note_travel'
end
local function fit(t,text,width)
    t:SetWidth(width);t:SetHeight(10000);t:SetText(text)
    local measured=t.GetStringHeight and t:GetStringHeight()
    local height=type(measured)=='number' and measured>0 and measured<1000 and measured or math.max(14,math.ceil(#text/38)*14)
    t:SetHeight(height);return height
end
function R.Build()
    if R.window then return end
    local U=A.Dialogs
    local f=U.CompactWindow(UIParent,312,220);R.window=f
    f:ClearAllPoints();f:SetPoint('TOPRIGHT',UIParent,'TOPRIGHT',-320,-240)
    f:SetFrameStrata('DIALOG');f:SetClampedToScreen(true);f:SetMovable(true);f:EnableMouse(true);f:RegisterForDrag('LeftButton')
    local anchor=A.db.routeStepsAnchor
    if anchor then f:ClearAllPoints();f:SetPoint(anchor.point,UIParent,anchor.relativePoint,anchor.x,anchor.y) end
    f:SetScript('OnDragStart',function() f:StartMoving() end)
    f:SetScript('OnDragStop',function()
        f:StopMovingOrSizing()
        local point,_,relativePoint,x,y=f:GetPoint()
        A.db.routeStepsAnchor=A.ValidateRouteStepsAnchor({point=point,relativePoint=relativePoint,x=x,y=y})
    end)
    R.heading=U.Label(f,'Route steps',16,6,'GameFontNormal');R.heading:SetWidth(218)
    R.collapse=CreateFrame('Button',nil,f);R.collapse:SetSize(20,20);R.collapse:SetPoint('TOPLEFT',f,'TOPLEFT',246,-2)
    R.collapse:SetScript('OnClick',function()
        A.db.routeStepsCollapsed=not A.db.routeStepsCollapsed;R.Refresh()
    end)
    function R.collapse:UpdateVisual()
        local icon=A.db.routeStepsCollapsed and 'Plus' or 'Minus'
        self:SetNormalTexture('Interface\\Buttons\\UI-'..icon..'Button-Up')
        self:SetPushedTexture('Interface\\Buttons\\UI-'..icon..'Button-Down')
        self:SetHighlightTexture('Interface\\Buttons\\UI-PlusButton-Hilight')
    end
    R.close=CreateFrame('Button',nil,f,'UIPanelCloseButton');R.close:SetSize(24,24);R.close:SetPoint('TOPRIGHT',f,'TOPRIGHT',-2,0)
    R.close:SetScript('OnClick',function()
        R.dismissedTarget=A.Navigation and (A.Navigation.target or A.Navigation.pending)
        f:Hide()
    end)
    R.destination=U.Label(f,'',14,38,'GameFontHighlightSmall');R.destination:SetWordWrap(true)
    R.status=U.Label(f,'',14,58,'GameFontDisableSmall');R.status:SetWordWrap(true)
    R.current=U.Label(f,'',14,80,'GameFontNormal');R.current:SetWordWrap(true)
    R.upcoming=U.Label(f,'Up next',14,110,'GameFontDisableSmall')
    for i=1,10 do
        local frame=CreateFrame('Frame',nil,f);frame:SetSize(272,28);frame:EnableMouse(true);frame:RegisterForDrag('LeftButton')
        local row=U.Label(frame,'',36,6,'GameFontHighlightSmall');R.rows[i]=row;row.frame=frame;row:SetWordWrap(true);row:SetJustifyH('LEFT')
        row.icon=frame:CreateTexture(nil,'ARTWORK');row.icon:SetSize(18,18);row.icon:SetPoint('LEFT',frame,'LEFT',6,0)
        row.highlight=frame:CreateTexture(nil,'BACKGROUND',nil,1);row.highlight:SetAllPoints(frame)
        row.highlight:SetColorTexture(.64,.43,.12,.22);row.highlight:Hide()
        frame:SetScript('OnEnter',function(self)
            GameTooltip:SetOwner(self,'ANCHOR_RIGHT');GameTooltip:SetText(self.stepTitle or 'Route step')
            if self.details and self.details~='' and self.details~=self.stepTitle then GameTooltip:AddLine(self.details,1,.82,0,true) end
            GameTooltip:Show()
        end)
        frame:SetScript('OnLeave',function() GameTooltip:Hide() end)
        frame:SetScript('OnHide',function(self) if GameTooltip:IsOwned(self) then GameTooltip:Hide() end end)
        frame:SetScript('OnDragStart',function() GameTooltip:Hide();f:GetScript('OnDragStart')(f) end)
        frame:SetScript('OnDragStop',function() f:GetScript('OnDragStop')(f) end)
    end
    for _,text in ipairs({R.heading,R.destination,R.status,R.current,R.upcoming}) do text:SetJustifyH('LEFT') end
end
function R.SetShown(shown)
    A.db.showRouteSteps=not not shown
    R.dismissedTarget=nil;R.signature=nil
    if A.NavigationSettings then A.NavigationSettings.Sync() end
    R.Refresh()
end
function R.Refresh()
    local N,J=A.Navigation,A.Journey
    local target=N and N.target;local pending=N and N.pending
    if not target and not pending then R.dismissedTarget=nil end
    if not A.db or not A.db.showRouteSteps or not target and not pending then if R.window then R.window:Hide() end;return end
    if R.dismissedTarget== (target or pending) then if R.window then R.window:Hide() end;return end
    R.Build()
    local f=R.window;local plan=J and J.active
    local at=plan and (J.legIndex or 1) or 1;local leg=plan and plan.legs and plan.legs[at]
    local destination=label((target or pending).name)
    local status=J and J.paused and 'Paused' or pending and (target and 'Updating route...' or 'Planning route...') or N.deferredRoutingTarget and 'New route queued until landing' or ''
    local instruction=plan and label(leg and leg.name) or target and 'Straight-line guidance to the destination' or 'Planning route...'
    if plan and instruction=='' then instruction='Follow the route to the destination' end
    if leg and leg.kind=='transport' and J.transportMessage then instruction=J.transportMessage end
    if J and J.crossing then instruction='Continue through the zone crossing' end
    if J and J.inStructure then instruction='Follow the passage to the next zone' end
    local collapsed=A.db.routeStepsCollapsed
    local signature=table.concat({destination,status,instruction,tostring(plan),tostring(at),tostring(collapsed)},'\001')
    local screenWidth,screenHeight=UIParent:GetWidth(),UIParent:GetHeight()
    signature=signature..':'..screenWidth..':'..screenHeight..':'..tostring(A.db.theme)..':'..tostring(A.Theme and A.Theme.revision)
    if signature==R.signature then f:Show();return end
    R.signature=signature
    local y=collapsed and 38 or 44
    R.destination:ClearAllPoints();R.destination:SetPoint('TOPLEFT',f,'TOPLEFT',20,-y)
    local destinationHeight=fit(R.destination,destination,272)
    R.destination:SetShown(not collapsed)
    if not collapsed then y=y+destinationHeight+12 end
    R.status:ClearAllPoints();R.status:SetPoint('TOPLEFT',f,'TOPLEFT',20,-y)
    local statusHeight=fit(R.status,status,272)
    R.status:SetShown(not collapsed and status~='')
    if not collapsed and status~='' then y=y+statusHeight+16 end
    R.collapse:UpdateVisual()
    R.current:SetShown(not plan);R.upcoming:Hide()
    for _,row in ipairs(R.rows) do row:Hide();row.frame:Hide();row.highlight:Hide() end
    do
        R.current:ClearAllPoints();R.current:SetPoint('TOPLEFT',f,'TOPLEFT',20,-y)
        local currentHeight=fit(R.current,'Now: '..instruction,272)
        if not plan then y=y+currentHeight+12 end
        local count=plan and plan.legs and (collapsed and 1 or math.min(10,#plan.legs)) or 0
        if count>0 then
            local first=collapsed and at or math.max(1,math.min(at-4,#plan.legs-9))
            for i=1,count do
                local index=first+i-1
                local row=R.rows[i];row.frame:ClearAllPoints();row.frame:SetPoint('TOPLEFT',f,'TOPLEFT',20,-y)
                local current=index==at;local step=plan.legs[index];local text,category,kind=R.Describe(step)
                if collapsed and J.paused then text='Paused: '..text end
                local height=math.max(28,fit(row,index..'. '..text,236)+12)
                row.frame:SetHeight(height);y=y+height+8
                row.frame.stepTitle=text
                row.frame.details=current and instruction or label(step.name)
                A.SetPinTexture(row.icon,category,kind,18);row.icon:SetAlpha(current and 1 or index<at and .4 or .85)
                if current then row:SetTextColor(1,.82,.35,1)
                elseif index<at then row:SetTextColor(.5,.48,.42,1)
                else row:SetTextColor(.86,.82,.72,1) end
                row.highlight:SetShown(current);row.frame:Show();row:Show()
            end
        end
    end
    f:SetHeight(y+18);f:SetScale(math.max(.1,math.min(1,(screenWidth-24)/312,(screenHeight-24)/(y+18))));f:Show()
end
R.driver=CreateFrame('Frame',nil,UIParent);R.driver:SetSize(1,1);R.driver:SetPoint('TOPLEFT',UIParent,'TOPLEFT',0,0);R.driver:EnableMouse(false);R.driver:Show()
local elapsed=0
R.driver:SetScript('OnUpdate',function(_,dt)
    elapsed=elapsed+dt;if elapsed<.2 then return end;elapsed=0;R.Refresh()
end)
