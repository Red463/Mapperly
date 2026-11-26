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
local function clipAxis(a,b,first,last)
    if a>=0 and a<=1 and b>=0 and b<=1 then return first,last end
    if a==b then return end
    local enter,leave=-a/(b-a),(1-a)/(b-a)
    first=math.max(first,math.min(enter,leave));last=math.min(last,math.max(enter,leave))
    if first<=last then return first,last end
end
-- Clip in normalized canvas coordinates before measuring marker or dot spacing.
function V.Clip(ax,ay,bx,by)
    local first,last=clipAxis(ax,bx,0,1)
    if first then first,last=clipAxis(ay,by,first,last) end
    if not first then return end
    local dx,dy=bx-ax,by-ay
    if last<1 then bx,by=ax+last*dx,ay+last*dy end
    if first>0 then ax,ay=ax+first*dx,ay+first*dy end
    return ax,ay,bx,by,first>0,last<1
end

-- Simplify only the drawing. The navigator still uses every verified waypoint.
-- Split at the furthest deviation from the chord, including a reversal along
-- the chord (a road can double back even when its points are collinear).
local function simplifySpan(segments, first, last, tolerance2, output)
    local start, finish = segments[first], segments[last]
    local ax, ay, bx, by = start[1], start[2], finish[3], finish[4]
    local dx, dy = bx - ax, by - ay
    local length2 = dx*dx + dy*dy
    local worst, peak, corner = tolerance2, 0, nil
    for i = first, last - 1 do
        local x, y = segments[i][3] - ax, segments[i][4] - ay
        local t = length2 > 0 and math.max(0, math.min(1, (x*dx + y*dy)/length2)) or 0
        local ex, ey = x - t*dx, y - t*dy
        local distance2 = ex*ex + ey*ey + math.max(0, peak - t)^2 * length2
        if distance2 > worst then worst, corner = distance2, i end
        peak = math.max(peak, t)
    end
    if corner then
        simplifySpan(segments, first, corner, tolerance2, output)
        simplifySpan(segments, corner + 1, last, tolerance2, output)
    elseif length2 > 0 then
        start[3], start[4] = bx, by
        output[#output + 1] = start
    end
end

local function displaySegments(segments, unit)
    local output, first = {}, 1
    local tolerance2 = (.55 * unit)^2
    while first <= #segments do
        local start, last = segments[first], first
        if start.kind == 'transport' then
            output[#output + 1] = start
        else
            -- Bounded spans keep even a 2,000-point switchback cheap to redraw.
            while last < #segments and last - first < 63 do
                local prev, nextSegment = segments[last], segments[last + 1]
                if nextSegment.split or nextSegment.kind ~= start.kind or
                    prev[3] ~= nextSegment[1] or prev[4] ~= nextSegment[2] then break end
                last = last + 1
            end
            local n = #output
            simplifySpan(segments, first, last, tolerance2, output)
            -- A zero-length clipped or duplicate sample may carry a real break.
            if #output == n and start.split and segments[last + 1] then segments[last + 1].split = true end
        end
        first = last + 1
    end
    return output
end

function V.Refresh(progressOnly)
    local style=A.RouteStyle
    if style then
        style.HideLines(V.lines);style.HideLines(V.fragments);style.Hide(V.directions)
    else
        for _,line in pairs(V.lines) do line:Hide() end
    end
    if V.window and V.window:IsShown() and V.followActive then
        local active=A.Journey and A.Journey.active
        if not active then V.window:Hide()
        elseif active~=V.plan then
            V.plan=active;V.candidate=A.Navigation.target;V.WriteSummary()
        elseif V.legIndex~=A.Journey.legIndex then V.WriteSummary()
        end
    end
    local plan=V.DisplayPlan()
    V.progressKey=style and style.Key(plan)
    V.progressIndex,V.progressFraction,V.progressPixels=nil,nil,0
    if A.BoatLinks and progressOnly~=true then A.BoatLinks.Update() end
    if not plan or not A.map or not A.db.showJourneyRoute then return end
    if #plan.points>2049 then return end -- Never replace omitted bends with unsafe shortcuts.
    local canvas=A.map:GetCanvas()
    if not V.overlay then
        V.overlay=CreateFrame('Frame',nil,canvas);V.overlay:SetAllPoints(canvas)
        V.overlay:EnableMouse(false);V.overlay:SetClipsChildren(true)
    end
    V.overlay:SetFrameLevel(V.LayerLevel(canvas))
    local map=A.map:GetMapID();local width,height=canvas:GetWidth(),canvas:GetHeight()
    if not finite(width) or not finite(height) or width<=0 or height<=0 then return end
    -- Distances below are in ordinary UI units; the canvas itself grows with zoom.
    local scale=canvas:GetEffectiveScale()
    local unit=finite(scale) and scale>0 and UIParent:GetEffectiveScale()/scale or 1
    local segments={}
    local marks={worldUnit=unit,spacing=145*unit,limit=24,size=5.5*unit,thickness=1.7*unit,strokeWidth=3*unit,anchor='TOPLEFT',
        inside=function(x,y) return x>=3*unit and x<=width-3*unit and y<=-3*unit and y>=-height+3*unit end}
    local function segment(i,kind,ax,ay,bx,by,split)
        local entered,left
        ax,ay,bx,by,entered,left=V.Clip(ax,ay,bx,by)
        if not ax then return true end
        ax,ay,bx,by=ax*width,-ay*height,bx*width,-by*height
        segments[#segments+1]={ax,ay,bx,by,slot=i,kind=kind,split=split or entered}
        return left
    end

    -- At world scale each service has one schematic connection between ports.
    -- If either port cannot project, retain any visible native path pieces.
    local schematic={}
    if map==947 and A.TransportLinks then
        for legIndex,leg in ipairs(plan.legs or {}) do
            local row=leg.transport
            if row and A.TransportLinks.methods[row.kind] and row.board and row.arrival then
                local ax,ay=V.Project(row.board,map);local bx,by=V.Project(row.arrival,map)
                if ax and bx then
                    local completed=A.Journey and A.Journey.active==plan and legIndex<(A.Journey.legIndex or 1)
                    segment(leg.first or #plan.points+legIndex,completed and 'completed' or 'transport',ax,ay,bx,by,true)
                    if leg.first and leg.last then
                        for i=leg.first,leg.last-1 do schematic[i]=true end
                    end
                end
            end
        end
    end
    if A.RouteProgress then V.progressIndex,V.progressFraction=A.RouteProgress.Split(plan) end
    local split=true
    for i=1,#plan.points-1 do
        local a,b=plan.points[i],plan.points[i+1]
        if not b.breakBefore and not schematic[i] then
            local ax,ay=V.Project(a,map);local bx,by=V.Project(b,map)
            if ax and bx then
                local kind=style and style.Kind(plan,i) or ((a.transport or b.transport) and 'transport' or 'ahead')
                if i==V.progressIndex and kind=='ahead' then
                    local dx,dy=bx-ax,by-ay
                    V.progressPixels=math.sqrt((dx*width)^2+(dy*height)^2)/unit
                    local fraction=V.progressFraction
                    if fraction>=1 then kind='completed'
                    elseif fraction>0 then
                        local x,y=ax+dx*fraction,ay+dy*fraction
                        -- Index zero holds the completed part of the current walking segment.
                        split=segment(0,'completed',ax,ay,x,y,split)
                        ax,ay=x,y
                    end
                end
                split=segment(i,kind,ax,ay,bx,by,split)
            else split=true
            end
        else split=true
        end
    end
    segments=displaySegments(segments,unit)
    for _,s in ipairs(segments) do
        local line=V.lines[s.slot]
        if not line then line=V.overlay:CreateLine(nil,'OVERLAY');V.lines[s.slot]=line end
        s.base=line
        if not style then
            line:SetThickness(marks.strokeWidth)
            if s.kind=='transport' then line:SetColorTexture(.3,.75,1,.9) else line:SetColorTexture(1,.77,.18,.9) end
            line:SetStartPoint('TOPLEFT',V.overlay,s[1],s[2]);line:SetEndPoint('TOPLEFT',V.overlay,s[3],s[4]);line:Show()
        end
    end
    if style then style.Render(segments,V.directions,V.fragments,V.overlay,marks) end
end
local progressDriver=CreateFrame('Frame',nil,UIParent);V.progressDriver=progressDriver;progressDriver:SetSize(1,1);progressDriver:EnableMouse(false)
local progressElapsed=0
progressDriver:SetScript('OnUpdate',function(_,dt)
    progressElapsed=progressElapsed+dt;if progressElapsed<.2 then return end;progressElapsed=0
    if A.RouteStyle and A.Journey and A.Journey.active and A.map and A.map:IsShown() and A.db.showJourneyRoute then
        local displayed=V.window and V.window:IsShown() and V.plan or A.Journey.active
        if V.progressKey~=A.RouteStyle.Key(displayed) then V.Refresh(true);return end
        if displayed==A.Journey.active and A.RouteProgress and #displayed.points<=2049 then
            local index,fraction,length=A.RouteProgress.Split(displayed)
            local delta=math.abs((fraction or 0)-(V.progressFraction or 0))
            if index~=V.progressIndex or index and delta>0 and (fraction==1 or fraction==0 or delta*length>=4 and delta*V.progressPixels>=3) then V.Refresh(true) end
        end
    end
end)
function V.Show(plan,candidate,drawer)
    V.plan=plan;V.candidate=candidate;V.followActive=A.Journey and A.Journey.active==plan;V.followDirect=false
    local U=A.Dialogs
    if not V.window then
        local f=U.ToolWindow('MapperlyJourneyPreview','Journey preview','Route and travel details',333,338);V.window=f
        local summary=U.Card(f,8,48,317,62)
        V.summary=U.Label(summary,'',8,4,'GameFontNormal');V.summary:SetSize(300,54);V.summary:SetWordWrap(true)
        V.summary:SetJustifyH('LEFT')
        local steps=U.Card(f,8,114,317,80)
        V.stepScroll=CreateFrame('ScrollFrame',nil,steps,'UIPanelScrollFrameTemplate')
        V.stepScroll:SetPoint('TOPLEFT',steps,'TOPLEFT',8,-6);V.stepScroll:SetWidth(277)
        local child=CreateFrame('Frame',nil,V.stepScroll);child:SetSize(277,1);V.stepScroll:SetScrollChild(child)
        V.steps=U.Label(child,'',2,2);V.steps:SetSize(273,1);V.steps:SetWordWrap(true);V.steps:SetJustifyH('LEFT');V.steps:SetJustifyV('TOP')
        local footer=CreateFrame('Frame',nil,f);footer:SetSize(317,132);footer:SetPoint('BOTTOM',f,'BOTTOM',0,6)
        local warning=U.Label(footer,'',4,2,'GameFontDisableSmall')
        warning:SetSize(310,62);warning:SetWordWrap(true);warning:SetJustifyH('LEFT');warning:SetJustifyV('TOP');V.warning=warning
        function f:FitToolHeight(height)
            local gain=self.hasJourneyControls and 0 or 32
            steps:SetHeight(height-256+gain);V.stepScroll:SetHeight(height-268+gain)
            warning:ClearAllPoints();warning:SetPoint('TOPLEFT',footer,'TOPLEFT',4,-2-gain)
        end
        f:FitToolHeight(f.toolHeight)
        V.start=U.Action(footer,'Start',0,100,73,function()
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
        V.pause=U.Action(footer,'Pause',0,68,80,function() A.Navigation.Pause() end)
        V.resume=U.Action(footer,'Resume',85,68,89,function() A.Navigation.Resume() end)
        V.skip=U.Action(footer,'Skip bend',179,68,138,function() A.Navigation.Skip() end)
        U.Action(footer,'Replan',78,100,84,function() A.Navigation.Replan() end)
        U.Action(footer,'Stop',167,100,73,function() A.Navigation.Stop();f:Hide() end)
        V.close=U.Action(footer,'Close',245,100,72,function()
            if A.drawerWindow==f and A.navigationWindow then
                A.SelectMapDrawer('navigate',A.navigationWindow)
            else f:Hide() end
        end)
        f:HookScript('OnHide',V.Refresh)
    end
    V.WriteSummary()
    V.close:SetText(drawer and 'Back' or 'Close')
    U.Show(V.window,drawer);V.Refresh()
end
function V.WriteSummary()
    local plan=V.plan
    if plan.kind=='direct' then
        V.summary:SetText(string.format('%s\nStraight-line distance: %d yd\nSmart routing is off; terrain is not checked.',plan.name or 'Destination',math.floor(plan.distance+.5)))
        V.warning:SetText('Straight-line guidance does not avoid obstacles. Start uses your current position.')
    else
        V.summary:SetText(string.format('%s\nWalking distance: %d yd || About %d min %s\nTerrain coverage: %s',plan.name or 'Destination',math.floor(plan.distance+.5),math.max(1,math.ceil(plan.estimatedSeconds/60)),plan.hasTransports and 'including transport' or 'on foot',plan.coverage or 'unknown'))
        local policy=plan.swimmingFallback and (plan.swimmingFallbackReason=='budget' and 'Dry-route search reached its limit; swimming is permitted on this route.' or 'A dry route could not be confirmed; swimming is permitted on this route.') or A.db.avoidSwimming and 'Dry routes are preferred; swimming remains available if needed.' or 'Swimming is allowed.'
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
    V.steps:SetText(plan.kind=='direct' and #text==0 and 'Follow the arrow to your destination.' or table.concat(text,'\n'))
    if V.stepScroll then
        V.steps:SetHeight(10000)
        local measured=V.steps.GetStringHeight and V.steps:GetStringHeight() or 0
        local height=math.max(18,#text*18,finite(measured) and measured+4 or 0)
        V.steps:SetHeight(height);V.stepScroll:GetScrollChild():SetHeight(height+4);V.stepScroll:SetVerticalScroll(0)
    end
    local active=A.Journey and A.Journey.active==plan
    local transit=active and A.Journey.Leg() and A.Journey.Leg().kind=='transport'
    V.skip:SetText(transit and 'Continue on foot' or 'Skip bend')
    V.legIndex=active and A.Journey.legIndex or nil
    V.pause:SetEnabled(active);V.resume:SetEnabled(active);V.skip:SetEnabled(active)
    if V.window then
        V.pause:SetShown(active);V.resume:SetShown(active);V.skip:SetShown(active)
        V.window.hasJourneyControls=active
        V.window:FitToolHeight(V.window:GetHeight())
    end
end
function V.OpenCurrent()
    local drawer=A.drawerKey=='navigate' and 'navigate' or nil
    if A.Journey and A.Journey.active and A.Navigation.target then V.Show(A.Journey.active,A.Navigation.target,drawer)
    elseif A.Navigation.target then
        local plan,reason=A.Journey.DirectPlan(A.Navigation.target)
        if plan then V.Show(plan,A.Navigation.target,drawer);V.followDirect=true;V.Refresh()
        else A.Print(reason);A.Navigation.RejectRequest(A.Navigation.target,reason) end
    else A.Print('Start or preview a journey first.') end
end
function V.CancelPreview()
    if V.window then V.window:Hide() end
    V.plan=nil;V.candidate=nil;V.followActive=false;V.followDirect=false
    if A.navigationWindow then A.navigationWindow.status:SetText('Routing preference changed.') end
end
function V.Preview(candidate)
    local drawer=A.drawerKey=='navigate' and A.map:IsShown() and 'navigate' or nil
    if A.db.navigationMode=='direct' then
        local plan,reason=A.Journey.DirectPlan(candidate)
        if not plan then return A.Navigation.RejectRequest(candidate,reason) end
        V.Show(plan,candidate,drawer)
        if A.navigationWindow then A.navigationWindow.status:SetText('Straight-line preview ready.') end
        return true
    end
    if A.PlanningJob.IsRunning() then
        return A.Navigation.RejectRequest(candidate,'A route is already being planned. Wait or stop it first.')
    end
    local statusID
    local accepted,reason=A.Journey.Request(candidate,function(plan)
        if not drawer or (A.drawerKey==drawer and A.map:IsShown()) then V.Show(plan,candidate,drawer) end
        if statusID and A.PlanningStatus then A.PlanningStatus.Ready(statusID,candidate,plan) end
        if A.navigationWindow then A.navigationWindow.status:SetText('Walking preview ready.') end
    end,function(reason)
        A.Print(reason)
        if statusID and A.PlanningStatus then A.PlanningStatus.Failed(statusID,candidate,reason) end
        if A.navigationWindow then A.navigationWindow.status:SetText(reason or 'No walking route found.') end
    end)
    if not accepted then return A.Navigation.RejectRequest(candidate,reason) end
    if A.PlanningStatus then statusID=A.PlanningStatus.Begin(candidate,true) end
    return accepted,reason
end
