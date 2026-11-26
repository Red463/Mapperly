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
    if A.JourneyView then A.JourneyView.Refresh() end
    if A.MinimapRoute then A.MinimapRoute.Update() end
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
    if f.remaining then f.remaining:Hide() end
    f.label:SetFontObject('GameFontNormal');f.label:SetText(reason);f:Show()
end
local function journeyLayout(f,walking)
    local following=not not walking
    local transit=following and A.Journey.Leg() and A.Journey.Leg().kind=='transport' or false
    if f.following~=following or f.onTransport~=transit then
        f.following=following;f.onTransport=transit;f.destination:ClearAllPoints()
        f.destination:SetPoint('TOP',f,'TOP',0,transit and -130 or following and -96 or -78)
        f:SetHeight(transit and 160 or 126);f.remaining:SetWidth(transit and 260 or 200)
    end
end
function N.Build()
    if N.frame then return end
    local f=CreateFrame('Frame','MapperlyNavigationArrow',UIParent);N.frame=f
    f:SetSize(200,126);f:SetPoint('CENTER',UIParent,'CENTER',180,140)
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
    f.remaining=f:CreateFontString(nil,'OVERLAY','GameFontHighlightSmall');f.remaining:SetPoint('TOP',f,'TOP',0,-76);f.remaining:SetWidth(200);f.remaining:SetJustifyH('CENTER');f.remaining:Hide()
    f.destination=f:CreateFontString(nil,'OVERLAY','GameFontHighlightSmall');f.destination:SetPoint('TOP',f,'TOP',0,-78);f.destination:SetWidth(200);f.destination:SetWordWrap(false);f.destination:SetJustifyH('CENTER')
    f:SetScript('OnEnter',function(self)
        GameTooltip:SetOwner(self,'ANCHOR_RIGHT');GameTooltip:SetText('Mapperly navigation')
        if N.target then GameTooltip:AddLine(string.format('%s: %.4f, %.4f',N.target.zone,N.target.x*100,N.target.y*100),1,.82,0,true) end
        GameTooltip:AddLine(A.Journey and A.Journey.active and 'Following a terrain-estimated walking route.' or 'Straight-line direction; no walking path is calculated.',1,1,1,true)
        if A.Journey and A.Journey.active then GameTooltip:AddLine('Arrow and primary distance guide to the next route turn. Total route distance is shown below.',1,1,1,true) end
        if N.recoveryError then GameTooltip:AddLine('Route update unavailable; keeping previous guidance. '..tostring(N.recoveryError),1,.82,0,true) end
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
local function activate(candidate,plan)
    local steps,previous=A.RouteSteps,N.target
    local keepDismissed=N.autoReplan and steps and previous and steps.dismissedTarget==previous and candidate.map==previous.map and number(previous.x) and number(previous.y) and math.abs(candidate.x-previous.x)<1e-8 and math.abs(candidate.y-previous.y)<1e-8
    N.pending=nil;N.autoReplan=nil;N.planningError=nil;N.recoveryError=nil;N.target=candidate;N.deferredRoutingTarget=nil
    if keepDismissed then steps.dismissedTarget=candidate end
    if A.Journey then if plan then A.Journey.Install(plan) else A.Journey.Clear() end end
    if A.Destinations then A.Destinations.Remember(candidate) end
    N.Build();N.frame.bearing=nil;N.frame.renderAngle=nil
    N.frame.destination:SetText(string.format('%s (%.1f, %.1f)',candidate.name,candidate.x*100,candidate.y*100))
    if A.JourneySession then A.JourneySession.Installed(candidate) end
    candidate.sessionResume=nil
    N.Tick();refresh()
    if A.RouteSteps then A.RouteSteps.Refresh() end
end
function N.RejectRequest(candidate,reason,options)
    if A.RouteReport then A.RouteReport.RecordRequest(candidate,reason) end
    if candidate and A.PlanningStatus and not (options and options.automatic) then
        A.PlanningStatus.Failed(nil,candidate,reason)
    end
    return nil,reason
end
local function intent(options)
    if A.JourneySession and not (options and (options.automatic or options.sessionResume)) then A.JourneySession.Intent() end
end
function N.Start(map,x,y,name,options)
    local nx,ny=N.Parse(x,y)
    if nx==nil then return N.RejectRequest(nil,ny,options) end
    map=tonumber(map)
    if not number(map) or map<1 or map%1~=0 then return N.RejectRequest(nil,'Choose a map before entering coordinates.',options) end
    local candidate={map=map,x=nx,y=ny,name=type(name)=='string' and name:sub(1,120) or nil}
    local hbd=library()
    if not hbd or type(hbd.GetWorldCoordinatesFromZone)~='function' then return N.RejectRequest(candidate,'Map coordinates are not available yet. Try again shortly.',options) end
    local ok,wx,wy,instance=pcall(hbd.GetWorldCoordinatesFromZone,hbd,nx,ny,map)
    if not ok or not number(wx) or not number(wy) or not number(instance) then return N.RejectRequest(candidate,'This map cannot be used for navigation. Open a zone or continent map.',options) end
    local info=C_Map.GetMapInfo and C_Map.GetMapInfo(map)
    local zone=info and info.name or 'Map '..map
    if not candidate.name or candidate.name:match('^%s*$') then candidate.name=zone end
    candidate.worldX,candidate.worldY,candidate.instance=wx,wy,instance
    candidate.category='navigation';candidate.zone=zone
    candidate.walkingOnly=options and options.walkingOnly or nil
    candidate.sessionResume=options and options.sessionResume or nil
    local currentLeg=A.Journey and A.Journey.Leg()
    if A.Flights and (A.Flights.OnTaxi()==true or currentLeg and currentLeg.transport and currentLeg.transport.kind=='flight' and A.Flights.ShouldDefer(A.Journey.transportState)) then
        if A.PlanningJob then A.PlanningJob.Cancel() end
        N.pending=nil;N.autoReplan=nil;N.deferredRoutingTarget=candidate
        intent(options)
        N.Build();N.Tick()
        if A.Print and not (options and options.automatic) then A.Print('Destination saved. The new route will be planned after landing.') end
        return true
    end
    if A.Journey and (options and options.mode or A.db.navigationMode)~='direct' then
        local statusID
        local accepted,reason=A.Journey.Request(candidate,function(plan)
            if A.Flights and A.Flights.OnTaxi()==true then
                N.pending=nil;N.autoReplan=nil
                if not (options and options.automatic) then N.deferredRoutingTarget=candidate end
                if statusID and A.PlanningStatus then A.PlanningStatus.Clear() end
                N.Tick();refresh();return
            end
            activate(candidate,plan)
            if statusID and A.PlanningStatus then A.PlanningStatus.Ready(statusID,candidate,plan) end
        end,function(why)
            N.pending=nil;N.autoReplan=nil
            if options and options.sessionResume and A.JourneySession then A.JourneySession.Intent() end
            if options and options.automatic then N.recoveryError=why else N.planningError=why;if A.Print then A.Print(why) end end
            if not N.target and N.frame then waiting(why or 'No walking route found') end
            if statusID and A.PlanningStatus then A.PlanningStatus.Failed(statusID,candidate,why) end
            refresh()
        end,options and options.continueJourney)
        if not accepted then return N.RejectRequest(candidate,reason,options) end
        intent(options)
        N.pending=candidate;N.autoReplan=options and options.automatic or nil;N.planningError=nil;N.deferredRoutingTarget=nil;N.Build()
        if not N.autoReplan and A.RouteRecovery then A.RouteRecovery.Clear() end
        if not N.autoReplan and A.PlanningStatus then statusID=A.PlanningStatus.Begin(candidate) end
        if not N.target then waiting('Planning walking route...') end
        return true
    end
    if A.PlanningJob then A.PlanningJob.Cancel() end
    if A.PlanningStatus then A.PlanningStatus.Clear() end
    intent(options)
    activate(candidate)
    return true
end
function N.ToPin(pin)
    if pin and pin.serviceKey and A.NearestServices then
        local current,why=A.NearestServices.Resolve(pin)
        if not current then return nil,why end
        pin=current
    end
    if not A.ValidPin(pin) then return nil,'This marker has no usable map coordinates.' end
    local ok,reason=N.Start(pin.map,pin.x*100,pin.y*100,pin.name,{walkingOnly=pin.walkingOnly})
    if not ok and A.Print then A.Print(reason) end
    return ok,reason
end
local function restart(target,options)
    options.walkingOnly=target.walkingOnly
    options.sessionResume=target.sessionResume
    return N.Start(target.map,target.x*100,target.y*100,target.name,options)
end
function N.CancelPlanning()
    if A.PlanningJob then A.PlanningJob.Cancel() end
    if A.JourneySession then A.JourneySession.Intent() end
    N.pending=nil;N.autoReplan=nil;N.handoffPending=nil;N.planningError=nil;N.recoveryError=nil;N.deferredRoutingTarget=nil
    if A.navigationWindow then A.navigationWindow.status:SetText('Route calculation cancelled.') end
    N.Tick();refresh()
end
function N.Stop(arrived)
    local pending=arrived and not N.autoReplan and N.pending or nil
    if A.PlanningJob and not pending then A.PlanningJob.Cancel() end
    if A.Journey then A.Journey.Clear() end
    if A.JourneySession then A.JourneySession.Clear() end
    N.pending=pending;N.autoReplan=nil;N.handoffPending=nil;N.planningError=nil;N.recoveryError=nil;N.target=nil;N.deferredRoutingTarget=nil
    if A.RouteRecovery then A.RouteRecovery.Clear() end
    if N.frame then N.frame:Hide() end
    GameTooltip:Hide();refresh()
    if pending then N.Build();waiting('Planning walking route...') end
    if arrived and A.Print then A.Print('Arrived at your navigation destination.') end
end
local function cancelAutomatic()
    if not N.autoReplan then return end
    if A.PlanningJob then A.PlanningJob.Cancel() end
    N.pending=nil;N.autoReplan=nil;N.recoveryError=nil
end
function N.Tick()
    local target=N.target
    if A.Flights and A.Flights.OnTaxi()==true then
        if N.autoReplan then cancelAutomatic() end
        if N.pending then
            local deferred=N.pending
            A.PlanningJob.Cancel();N.pending=nil;N.deferredRoutingTarget=deferred
            if A.PlanningStatus then A.PlanningStatus.Clear() end
        end
    end
    if N.handoffPending then
        if N.pending==N.handoffPending and A.PlanningJob.IsRunning() then
            N.Build();journeyLayout(N.frame,A.Journey.active);waiting('Updating walking route...');return
        end
        N.handoffPending=nil
    end
    if target and N.deferredRoutingTarget and not (A.Journey and A.Journey.active) and
        A.Flights and A.Flights.worldReady and A.Flights.OnTaxi()==false and not N.pending then
        local deferred=N.deferredRoutingTarget;N.deferredRoutingTarget=nil
        local ok,why=restart(deferred,{mode=A.db.navigationMode})
        if not ok and A.Print then A.Print(why) end
        return
    end
    if not target then
        if N.deferredRoutingTarget then
            if A.Flights and A.Flights.worldReady and A.Flights.OnTaxi()==false then
                local deferred=N.deferredRoutingTarget;N.deferredRoutingTarget=nil
                local ok,why=restart(deferred,{mode=A.db.navigationMode})
                if not ok then N.planningError=why;N.Build();waiting(why) end
            else N.Build();waiting('Waiting to land before planning route...') end
        elseif N.pending then N.Build();waiting('Planning walking route...')
        elseif N.planningError then N.Build();waiting(N.planningError)
        elseif N.frame then N.frame:Hide() end
        return
    end
    local dx,dy,remaining
    local walking=A.Journey and A.Journey.active
    if walking then
        local player=A.Journey.PlayerPosition()
        if not A.Journey.paused then player=A.Journey.RoutePosition(player) end
        if A.RouteRecovery then
            local recovery=A.RouteRecovery.Update(player,nil,not N.pending and not A.PlanningJob.IsRunning())
            if recovery.rejoined or recovery.onRoute and N.autoReplan then cancelAutomatic();refresh() end
            if recovery.replan and not N.pending and not A.PlanningJob.IsRunning() then
                local ok,reason=restart(target,{mode='terrain',automatic=true})
                if not ok then N.recoveryError=reason end
            end
        end
        local oldLeg=A.Journey.legIndex
        local oldTransport=A.Journey.Leg() and A.Journey.Leg().transport
        local bend,reason=A.Journey.Update(player,true)
        local passengerExited=oldTransport and oldTransport.kind~='flight' and oldLeg~=A.Journey.legIndex
        if oldLeg~=A.Journey.legIndex and A.JourneyView then A.JourneyView.Refresh() end
        local flightState=A.Journey.transportState
        if flightState and flightState.interrupted and not flightState.replanAttempted and not N.pending and not A.PlanningJob.IsRunning() and player and A.Terrain.Segment(player,player) then
            flightState.replanAttempted=true
            local replacement=N.deferredRoutingTarget or target
            local ok,why=restart(replacement,{mode='terrain',automatic=true})
            if not ok then N.recoveryError=why end
        end
        if N.deferredRoutingTarget and not (A.Transports and A.Transports.ShouldDefer()) and not (flightState and flightState.interrupted) and not N.pending then
            local deferred=N.deferredRoutingTarget;N.deferredRoutingTarget=nil
            local ok,why=restart(deferred,{mode=A.db.navigationMode})
            if not ok and A.Print then A.Print(why) end
        end
        -- Boat/lift exits need not coincide with the precomputed shore point.
        -- Rebase from confirmed arrival ground before normal off-route recovery
        -- can mistake that transfer for a detour. Certified piers already join
        -- their native walking floor, so retain those protected paths unchanged.
        local joinedDock=passengerExited and oldTransport.arrivalCorridor and A.Transports.DockCorridor(oldTransport.arrivalCorridor) and
            A.Structures and A.Structures.Contains(player,oldTransport.arrivalCorridor)
        if passengerExited and not joinedDock and reason~='arrived' and A.Journey.active==walking and N.target==target and
            not N.pending and not N.deferredRoutingTarget and not A.PlanningJob.IsRunning() then
            local ok,why=restart(target,{mode='terrain',automatic=true,continueJourney=true})
            if ok and N.pending then
                N.handoffPending=N.pending;journeyLayout(N.frame,walking);waiting('Updating walking route...');return
            end
            if not ok then N.recoveryError=why end
        end
        journeyLayout(N.frame,walking)
        if not bend then
            if reason=='arrived' then N.Stop(true) else waiting(reason) end
            return
        end
        -- Use the same local position and map extents as the route/follower.
        -- Mixing C_Map positions with a separately sampled world-position
        -- feed can send the HUD in a different direction from the map line.
        local zone=A.Terrain.Zone(bend.mapID)
        if not zone then waiting('Route position unavailable');return end
        if player and player.mapID~=bend.mapID and A.TravelNetwork then player=A.TravelNetwork.Transform(player,bend.mapID) end
        if not player then waiting('Route position unavailable');return end
        dx=-(bend.x-player.x)*zone.widthYards
        dy=-(bend.y-player.y)*zone.heightYards
        remaining=A.Journey.Remaining(player)
    else
        local hbd=library()
        if not hbd or type(hbd.GetPlayerWorldPosition)~='function' then waiting('Position unavailable');return end
        local ok,px,py,instance=pcall(hbd.GetPlayerWorldPosition,hbd)
        if not ok or not number(px) or not number(py) or not number(instance) then waiting('Position unavailable');return end
        if instance~=target.instance then waiting('Different continent / instance');return end
        dx,dy=target.worldX-px,target.worldY-py
    end
    local distance=math.sqrt(dx*dx+dy*dy)
    if not number(distance) then waiting('Position unavailable');return end
    if not (A.Journey and A.Journey.active) and distance<=10 then N.Stop(true);return end
    local heading=facing()
    if heading==nil then waiting('Direction unavailable');return end
    local f=N.frame
    local following=not not walking
    journeyLayout(f,walking)
    if following then
        local status=A.Journey.transportMessage or (N.autoReplan and 'Updating route' or A.RouteRecovery and A.RouteRecovery.IsOffRoute() and 'Rejoin route' or A.Journey.inStructure and 'Tunnel passage' or A.Journey.crossing and 'Zone crossing' or A.Journey.index<#walking.points and 'Next turn' or 'Destination')
        f.remaining:SetText(string.format('%s  |  %d yd remaining',status,math.floor(remaining+.5)))
        f.remaining:Show()
    else f.remaining:Hide() end
    f.bearing=N.Bearing(dx,dy)
    f.label:SetFontObject('GameFontNormalLarge')
    f.label:SetText(string.format('%d yd',math.floor(distance+.5)))
    if f.renderAngle==nil then rotate(f,normalize(f.bearing-heading)) end
    f.icon:Show();f.shadow:Show();f:Show()
end
function N.Pause()
    cancelAutomatic()
    if A.Journey then A.Journey.Pause();if A.JourneySession then A.JourneySession.Capture() end;N.Tick();refresh() end
end
function N.Resume()
    if not A.Journey then return end
    local ok,reason=A.Journey.Resume(A.Journey.PlayerPosition())
    if not ok and A.Print then A.Print(reason) end
    if ok and A.JourneySession then A.JourneySession.Capture() end
    N.Tick();refresh();return ok,reason
end
function N.Skip()
    if not A.Journey then return end
    local transit=A.Journey.Leg() and A.Journey.Leg().kind=='transport'
    local ok,reason
    if transit then ok,reason=A.Journey.ConfirmTransportArrival(A.Journey.PlayerPosition()) else ok,reason=A.Journey.Skip(A.Journey.PlayerPosition()) end
    if not ok and A.Print then A.Print(reason) end
    N.Tick();refresh();return ok,reason
end
function N.Replan()
    local t=N.deferredRoutingTarget or N.target
    if t then return restart(t,{mode=A.Journey and A.Journey.active and 'terrain' or A.db.navigationMode}) end
end
function N.SetSmartRouting(enabled)
    local mode=enabled and 'terrain' or 'direct'
    if A.db.navigationMode==mode then return true end
    local target=N.pending or N.deferredRoutingTarget or N.target
    local leg=A.Journey and A.Journey.Leg()
    A.db.navigationMode=mode
    if A.PlanningJob then A.PlanningJob.Cancel() end
    N.pending=nil;N.autoReplan=nil;N.planningError=nil
    -- A preview belongs to its planning mode. Close it rather than letting an
    -- old walking preview contradict an explicit switch to direct guidance.
    if A.JourneyView then A.JourneyView.CancelPreview() end
    local ok,reason=true
    if target and A.Flights and (A.Flights.OnTaxi()==true or A.Transports and A.Transports.ShouldDefer() and A.Journey.Leg().transport.kind=='flight') then N.deferredRoutingTarget=target
    elseif target and mode=='direct' then activate(target)
    elseif target then ok,reason=restart(target,{mode=mode})
    else
        if A.Journey then A.Journey.Clear() end
        N.Tick();refresh()
    end
    if A.NavigationSettings then A.NavigationSettings.Sync() end
    if not ok and A.Print then A.Print(reason) end
    return ok,reason
end
local function routingPreferenceChanged(automatic)
    local target=N.pending or N.deferredRoutingTarget or N.target
    local ok,reason=true
    if A.db.navigationMode~='direct' then
        if A.PlanningJob then A.PlanningJob.Cancel() end
        N.pending=nil;N.autoReplan=nil;N.planningError=nil
        if A.JourneyView then A.JourneyView.CancelPreview() end
        if target and A.Transports and A.Transports.ShouldDefer() then N.deferredRoutingTarget=target
        elseif target then ok,reason=restart(target,{mode='terrain',automatic=automatic}) end
        N.Tick();refresh()
    end
    if A.NavigationSettings then A.NavigationSettings.Sync() end
    if not ok and A.Print then A.Print(reason) end
    return ok,reason
end
function N.SetPreferRoads(enabled)
    enabled=not not enabled
    if A.db.preferRoads==enabled then return true end
    A.db.preferRoads=enabled
    return routingPreferenceChanged()
end
function N.SetAvoidSwimming(enabled)
    enabled=not not enabled
    if A.db.avoidSwimming==enabled then return true end
    A.db.avoidSwimming=enabled
    A.db.allowSwimming=true
    return routingPreferenceChanged(false)
end
-- Retain the former API for integrations, with the new best-effort semantics.
function N.SetAllowSwimming(enabled) return N.SetAvoidSwimming(not enabled) end
function N.SetRoadPreferenceStrength(value)
    local level=A.Roads.Strength(value)
    if A.db.roadPreferenceStrength==level then return true end
    A.db.roadPreferenceStrength=level
    if A.db.preferRoads then return routingPreferenceChanged() end
    if A.NavigationSettings then A.NavigationSettings.Sync() end
    return true
end
function N.SetTransportPreference(kind,enabled)
    local key=({boat='useBoats',zeppelin='useZeppelins',airship='useAirships',flight='useFlights',tram='useTrams',lift='useLifts'})[kind]
    if not key then return nil,'Unknown travel method.' end
    enabled=not not enabled
    if A.db[key]==enabled then return true end
    A.db[key]=enabled
    return routingPreferenceChanged()
end
function N.OnFlightsChanged()
    local leg=A.Journey and A.Journey.Leg()
    if A.Flights and (A.Flights.OnTaxi()==true or leg and leg.transport and leg.transport.kind=='flight' and A.Flights.ShouldDefer(A.Journey.transportState)) then return true end
    if N.deferredRoutingTarget or N.pending and not N.autoReplan then return true end
    if A.db.navigationMode~='direct' and (N.pending or N.deferredRoutingTarget or N.target) then return routingPreferenceChanged(true) end
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
