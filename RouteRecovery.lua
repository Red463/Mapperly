local _,A=...
local R={};A.RouteRecovery=R
local state={}
function R.Clear() state={} end
function R.LegChanged() state.join=nil;state.offSince=nil;state.lastCheck=nil end
function R.IsOffRoute() return state.offSince~=nil end
local function valid(n) return not (issecretvalue and issecretvalue(n)) and type(n)=='number' and n==n and math.abs(n)<math.huge end
local function clock()
    local ok,n=pcall(function() return GetTime() end)
    if ok and valid(n) then return n end
end
local function project(p,a,b,z)
    local dx,dy=(b.x-a.x)*z.widthYards,(b.y-a.y)*z.heightYards
    local px,py=(p.x-a.x)*z.widthYards,(p.y-a.y)*z.heightYards
    local length=dx*dx+dy*dy
    local t=length>0 and math.max(0,math.min(1,(px*dx+py*dy)/length)) or 0
    return math.sqrt((px-t*dx)^2+(py-t*dy)^2),{mapID=p.mapID,x=a.x+(b.x-a.x)*t,y=a.y+(b.y-a.y)*t}
end
function R.Update(p,now,canReplan)
    local J=A.Journey;local plan=J and J.active
    if J and J.ReleaseAccessStructure then J.ReleaseAccessStructure(p) end
    if A.Flights and A.Flights.OnTaxi()==true then state.join=nil;state.offSince=nil;return {} end
    if J and J.Leg() and (J.Leg().kind=='transport' or (J.Leg().portalGuidance or J.Leg().cityGuidance) and not J.inStructure) then state.join=nil;state.offSince=nil;return {} end
    if not plan or J.paused or type(p)~='table' or p.mapID~=J.MapID() or not valid(p.x) or not valid(p.y) or not A.ValidPin({map=p.mapID,x=p.x,y=p.y,name='Route position'}) then
        state.join=nil;state.offSince=nil;return {}
    end
    now=now or clock();if not valid(now) then return {} end
    if J.inStructure and A.Structures and A.Structures.Contains(p,J.inStructure) then state.join=nil;state.offSince=nil;return {} end
    if state.plan~=plan or state.lastCheck and now<state.lastCheck then
        state={plan=plan,lastAttempt=state.lastCheck and now>=state.lastCheck and state.lastAttempt or nil}
    end
    if state.lastCheck and now-state.lastCheck<.5 then return {} end
    state.lastCheck=now
    if not A.Terrain.Segment(p,p) then state.join=nil;state.offSince=nil;return {} end
    if J.inStructure then
        -- Native floor targets use world coordinates and may lie under blocked
        -- root terrain. Only request recovery after leaving the corridor onto
        -- permitted outdoor ground; ordinary leg projection cannot handle them.
        state.join=nil;state.offSince=state.offSince or now
        if canReplan~=false and now-state.offSince>=3 and (not state.lastAttempt or now-state.lastAttempt>=10) then
            state.lastAttempt=now;return {replan=true}
        end
        return {}
    end
    local z=A.Terrain.Zone(J.MapID());local index=J.index
    local first,last=J.Bounds()
    if not z or not index or not plan.points[index] or #plan.points>2049 then return {} end
    local current,nearest=project(p,J.crossing and plan.points[index] or plan.points[math.max(first,index-1)],J.crossing and J.Current() or plan.points[index],z)
    local minimum=current;local best;local nearby={}
    for i=index+1,last do
        local d,q=project(p,plan.points[i-1],plan.points[i],z)
        if d<minimum then minimum=d;nearest=q end
        if d<=12 then
            local candidate={index=i,d=d,point=q};nearby[#nearby+1]=candidate
            if not best or d<best.d then best=candidate end
        end
    end
    local ambiguous=false
    if best then
        local first,last=best.index,best.index
        for _,candidate in ipairs(nearby) do if candidate.d<=best.d+4 then first=math.min(first,candidate.index);last=math.max(last,candidate.index) end end
        ambiguous=last-first>1
        if last-first==1 then
            -- Adjacency is only unambiguous near the common vertex. Farther
            -- away, a hairpin can put two different legs alongside each other.
            local shared=plan.points[first]
            ambiguous=project(p,shared,shared,z)>12
        end
    end
    if current>18 and best and not ambiguous and A.Terrain.Segment(p,best.point) and A.Terrain.Segment(p,plan.points[best.index]) then
        if not state.join or best.index<state.join.index or best.index>state.join.index+1 then
            state.join={index=best.index,since=now}
        else state.join.index=best.index end
        if now-state.join.since>=2 then
            J.index=best.index;state.join=nil;state.offSince=nil
            return {rejoined=true}
        end
    else state.join=nil end
    local off=minimum>30 or not A.Terrain.Segment(p,nearest)
    if not off then
        state.offSince=nil
        return {onRoute=current<=12 and A.Terrain.Segment(p,plan.points[index])}
    end
    state.offSince=state.offSince or now
    if canReplan~=false and now-state.offSince>=3 and (not state.lastAttempt or now-state.lastAttempt>=10) then
        state.lastAttempt=now;return {replan=true}
    end
    return {}
end
