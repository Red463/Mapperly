local _,A=...
local V={lines={},directions={},fragments={}};A.JourneyView=V
local function finite(v) return not (issecretvalue and issecretvalue(v)) and type(v)=='number' and v==v and math.abs(v)<math.huge end
function V.Project(p,map)
    if p.mapID==map and finite(p.x) and finite(p.y) then return p.x,p.y end
    local hbd=LibStub and LibStub('HereBeDragons-2.0',true)
    if not hbd then return end
    local ok,wx,wy,instance=true,p.worldX,p.worldY,p.instance
    if not finite(wx) or not finite(wy) or not finite(instance) then ok,wx,wy,instance=pcall(hbd.GetWorldCoordinatesFromZone,hbd,p.x,p.y,p.mapID) end
    if not ok or not finite(wx) or not finite(wy) or not finite(instance) then return end
    local good,x,y=pcall(hbd.GetZoneCoordinatesFromWorldInstance,hbd,wx,wy,instance,map,true)
    if good and finite(x) and finite(y) then return x,y end
end
function V.DisplayPlan()
    if V.window and V.window:IsShown() and V.followDirect then
        local target=A.Navigation.target
        if not target or A.Journey.active then
            V.window:Hide();V.followDirect=false;V.plan=nil
        else
            local plan,reason=A.Journey.DirectPlan(target)
            if not plan then V.steps:SetText(reason or 'Position unavailable.');return end
            V.plan=plan;V.candidate=target;V.WriteSummary()
        end
    end
    if V.window and V.window:IsShown() and V.plan then return V.plan end
    if A.Journey and A.Journey.active then return A.Journey.active end
    if A.Journey and A.Navigation and A.Navigation.target then return A.Journey.DirectPlan(A.Navigation.target) end
end
function V.LayerLevel(canvas)
    local level=canvas:GetFrameLevel()+10
    if A.map.GetPinFrameLevelsManager then
        local ok,manager=pcall(A.map.GetPinFrameLevelsManager,A.map)
        if ok and (type(manager)=='table' or type(manager)=='userdata') and type(manager.GetFrameLevelStart)=='function' then
            -- Exploration/highlight art is drawn by pins above the tile canvas.
            -- Use the top of those art tiers, as Gatherly's route layer does.
            for _,kind in ipairs({'PIN_FRAME_LEVEL_DEFAULT','PIN_FRAME_LEVEL_MAP_EXPLORATION','PIN_FRAME_LEVEL_MAP_HIGHLIGHT'}) do
                local good,base=pcall(manager.GetFrameLevelStart,manager,kind)
                if good and finite(base) then
                    local range=1
                    if type(manager.GetFrameLevelRange)=='function' then
                        local valid,n=pcall(manager.GetFrameLevelRange,manager,kind)
                        if valid and finite(n) and n>=1 then range=n end
                    end
                    level=math.max(level,base+range)
                end
            end
        end
    end
    local api=OpenMapAPI
    if type(api)=='table' and api.major==1 and type(api.IsStitched)=='function' and type(api.ArtTopLevel)=='function' then
        local ok,stitched=pcall(api.IsStitched)
        if ok and stitched then
            local good,top=pcall(api.ArtTopLevel)
            if good and finite(top) then level=math.max(level,top+1) end
        end
    end
    return level
end
function V.Refresh()
    for _,line in pairs(V.lines) do line:Hide() end
    for _,line in ipairs(V.fragments) do line:Hide() end
    if A.RouteStyle then A.RouteStyle.Hide(V.directions) end
    if V.window and V.window:IsShown() and V.followActive then
        local active=A.Journey and A.Journey.active
        if not active then V.window:Hide()
        elseif active~=V.plan then
            V.plan=active;V.candidate=A.Navigation.target;V.WriteSummary()
        elseif V.legIndex~=A.Journey.legIndex then V.WriteSummary()
        end
    end
    local plan=V.DisplayPlan()
    V.progressKey=A.RouteStyle and A.RouteStyle.Key(plan)
    if A.BoatLinks then A.BoatLinks.Update(plan) end
    if not plan or not A.map or not A.db.showJourneyRoute then return end
    if #plan.points>2049 then return end -- Never replace omitted bends with unsafe shortcuts.
    local canvas=A.map:GetCanvas()
    if not V.overlay then
        V.overlay=CreateFrame('Frame',nil,canvas);V.overlay:SetAllPoints(canvas)
        V.overlay:EnableMouse(false);V.overlay:SetClipsChildren(true)
    end
    V.overlay:SetFrameLevel(V.LayerLevel(canvas))
    local map=A.map:GetMapID();local width,height=canvas:GetWidth(),canvas:GetHeight()
    local segments={};local split=true
    local marks={spacing=110,limit=24,size=8,thickness=2.5,strokeWidth=2,anchor='TOPLEFT',inside=function(x,y) return x>=5 and x<=width-5 and y<=-5 and y>=-height+5 end}
    for i=1,#plan.points-1 do
        local ax,ay=V.Project(plan.points[i],map);local bx,by=V.Project(plan.points[i+1],map)
        if ax and bx and not plan.points[i+1].breakBefore then
            local line=V.lines[i]
            if not line then line=V.overlay:CreateLine(nil,'OVERLAY');line:SetThickness(2);V.lines[i]=line end
            if A.RouteStyle then line:SetColorTexture(A.RouteStyle.Color(plan,i))
            elseif plan.points[i].transport or plan.points[i+1].transport then line:SetColorTexture(.3,.75,1,.9) else line:SetColorTexture(1,.77,.18,.9) end
            line:SetStartPoint('TOPLEFT',V.overlay,ax*width,-ay*height)
            line:SetEndPoint('TOPLEFT',V.overlay,bx*width,-by*height);line:Show()
            if A.RouteStyle then
                segments[#segments+1]={ax*width,-ay*height,bx*width,-by*height,base=line,color={A.RouteStyle.Color(plan,i)},markable=not A.RouteStyle.Completed(plan,i),split=split}
            end
            split=false
        else split=true
        end
    end
    if A.RouteStyle then A.RouteStyle.Render(segments,V.directions,V.fragments,V.overlay,marks) end
end
local progressDriver=CreateFrame('Frame',nil,UIParent);V.progressDriver=progressDriver;progressDriver:SetSize(1,1);progressDriver:EnableMouse(false)
local progressElapsed=0
progressDriver:SetScript('OnUpdate',function(_,dt)
    progressElapsed=progressElapsed+dt;if progressElapsed<.2 then return end;progressElapsed=0
    if A.RouteStyle and A.Journey and A.Journey.active and A.map and A.map:IsShown() then
        local displayed=V.window and V.window:IsShown() and V.plan or A.Journey.active
        if V.progressKey~=A.RouteStyle.Key(displayed) then V.Refresh() end
    end
end)
function V.Show(plan,candidate)
    V.plan=plan;V.candidate=candidate;V.followActive=A.Journey and A.Journey.active==plan;V.followDirect=false
    local U=A.Dialogs
    if not V.window then
        local f=U.Window('MapperlyJourneyPreview','Journey preview','Review the route before starting, or manage your active journey.',640,524);V.window=f
        local summary=U.Card(f,24,104,592,124)
        V.summary=U.Label(summary,'',16,14,'GameFontNormal');V.summary:SetSize(558,94);V.summary:SetWordWrap(true)
        local steps=U.Card(f,24,242,592,124)
        V.stepScroll=CreateFrame('ScrollFrame',nil,steps,'UIPanelScrollFrameTemplate')
        V.stepScroll:SetPoint('TOPLEFT',steps,'TOPLEFT',12,-12);V.stepScroll:SetSize(540,98)
        local child=CreateFrame('Frame',nil,V.stepScroll);child:SetSize(540,98);V.stepScroll:SetScrollChild(child)
        V.steps=U.Label(child,'',4,2);V.steps:SetSize(528,98);V.steps:SetWordWrap(true)
        local warning=U.Label(f,'Terrain estimate: check obstacles in game. Swimming is currently allowed. Start replans from your current position.',28,380,'GameFontDisableSmall')
        warning:SetSize(580,42);warning:SetWordWrap(true);V.warning=warning
        V.start=U.Action(f,'Start',24,440,100,function()
            if not V.candidate or not V.plan then return end
            local p=V.candidate
            local mode=V.plan.kind=='walking' and 'terrain' or 'direct'
            if p.questID and A.QuestNavigation then
                local current,why=A.QuestNavigation.RouteTarget(p,mode)
                if not current then V.steps:SetText(why);return end
                p=current
            end
            if p.serviceKey and A.NearestServices then
                local current,why=A.NearestServices.Resolve(p)
                if not current then V.steps:SetText(why);return end
                p=current
            end
            local ok,reason=A.Navigation.Start(p.map or p.mapID,p.x*100,p.y*100,p.name,{mode=mode,walkingOnly=p.walkingOnly})
            if ok then
                if p.approachDistance and A.Print then A.Print(string.format('Routing to a walkable approach, %.0f yd from %s. The final approach is manual.',p.approachDistance,p.label or p.name)) end
                if p.catalog and p.availabilityStatus=='unknown' and A.Print then A.Print('Quest availability is unconfirmed. Routing to the recorded starter; check pickup requirements in-game.') end
                f:Hide()
            else V.steps:SetText(reason or 'Unable to start route.') end
        end);A.Theme.ButtonRole(V.start,'primary')
        V.pause=U.Action(f,'Pause',134,440,100,function() A.Navigation.Pause() end)
        V.resume=U.Action(f,'Resume',244,440,100,function() A.Navigation.Resume() end)
        V.skip=U.Action(f,'Skip bend',354,440,110,function() A.Navigation.Skip() end)
        U.Action(f,'Replan',474,440,110,function() A.Navigation.Replan() end)
        U.Action(f,'Stop',24,484,112,function() A.Navigation.Stop();f:Hide() end)
        U.Action(f,'Close',504,484,112,function() f:Hide() end)
        f:HookScript('OnHide',V.Refresh)
    end
    V.WriteSummary()
    U.Show(V.window);V.Refresh()
end
function V.WriteSummary()
    local plan=V.plan
    if plan.kind=='direct' then
        V.summary:SetText(string.format('%s\nStraight-line distance: %d yd\nSmart routing is off; terrain is not checked.',plan.name or 'Destination',math.floor(plan.distance+.5)))
        V.warning:SetText('Straight-line guidance does not avoid obstacles. Start uses your current position.')
    else
        V.summary:SetText(string.format('%s\nWalking distance: %d yd || About %d min %s\nTerrain coverage: %s',plan.name or 'Destination',math.floor(plan.distance+.5),math.max(1,math.ceil(plan.estimatedSeconds/60)),plan.hasTransports and 'including transport' or 'on foot',plan.coverage or 'unknown'))
        local policy=plan.swimmingFallback and 'No dry route was found; swimming is permitted on this route.' or A.db.avoidSwimming and 'Dry routes are preferred; swimming remains available if needed.' or 'Swimming is allowed.'
        if plan.hasCityGuidance then policy='Indoor city access uses direction markers; follow the walkways. '..policy end
        if plan.hasPortalGuidance then policy='City tram access uses portal bearings; follow the streets to the marker. '..policy end
        V.warning:SetText(plan.hasTransports and 'Transport estimate includes waiting. Manual boarding and disembarking are required. '..policy or 'Terrain estimate: check obstacles in game. '..policy..' Start replans from your current position.')
    end
    local text={}
    for i,leg in ipairs(plan.legs or {}) do
        local row=leg.transport
        local cost=row and row.kind=='flight' and (' ('..A.Flights.Fare(row.fare,row.fareEstimated)..')') or ''
        text[#text+1]=i..'. '..leg.name..cost
    end
    if plan.flightCost then text[#text+1]='Flight total: '..A.Flights.Fare(plan.flightCost,plan.flightCostEstimated)..(plan.flightCostUnknown and ' + unquoted flights' or '') end
    V.steps:SetText(table.concat(text,'\n'))
    if V.stepScroll then
        V.steps:SetHeight(10000)
        local measured=V.steps.GetStringHeight and V.steps:GetStringHeight() or 0
        local height=math.max(98,#text*18,finite(measured) and measured+4 or 0)
        V.steps:SetHeight(height);V.stepScroll:GetScrollChild():SetHeight(height+4);V.stepScroll:SetVerticalScroll(0)
    end
    local active=A.Journey and A.Journey.active==plan
    local transit=active and A.Journey.Leg() and A.Journey.Leg().kind=='transport'
    V.skip:SetText(transit and 'Continue on foot' or 'Skip bend')
    V.legIndex=active and A.Journey.legIndex or nil
    V.pause:SetEnabled(active);V.resume:SetEnabled(active);V.skip:SetEnabled(active)
end
function V.OpenCurrent()
    if A.Journey and A.Journey.active and A.Navigation.target then V.Show(A.Journey.active,A.Navigation.target)
    elseif A.Navigation.target then
        local plan,reason=A.Journey.DirectPlan(A.Navigation.target)
        if plan then V.Show(plan,A.Navigation.target);V.followDirect=true;V.Refresh() else A.Print(reason) end
    else A.Print('Start or preview a journey first.') end
end
function V.CancelPreview()
    if V.window then V.window:Hide() end
    V.plan=nil;V.candidate=nil;V.followActive=false;V.followDirect=false
    if A.navigationWindow then A.navigationWindow.status:SetText('Routing preference changed.') end
end
function V.Preview(candidate)
    if A.db.navigationMode=='direct' then
        local plan,reason=A.Journey.DirectPlan(candidate)
        if not plan then return nil,reason end
        V.Show(plan,candidate)
        if A.navigationWindow then A.navigationWindow.status:SetText('Straight-line preview ready.') end
        return true
    end
    if A.PlanningJob.IsRunning() then return nil,'A route is already being planned. Wait or stop it first.' end
    local statusID
    local accepted,reason=A.Journey.Request(candidate,function(plan)
        V.Show(plan,candidate)
        if statusID and A.PlanningStatus then A.PlanningStatus.Ready(statusID,candidate,plan) end
        if A.navigationWindow then A.navigationWindow.status:SetText('Walking preview ready.') end
    end,function(reason)
        A.Print(reason)
        if statusID and A.PlanningStatus then A.PlanningStatus.Failed(statusID,candidate,reason) end
        if A.navigationWindow then A.navigationWindow.status:SetText(reason or 'No walking route found.') end
    end)
    if accepted and A.PlanningStatus then statusID=A.PlanningStatus.Begin(candidate,true) end
    return accepted,reason
end
