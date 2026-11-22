local _,A=...
local J={};A.Journey=J
local function point(p)
    if type(p)~='table' then return end
    local map=p.mapID or p.map
    for _,v in ipairs({map,p.x,p.y}) do if issecretvalue and issecretvalue(v) then return end end
    if not A.ValidPin({map=map,x=p.x,y=p.y,name=p.name or 'Walking point'}) then return end
    return {mapID=map,x=p.x,y=p.y}
end
local function endpoints(start,goal)
    local a,b=point(start),point(goal)
    if not a or not b then return nil,'Invalid walking route coordinates.' end
    if a.mapID~=b.mapID then return nil,'Cross-zone walking journeys are not available in this preview.' end
    local zone=A.Terrain.Zone(a.mapID)
    if not zone then return nil,'Terrain coverage is unavailable for this map.' end
    if not A.Terrain.Segment(a,a) or not A.Terrain.Segment(b,b) then return nil,'The start or destination is blocked or outside known terrain.' end
    return a,b,zone
end
function J.Plan(start,goal,options)
    local a,b,zone=endpoints(start,goal)
    if not a then return nil,b end
    local points,distance=A.Terrain.Path(a,b,{maxExpansions=262144})
    if not points then
        return nil,distance=='budget' and 'Route search reached its limit. Try a closer waypoint.' or 'No walking connection was found through the available terrain.'
    end
    local speed=options and options.speed or 7
    if type(speed)~='number' or speed<=0 then speed=7 end
    return {kind='walking',points=points,distance=distance,estimatedSeconds=distance/speed,
        mapID=a.mapID,name=goal.name or 'Destination',coverage=zone.status,
        legs={{kind='walk',name='Walk to '..(goal.name or 'destination'),points=points,distance=distance,estimatedSeconds=distance/speed}}}
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
function J.Request(candidate,done,failed)
    local start,reason=J.PlayerPosition()
    if not start then return nil,reason end
    local a,b=endpoints(start,candidate)
    if not a then return nil,b end
    A.PlanningJob.Start(function() return J.Plan(start,candidate,{}) end,done,failed)
    return true
end
function J.Install(plan)
    J.active=plan;J.index=math.min(2,#plan.points);J.paused=false
end
function J.Clear() J.active=nil;J.index=nil;J.paused=false end
function J.Current() return J.active and J.active.points[J.index] end
local function distance(a,b)
    local z=A.Terrain.Zone(a.mapID)
    return math.sqrt(((a.x-b.x)*z.widthYards)^2+((a.y-b.y)*z.heightYards)^2)
end
function J.Update(position)
    local plan=J.active;if not plan then return nil,'No walking journey' end
    if J.paused then return nil,'Paused' end
    local p=point(position)
    if not p or p.mapID~=plan.mapID then return nil,'Return to the route zone' end
    -- Masks constrain the planned geometry, not where the player may walk.
    -- Keep the established target while outside the mask; do not rebuild or
    -- discard the route because of a false-positive restriction underfoot.
    local outsideMask=not A.Terrain.Segment(p,p)
    local target=J.Current()
    while target and distance(p,target)<=8 do
        local nextPoint=plan.points[J.index+1]
        if not nextPoint then
            if outsideMask or A.Terrain.Segment(p,target) then return nil,'arrived' end
            break
        end
        if not outsideMask and not A.Terrain.Segment(p,nextPoint) then break end
        J.index=J.index+1;target=J.Current()
    end
    if not target or not outsideMask and not A.Terrain.Segment(p,target) then return nil,'Route obstructed: replan or return to the route' end
    return target
end
function J.Pause() if J.active then J.paused=true;return true end end
function J.Resume(position)
    local p=point(position);local target=J.Current()
    if not p or not target or p.mapID~=target.mapID or A.Terrain.Segment(p,p) and not A.Terrain.Segment(p,target) then return nil,'Replan from your current position before resuming.' end
    J.paused=false;return true
end
function J.Skip(position)
    local p=point(position);local nextPoint=J.active and J.active.points[J.index+1]
    if not p or not nextPoint or p.mapID~=nextPoint.mapID or A.Terrain.Segment(p,p) and not A.Terrain.Segment(p,nextPoint) then return nil,'The next route segment cannot be skipped safely.' end
    J.index=J.index+1;return true
end
function J.Remaining(position)
    local p=point(position);local target=J.Current()
    if not p or not target or p.mapID~=target.mapID then return 0 end
    local total=distance(p,target)
    for i=J.index,#J.active.points-1 do total=total+distance(J.active.points[i],J.active.points[i+1]) end
    return total
end
