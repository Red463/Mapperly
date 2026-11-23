local _,A=...
local J={};A.Journey=J
local function point(p)
    if type(p)~='table' then return end
    local map=p.mapID or p.map
    for _,v in ipairs({map,p.x,p.y}) do if issecretvalue and issecretvalue(v) then return end end
    if not A.ValidPin({map=map,x=p.x,y=p.y,name=p.name or 'Walking point'}) then return end
    return {mapID=A.TravelNetwork and A.TravelNetwork.Canonical(map) or map,x=p.x,y=p.y}
end
local function endpoints(start,goal,options)
    local a,b=point(start),point(goal)
    if not a or not b then return nil,'Invalid walking route coordinates.' end
    local zone=A.Terrain.Zone(a.mapID)
    if not zone or not A.Terrain.Zone(b.mapID) then return nil,'Terrain coverage is unavailable for this map.' end
    if a.mapID~=b.mapID and not A.TravelNetwork then return nil,'Walking network is unavailable.' end
    local boarding=A.Flights and A.Flights.ContextValid(options and options.boardingContext,a)
    local cityStart=A.CityNavigation and A.CityNavigation.Supports(a,options)
    local cityGoal=A.CityNavigation and A.CityNavigation.Supports(b,options)
    if (not boarding and not cityStart and not A.Terrain.Segment(a,a)) or (not cityGoal and not A.Terrain.Segment(b,b)) then return nil,'The start or destination is blocked or outside known terrain.' end
    return a,b,zone
end
local function plan(start,goal,options)
    local a,b,zone=endpoints(start,goal,options)
    if not a then return nil,b end
    local preferRoads=options and options.preferRoads
    if preferRoads==nil then preferRoads=A.db and A.db.preferRoads end
    local strength=options and options.roadPreferenceStrength
    if strength==nil then strength=A.db and A.db.roadPreferenceStrength end
    local speed=options and options.speed or 7
    if type(speed)~='number' or speed~=speed or speed<=0 or speed==math.huge then speed=7 end
    local networkOptions={preferRoads=preferRoads,roadPreferenceStrength=strength,name=goal.name or 'Destination',speed=speed,faction=options and options.faction,boardingContext=options and options.boardingContext,start=a,
        walkingOnly=options and options.walkingOnly,maxWalkingCells=options and options.maxWalkingCells}
    if a.mapID~=b.mapID or A.Flights and A.Flights.ContextValid(networkOptions.boardingContext,a) then
        return A.TravelNetwork.Plan(a,b,networkOptions)
    end
    local progress=A.PlanningJob and A.PlanningJob.Progress();local before=progress and progress.cells or 0
    local points,distance=A.Terrain.Path(a,b,{maxExpansions=math.min(262144,networkOptions.maxWalkingCells or 262144),preferRoads=preferRoads,roadPreferenceStrength=strength})
    if not points and A.CityNavigation then points,distance=A.CityNavigation.Path(a,b,options) end
    if not points and A.TravelNetwork and A.StructureData then
        local after=A.PlanningJob and A.PlanningJob.Progress()
        if networkOptions.maxWalkingCells and after then networkOptions.maxWalkingCells=math.max(0,networkOptions.maxWalkingCells-(after.cells-before)) end
        return A.TravelNetwork.Plan(a,b,networkOptions)
    end
    if not points then
        return nil,distance=='budget' and 'Route search reached its limit. Try a closer waypoint.' or 'No walking connection was found through the available terrain.'
    end
    local transports=not networkOptions.walkingOnly and A.Transports and A.Transports.Edges(networkOptions) or {}
    if #transports>0 and distance>A.Transports.MinimumSeconds(transports)*speed and
        (not A.TravelNetwork.CanImproveWithTransport or A.TravelNetwork.CanImproveWithTransport(a,b,transports,speed,distance)) then
        networkOptions.candidatePoints=points;networkOptions.candidateDistance=distance
        return A.TravelNetwork.Plan(a,b,networkOptions)
    end
    return {kind='walking',multiZone=points.cityGuidance or nil,points=points,distance=distance,estimatedSeconds=distance/speed,
        mapID=a.mapID,name=goal.name or 'Destination',coverage=points.cityGuidance and 'city guidance' or zone.status,hasCityGuidance=points.cityGuidance,
        legs={{kind='walk',name='Walk to '..(goal.name or 'destination'),mapID=a.mapID,first=1,last=#points,cityGuidance=points.cityGuidance,points=points,distance=distance,estimatedSeconds=distance/speed}}}
end
-- Prefer a complete dry itinerary; never treat the preference as a prohibition.
function J.Plan(start,goal,options)
    local water=A.Water
    if not water or not water.WithPlanningPolicy then return plan(start,goal,options) end
    local function work() return plan(start,goal,options) end
    if options and type(options.allowSwimming)=='boolean' then
        return water.WithPlanningPolicy(options.allowSwimming,work)
    end
    if A.db and A.db.avoidSwimming then
        local dry=water.WithPlanningPolicy(false,work)
        if dry then return dry end
        if A.PlanningJob then A.PlanningJob.Report('Trying route with swimming permitted') end
        local result,reason=water.WithPlanningPolicy(true,work)
        if result then result.swimmingFallback=true end
        return result,reason
    end
    return work()
end
function J.DirectPlan(candidate)
    local hbd=LibStub and LibStub('HereBeDragons-2.0',true)
    if not hbd or type(hbd.GetPlayerWorldPosition)~='function' then return nil,'Player position is unavailable.' end
    local function valid(v) return not (issecretvalue and issecretvalue(v)) and type(v)=='number' and v==v and math.abs(v)<math.huge end
    local ok,px,py,instance=pcall(hbd.GetPlayerWorldPosition,hbd)
    if not ok or not valid(px) or not valid(py) or not valid(instance) then return nil,'Player position is unavailable.' end
    local wx,wy,wi=candidate.worldX,candidate.worldY,candidate.instance
    if not valid(wx) or not valid(wy) or not valid(wi) then
        local good
        good,wx,wy,wi=pcall(hbd.GetWorldCoordinatesFromZone,hbd,candidate.x,candidate.y,candidate.map or candidate.mapID)
        if not good or not valid(wx) or not valid(wy) or not valid(wi) then return nil,'Destination coordinates are unavailable.' end
    end
    if wi~=instance then return nil,'Direct guidance waits until you reach the destination continent or instance.' end
    local length=math.sqrt((wx-px)^2+(wy-py)^2)
    return {kind='direct',name=candidate.name or 'Destination',distance=length,estimatedSeconds=length/7,coverage='not checked',
        points={{worldX=px,worldY=py,instance=instance},{worldX=wx,worldY=wy,instance=wi}},
        legs={{kind='direct',name='Head towards '..(candidate.name or 'destination')}}}
end
function J.PlayerPosition()
    if not C_Map or not C_Map.GetBestMapForUnit or not C_Map.GetPlayerMapPosition then return nil,'Player position is unavailable.' end
    local ok,map=pcall(C_Map.GetBestMapForUnit,'player')
    if not ok or not map then return nil,'Player zone is unavailable.' end
    local good,p=pcall(C_Map.GetPlayerMapPosition,map,'player')
    if not good or not p or issecretvalue and issecretvalue(p) then return nil,'Player position is unavailable.' end
    local readable,x,y=pcall(p.GetXY,p)
    local result=readable and point({mapID=map,x=x,y=y})
    return result,result and nil or 'Player position is unavailable.'
end
function J.Request(candidate,done,failed,continueJourney)
    if A.Flights and A.Flights.OnTaxi()==true then return nil,'Wait until you land before planning a walking journey.' end
    local start,reason=J.PlayerPosition()
    if not start then return nil,reason end
    if continueJourney and J.Leg() and J.Leg().kind=='walk' and A.TravelNetwork then
        -- Native zone assignment can lag behind a verified transport handoff.
        -- Keep the actual world position on the current walking map; this
        -- changes neither coordinates nor ground permissions.
        local projected=A.TravelNetwork.Transform(start,J.MapID())
        if projected and A.Terrain.Segment(projected,projected) then start=projected end
    end
    local options={boardingContext=A.Flights and A.Flights.BoardingContext(start),walkingOnly=candidate.walkingOnly}
    local a,b=endpoints(start,candidate,options)
    if not a then return nil,b end
    A.PlanningJob.Start(function() return J.Plan(start,candidate,options) end,done,failed)
    return true
end
function J.Install(plan)
    J.active=plan;J.index=math.min(2,#plan.points);J.paused=false;J.legIndex=plan.multiZone and 1 or nil;J.crossing=false;J.inStructure=nil;J.structureIndex=nil;J.transportState=nil;J.transportMessage=nil
end
function J.Clear() J.active=nil;J.index=nil;J.paused=false;J.legIndex=nil;J.crossing=false;J.inStructure=nil;J.structureIndex=nil;J.transportState=nil;J.transportMessage=nil end
function J.Leg() return J.active and J.active.multiZone and J.active.legs[J.legIndex] end
function J.MapID() local leg=J.Leg();return leg and leg.mapID or J.active and J.active.mapID end
function J.Bounds() local leg=J.Leg();return leg and leg.first or 1,leg and leg.last or J.active and #J.active.points or 0 end
function J.Current()
    local leg=J.Leg()
    if leg and leg.kind=='transport' then return leg.transport.board end
    if J.crossing and leg then return leg.exitPath and leg.exitPath[J.structureIndex or 2] or leg.exitAim end
    return J.active and J.active.points[J.index]
end
function J.Prepare(position)
    local p=point(position);local plan=J.active
    if not p or not plan then return end
    local nextLeg=plan.multiZone and plan.legs[J.legIndex+1]
    if J.Leg() and J.Leg().kind=='transport' then return true end
    local sameMap=p.mapID==J.MapID()
    local leg=J.Leg();local floorFinished=not J.inStructure or not leg.exitPath or (J.structureIndex or 2)>=#leg.exitPath
    if nextLeg and floorFinished and p.mapID==nextLeg.mapID and (not sameMap and (J.crossing or A.TravelNetwork.Distance(p,nextLeg.points[1])<=8) or sameMap and J.crossing and A.TravelNetwork.Distance(p,nextLeg.points[1])<=8) then
        J.inStructure=J.Leg().exitStructure
        J.legIndex=J.legIndex+1;J.index=nextLeg.first;J.crossing=false
        if A.RouteRecovery then A.RouteRecovery.LegChanged() end
        return true
    end
    if sameMap then return true end
end
function J.RoutePosition(position)
    local p=point(position);if not p or not J.active then return end
    if J.Prepare(p) then return p end
    if J.inStructure then return p end
    -- Native map assignments can change within overlapping artwork bounds
    -- before a geometric leg ends. Continue the same geometry in that case.
    if J.active.multiZone and A.TravelNetwork then return A.TravelNetwork.Transform(p,J.MapID()) end
end
local function distance(a,b)
    if (not a.mapID or not b.mapID or a.mapID~=b.mapID) and A.TravelNetwork then return A.TravelNetwork.Distance(a,b) or 0 end
    local z=A.Terrain.Zone(a.mapID)
    return math.sqrt(((a.x-b.x)*z.widthYards)^2+((a.y-b.y)*z.heightYards)^2)
end
local function advanceFloor(p,leg)
    local path=leg.exitPath;local at=J.structureIndex
    local x,y=A.TravelNetwork.World(p)
    if not x or not A.Structures.Contains(p,leg.exitStructure) then return end
    local walked=0;local best,bestDistance;local found=false
    -- Samples are denser than normal movement updates. Project onto the first
    -- nearby continuous run of floor segments, rather than requiring a hit on
    -- every vertex. Do not jump to a parallel return passage across a hairpin.
    for i=at,#path do
        local a,b=path[i-1],path[i]
        local dx,dy=b.worldX-a.worldX,b.worldY-a.worldY;local length=dx*dx+dy*dy
        local t=length>0 and math.max(0,math.min(1,((x-a.worldX)*dx+(y-a.worldY)*dy)/length)) or 0
        local d=(x-a.worldX-t*dx)^2+(y-a.worldY-t*dy)^2
        if d<=6.25 then
            found=true
            if not bestDistance or d<bestDistance-.000001 then best,bestDistance=i,d end
        elseif found then break end
        walked=walked+math.sqrt(length)
        if walked>30 then break end
    end
    if best then J.structureIndex=best end
    while J.structureIndex<#path and distance(p,J.Current())<=1 do J.structureIndex=J.structureIndex+1 end
end
local function joinDockArrival(p,id)
    local leg=J.Leg()
    if not p or not leg or leg.kind~='walk' or not A.Transports.DockCorridor(id) or not A.Structures.Contains(p,id) then return end
    local path,first,last
    if leg.exitStructure==id then path=leg.exitPath;first=2;last=#path
    else path=J.active.points;first=leg.first+1;last=leg.last end
    local x,y=A.TravelNetwork.World(p);local best,nearest
    for i=first,last do
        local a,b=path[i-1],path[i]
        if not A.Structures.Contains(a,id) or not A.Structures.Contains(b,id) then break end
        local ax,ay=A.TravelNetwork.World(a);local bx,by=A.TravelNetwork.World(b)
        local dx,dy=bx-ax,by-ay;local length=dx*dx+dy*dy
        local t=length>0 and math.max(0,math.min(1,((x-ax)*dx+(y-ay)*dy)/length)) or 0
        local d=(x-ax-t*dx)^2+(y-ay-t*dy)^2
        if d<=6.25 and (not nearest or d<nearest) then best=i;nearest=d end
    end
    if best then
        if leg.exitStructure==id then J.crossing=true;J.inStructure=id;J.structureIndex=best;J.index=leg.last
        else J.index=best end
    end
end
-- The entrance floor may be inherited for the first city point. Retain it
-- while still on that floor, then release it for coarse city wayfinding.
function J.ReleaseAccessStructure(p)
    local leg=J.Leg()
    if not leg or not (leg.cityGuidance or leg.portalGuidance) or not J.inStructure or J.crossing then return end
    if type(p)~='table' or not A.ValidPin({map=p.mapID,x=p.x,y=p.y,name='City position'}) then return end
    if A.Structures and not A.Structures.Contains(p,J.inStructure) then J.inStructure=nil end
end
function J.Update(position,keepGuidance)
    local plan=J.active;if not plan then return nil,'No walking journey' end
    if J.paused then return nil,'Paused' end
    local transit=J.Leg()
    local nextTransit=transit and transit.kind=='walk' and plan.legs[(J.legIndex or 1)+1]
    if nextTransit and nextTransit.transport and nextTransit.transport.automaticTram and A.Trams then
        if A.Flights and A.Flights.worldReady==false then return nil,'Loading the tram station...' end
        if A.Trams.Inside() then
            J.legIndex=J.legIndex+1;J.index=nextTransit.first;transit=nextTransit
            J.transportState={};J.crossing=false;J.inStructure=nil
            if A.RouteRecovery then A.RouteRecovery.LegChanged() end
        end
    end
    if A.Flights and A.Flights.OnTaxi()==true and (not transit or transit.kind~='transport') then
        local p=point(position)
        for i=(J.legIndex or 1)+1,#plan.legs do
            local nextLeg=plan.legs[i]
            if nextLeg.kind=='transport' then
                local row=nextLeg.transport
                local near=p and A.TravelNetwork.Distance(p,row.board)
                if row.kind=='flight' and near and near<=120 then
                    J.legIndex=i;J.index=nextLeg.first;transit=nextLeg;J.transportState=nil
                    if A.RouteRecovery then A.RouteRecovery.LegChanged() end
                end
                break
            end
        end
        if not transit or transit.kind~='transport' then return nil,'Flying; walking guidance will resume after landing.' end
    end
    if transit and transit.kind=='transport' then
        J.transportState=J.transportState or {}
        local p=point(position)
        local aim,message,arrived=A.Transports.Guide(transit,p,J.transportState)
        J.transportMessage=message
        if arrived then
            J.legIndex=J.legIndex+1;J.index=J.Leg().first;J.transportState=nil;J.transportMessage=nil
            if transit.transport.arrivalCorridor then joinDockArrival(p,transit.transport.arrivalCorridor) end
            if A.RouteRecovery then A.RouteRecovery.LegChanged() end
            return J.Update(p,keepGuidance)
        end
        return aim,message
    end
    local p=J.RoutePosition(position)
    if not p then return nil,'Return to the route zone or replan from here' end
    J.ReleaseAccessStructure(p)
    if J.crossing then
        local leg=J.Leg()
        if leg.exitPath then
            advanceFloor(p,leg)
            return A.Structures.Aim(J.Current(),p.mapID)
        end
        return J.Current()
    end
    -- Masks constrain the planned geometry, not where the player may walk.
    -- Keep the established target while outside the mask; do not rebuild or
    -- discard the route because of a false-positive restriction underfoot.
    local portalGuidance=J.Leg() and (J.Leg().portalGuidance or J.Leg().cityGuidance)
    if portalGuidance and J.index==J.Leg().first then J.index=J.Leg().last end
    local outsideMask=portalGuidance or not A.Terrain.Segment(p,p)
    local target=J.Current()
    while target and distance(p,target)<=8 do
        local nextPoint=plan.points[J.index+1]
        local leg=J.Leg()
        if leg and J.index==leg.first then J.inStructure=nil end
        local nextLeg=leg and plan.legs[J.legIndex+1]
        if leg and J.index==leg.last and nextLeg and nextLeg.kind=='transport' then
            if nextLeg.transport.automaticTram then return target,'Walk through the '..nextLeg.transport.fromName..' tram portal.' end
            J.legIndex=J.legIndex+1;J.index=nextLeg.first;J.crossing=false;J.inStructure=nil;J.transportState={}
            if A.RouteRecovery then A.RouteRecovery.LegChanged() end
            return J.Update(p,keepGuidance)
        end
        if leg and J.index==leg.last and (leg.exitAim or leg.exitPath) then
            J.crossing=true;J.inStructure=leg.exitStructure;J.structureIndex=2
            return leg.exitPath and A.Structures.Aim(J.Current(),p.mapID) or leg.exitAim
        end
        if not nextPoint then
            if outsideMask or A.Terrain.Segment(p,target) then return nil,'arrived' end
            break
        end
        if not outsideMask and not A.Terrain.Segment(p,nextPoint) then break end
        J.index=J.index+1;target=J.Current()
    end
    if not target then return nil,'Route obstructed: replan or return to the route' end
    if not outsideMask and not A.Terrain.Segment(p,target) then
        if keepGuidance then return target,'Return to route' end
        return nil,'Route obstructed: replan or return to the route'
    end
    return target
end
function J.Pause() if J.active then J.paused=true;return true end end
function J.Resume(position)
    if J.Leg() and (J.Leg().kind=='transport' or (J.Leg().portalGuidance or J.Leg().cityGuidance) and not J.inStructure) then J.paused=false;return true end
    local p=J.RoutePosition(position);local target=J.Current()
    J.ReleaseAccessStructure(p)
    if J.Leg() and (J.Leg().cityGuidance or J.Leg().portalGuidance) and not J.inStructure then J.paused=false;return true end
    local structure=p and J.inStructure and A.Structures and A.Structures.Contains(p,J.inStructure)
    if structure then J.paused=false;return true end
    if not p or not target or p.mapID~=target.mapID or not structure and A.Terrain.Segment(p,p) and not A.Terrain.Segment(p,target) then return nil,'Replan from your current position before resuming.' end
    J.paused=false;return true
end
function J.Skip(position)
    if J.Leg() and J.Leg().kind=='transport' then return nil,'Finish the transport leg before skipping a route bend.' end
    if J.inStructure then return nil,'Finish the tunnel before skipping a route segment.' end
    local p=J.RoutePosition(position);local nextPoint=J.active and J.active.points[J.index+1]
    if not p or not nextPoint or p.mapID~=nextPoint.mapID or A.Terrain.Segment(p,p) and not A.Terrain.Segment(p,nextPoint) then return nil,'The next route segment cannot be skipped safely.' end
    J.index=J.index+1;return true
end
function J.ConfirmTransportArrival(position)
    local leg=J.Leg();local p=point(position)
    J.transportState=J.transportState or {}
    if not leg or leg.kind~='transport' or not A.Transports.CanDisembark(leg.transport,p,J.transportState,true) then
        return nil,'Disembark and reach the marked land approach before continuing.'
    end
    return true
end
function J.Remaining(position)
    if J.Leg() and J.Leg().kind=='transport' then
        local total=0;for i=J.legIndex+1,#J.active.legs do if J.active.legs[i].kind=='walk' then total=total+J.active.legs[i].distance end end
        return total
    end
    local p=J.RoutePosition(position);local target=J.Current()
    if not p or not target or target.mapID and p.mapID~=target.mapID then return 0 end
    local total=distance(p,target)
    local leg=J.Leg();local at=J.crossing and leg and leg.exitPath and leg.corridorStart+J.structureIndex-1 or J.index+(J.crossing and 1 or 0)
    for i=at,#J.active.points-1 do
        local a,b=J.active.points[i],J.active.points[i+1]
        if not a.transport and not b.transport and not b.breakBefore then total=total+distance(a,b) end
    end
    return total
end
