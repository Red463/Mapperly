local _,A=...
local P={};A.TravelNetwork=P
local function data() local d=A.CrossingData;return type(d)=='table' and d.version==1 and d end
function P.Canonical(map)
    local d=data();return d and d.aliases and d.aliases[map] or map
end
function P.World(p)
    if type(p.worldX)=='number' and type(p.worldY)=='number' and type(p.instance)=='number' then return p.worldX,p.worldY,p.instance end
    local d=data();local m=d and d.maps and d.maps[p.mapID]
    if not m then return end
    return m.west-p.x*m.width,m.north-p.y*m.height,m.instance
end
function P.Transform(p,map)
    local x,y,instance=P.World(p);local d=data();local m=d and d.maps and d.maps[map]
    if not m or not x or instance~=m.instance then return end
    local q={mapID=map,x=(m.west-x)/m.width,y=(m.north-y)/m.height}
    if A.ValidPin({map=map,x=q.x,y=q.y,name='Crossing'}) then return q end
end
function P.Distance(a,b)
    if a.mapID and a.mapID==b.mapID then
        local z=A.Terrain.Zone(a.mapID);if not z then return end
        return math.sqrt(((a.x-b.x)*z.widthYards)^2+((a.y-b.y)*z.heightYards)^2)
    end
    local ax,ay,ai=P.World(a);local bx,by,bi=P.World(b)
    if ax and bx and ai==bi then return math.sqrt((ax-bx)^2+(ay-by)^2) end
end
-- Separate pieces of permitted ground need a structure or another network
-- connection. Region numbers are local to a map; zero denotes blocked ground.
function P.SeparateGround(a,b)
    if a.mapID~=b.mapID or not A.WalkingRegions then return false end
    local first,last=A.WalkingRegions.Get(a),A.WalkingRegions.Get(b)
    return first and last and first>0 and last>0 and first~=last or false
end
function P.CanImproveWithStructure(a,b,limit,points)
    local d=data();if not d then return false end
    if not points or #points<2 then return false end
    local route={};local walked=0
    for i,p in ipairs(points) do
        local x,y,instance=P.World(p);if not x then return false end
        if i>1 then local previous=route[i-1];walked=walked+math.sqrt((x-previous.x)^2+(y-previous.y)^2) end
        route[i]={x=x,y=y,walked=walked}
    end
    local function nearest(q)
        local x,y=P.World(q);local best,arc=math.huge,0
        for i=2,#route do
            local first,last=route[i-1],route[i];local dx,dy=last.x-first.x,last.y-first.y;local length=dx*dx+dy*dy
            local t=length>0 and math.max(0,math.min(1,((x-first.x)*dx+(y-first.y)*dy)/length)) or 0
            local distance=math.sqrt((x-first.x-t*dx)^2+(y-first.y-t*dy)^2)
            if distance<best then best=distance;arc=first.walked+t*math.sqrt(length) end
        end
        return best,arc
    end
    for _,e in ipairs(d.edges or {}) do if e.structure and A.Structures and A.Structures.Get(e) then
        for direction=1,2 do
            local first,last=direction==1 and e.a or e.b,direction==1 and e.b or e.a
            if first.mapID==a.mapID and last.mapID==b.mapID then
                local lower=(P.Distance(a,first) or math.huge)+e.distance+(P.Distance(last,b) or math.huge)
                if lower<limit-.0001 then
                    local firstDistance,firstArc=nearest(first);local lastDistance,lastArc=nearest(last)
                    -- A loose endpoint bearing mistakes road meanders for a
                    -- bridge detour. Require a potential shortcut of the actual
                    -- established route before launching a network search.
                    if lastArc>firstArc and lastArc-firstArc>firstDistance+e.distance+lastDistance+.001 then return true end
                end
            end
        end
    end end
    return false
end
function P.CanImproveWithTransport(a,b,edges,speed,limit)
    -- Relax walking to straight lines, ignoring barriers and road penalties.
    -- This can underestimate a transport journey, never rule out a winner.
    -- Include combinations of vehicles rather than testing each in isolation.
    local function world(p)
        if type(p)~='table' then return end
        local x,y,i=P.World(p)
        local function valid(v) return type(v)=='number' and v==v and math.abs(v)<math.huge end
        if valid(x) and valid(y) and valid(i) then return {x,y,i} end
    end
    local origin,goal=world(a),world(b)
    if not origin or not goal or type(speed)~='number' or speed<=0 or speed~=speed or speed==math.huge or type(limit)~='number' or limit~=limit then return true end
    local links={}
    for _,e in ipairs(edges) do
        local from,to=world(e.from),world(e.to)
        if not from or not to or type(e.seconds)~='number' or e.seconds~=e.seconds or e.seconds<0 then return true end
        links[#links+1]={from=from,to=to,cost=e.seconds*speed}
    end
    local function distance(p,q)
        if p[3]~=q[3] then return math.huge end
        return math.sqrt((p[1]-q[1])^2+(p[2]-q[2])^2)
    end
    local scores,closed={[0]=0},{};local work=0
    for _=0,#links do
        local at,best
        for i,g in pairs(scores) do if not closed[i] and g<limit and (not best or g<best) then at,best=i,g end end
        if not at then return false end
        closed[at]=true
        local p=at==0 and origin or links[at].to
        if at~=0 and best+distance(p,goal)<limit then return true end
        for i,e in ipairs(links) do
            if not closed[i] then
                local cost=best+distance(p,e.from)+e.cost
                if cost<limit and (not scores[i] or cost<scores[i]) then scores[i]=cost end
            end
            work=work+1
            if work%256==0 and A.Terrain.Checkpoint then A.Terrain.Checkpoint() end
        end
    end
    return false
end
local function validEdge(edge)
    local a,b=edge.a,edge.b
    if not A.ValidPin({map=a.mapID,x=a.x,y=a.y,name='Crossing'}) or not A.ValidPin({map=b.mapID,x=b.x,y=b.y,name='Crossing'}) then return end
    local ab,ba=P.Transform(a,b.mapID),P.Transform(b,a.mapID)
    local length=P.Distance(a,b)
    if edge.structure then
        local row=A.Structures and A.Structures.Get(edge)
        if row and length and length<=row.distance+.001 then return row.distance end
        return
    end
    if not ab or not ba or not length or length>120.001 then return end
    if A.Terrain.Segment(a,ba) and A.Terrain.Segment(ab,b) then return length end
end
local function assemble(last,a,b,options)
    if A.PlanningJob then A.PlanningJob.Report('Finishing journey') end
    local chain={};local cursor=last
    while cursor.previous do table.insert(chain,1,cursor);cursor=cursor.previous end
    local d=data();local plan={kind='walking',multiZone=true,mapID=a.mapID,destinationMapID=b.mapID,
        name=options.name or 'Destination',distance=last.g,estimatedSeconds=last.g/options.speed,coverage='complete',points={},legs={}}
    for _,step in ipairs(chain) do
        local points=step.walk;local map=points[1].mapID
        local legLength=step.length+(step.bridge and step.bridge.distance or 0)
        local leg={kind='walk',mapID=map,points=points,distance=legLength,estimatedSeconds=legLength/options.speed,
            name=points.portalInstruction or points.cityInstruction or 'Walk through '..d.maps[map].name,first=#plan.points+1,portalGuidance=points.portalGuidance,cityGuidance=points.cityGuidance}
        if points.portalGuidance then plan.hasPortalGuidance=true end
        if points.cityGuidance then plan.hasCityGuidance=true;plan.coverage='city guidance' end
        for _,p in ipairs(points) do plan.points[#plan.points+1]=p end
        leg.last=#plan.points
        if step.bridge and step.bridge.transport then
            plan.hasTransports=true
        elseif step.bridge then
            leg.exitAim=P.Transform(step.bridge.to,map);leg.exitDistance=step.bridge.distance;leg.exitStructure=step.bridge.structure
            if step.bridge.structure then
                leg.exitPath=step.bridge.path or A.Structures.Path(step.bridge.structure,step.bridge.from)
                leg.corridorStart=leg.last
                for i=2,#leg.exitPath-1 do plan.points[#plan.points+1]=leg.exitPath[i] end
            end
        end
        if A.Terrain.Zone(map).status=='partial' then plan.coverage='partial' end
        if not (step.bridge and step.bridge.boardingOverride and step.length==0) then plan.legs[#plan.legs+1]=leg end
        if step.bridge and step.bridge.transport then
            local row=step.bridge.transport
            if row.automaticTram then leg.name='Walk through the '..row.fromName..' tram portal' end
            leg.distance=step.length;leg.estimatedSeconds=step.length/options.speed
            local method=({flight='Flight',boat='Boat',zeppelin='Zeppelin',airship='Airship',tram='Tram',lift='Lift'})[row.kind] or 'Transport'
            local transit={kind='transport',name=method..': '..row.name,
                mapID=row.a.mapID,transport=row,first=#plan.points+1,distance=0,estimatedSeconds=row.planningSeconds,points={}}
            local path=row.kind=='flight' and A.Flights.Path(row) or row.path
            if not path or #path<2 then path={row.board,row.arrival} end
            for i,p in ipairs(path) do
                local q={worldX=p.worldX,worldY=p.worldY,instance=p.instance,transport=true,breakBefore=i==1 or p.breakBefore or row.kind~='flight' and (not row.path or #row.path<2)}
                plan.points[#plan.points+1]=q;transit.points[#transit.points+1]=q
            end
            transit.last=#plan.points;plan.legs[#plan.legs+1]=transit
            if row.kind=='flight' then
                plan.flightCost=(plan.flightCost or 0)+(row.fare or 0)
                plan.flightCostEstimated=plan.flightCostEstimated or row.fareEstimated
                plan.flightCostUnknown=plan.flightCostUnknown or row.fare==nil
            end
        end
    end
    if plan.hasTransports then
        local i=1
        while i+2<=#plan.legs do
            local first,walk,last=plan.legs[i],plan.legs[i+1],plan.legs[i+2]
            local a,b=first.transport,last.transport
            if a and b and a.pathID and a.pathID==b.pathID and a.toNodeID==b.fromNodeID and walk.kind=='walk' and walk.distance<.01 then
                local row={};for k,v in pairs(a) do row[k]=v end
                row.b=b.b;row.arrival=b.arrival;row.toName=b.toName;row.toNodeID=b.toNodeID
                row.arrivalGroundHeight=b.arrivalGroundHeight
                row.arrivalAccess=b.arrivalAccess
                row.planningSeconds=a.planningSeconds+b.planningSeconds-math.max(0,(b.waitAssumptionSeconds or 0)-(b.originDwellSeconds or 0))
                row.name=(a.fromName or 'Departure')..' to '..(b.toName or 'destination')..' (stay aboard at '..(a.toName or 'intermediate stop')..')'
                first.transport=row;first.name='Stay aboard: '..row.name;first.last=last.last;first.estimatedSeconds=row.planningSeconds
                table.remove(plan.legs,i+1);table.remove(plan.legs,i+1)
            else i=i+1 end
        end
        plan.distance=0;plan.estimatedSeconds=0
        for i,leg in ipairs(plan.legs) do
            plan.estimatedSeconds=plan.estimatedSeconds+leg.estimatedSeconds
            if leg.kind=='walk' then
                plan.distance=plan.distance+leg.distance
                if i>1 and plan.legs[i-1].kind=='transport' then
                    local p=plan.points[leg.first];plan.points[leg.first]={mapID=p.mapID,x=p.x,y=p.y,breakBefore=true}
                end
            end
        end
    end
    return plan
end
-- A map-to-map crossing can end on an isolated piece of the destination
-- map. Treat all points in the same known ground region as connected and
-- include each authorized crossing or vehicle in its allowed direction.
-- Unknown terrain makes the proof inconclusive.
local function regionNetworkConnected(graph, start, goal, transports, options)
    if not A.WalkingRegions or type(A.WalkingRegions.Get)~='function' then return end
    local known, links = {}, {}
    local specialAccess={}
    for _,edge in ipairs(transports) do
        local row=edge.transport
        if row then
            -- Exact dock floors and tram bearings can bypass outdoor terrain.
            -- Allow all local joins on their respective sides in this proof.
            if row.automaticTram or row.boardingCorridor then specialAccess[edge.from.mapID]=true end
            if row.automaticTram or row.arrivalCorridor then specialAccess[edge.to.mapID]=true end
        end
    end
    local function link(from,to)
        links[from]=links[from] or {}
        links[from][to]=true
    end
    local sampled = 0
    local function key(p)
        if known[p] then return known[p] end
        local region = A.WalkingRegions.Get(p)
        if type(region)~='number' or region<=0 or region%1~=0 then return end
        local value = p.mapID..':'..region
        if specialAccess[p.mapID] or A.CityNavigation and A.CityNavigation.Supports(p,options) then
            local interior=p.mapID..':access'
            link(value,interior);link(interior,value)
        end
        known[p]=value
        sampled=sampled+1
        if sampled%32==0 and A.Terrain.Checkpoint then A.Terrain.Checkpoint() end
        return value
    end
    local first,last=key(start),key(goal)
    if not first or not last then return end
    for _,rows in pairs(graph) do
        for _,edge in ipairs(rows) do
            local from,to=key(edge.from),key(edge.to)
            if not from or not to then return end
            link(from,to)
        end
    end
    local reached,queue = {[first]=true},{first}
    local index=1
    while index<=#queue do
        local at=queue[index]
        if at==last then return true end
        for target in pairs(links[at] or {}) do
            if not reached[target] then
                reached[target]=true
                queue[#queue+1]=target
            end
        end
        if index%32==0 and A.Terrain.Checkpoint then A.Terrain.Checkpoint() end
        index=index+1
    end
    return false
end
function P.Plan(a,b,options)
    options=options or {};options.speed=options.speed or 7
    options.start=a
    if type(options.speed)~='number' or options.speed~=options.speed or options.speed<=0 or options.speed==math.huge then options.speed=7 end
    local d=data();local _,_,ai=P.World(a);local _,_,bi=P.World(b)
    local transports=not options.walkingOnly and A.Transports and A.Transports.Edges(options) or {}
    local mixed=#transports>0
    local minimum=mixed and A.Transports.MinimumSeconds(transports)*options.speed or math.huge
    if not d or ai==nil or bi==nil or ai~=bi and not mixed then return nil,'No verified walking network connects these maps.' end
    if A.PlanningJob then
        local flights,sources=0,{}
        for _,e in ipairs(transports) do if e.transport and e.transport.kind=='flight' then
            flights=flights+1
            sources[e.transport.fromNodeID or e.from]=true
        end end
        local count=0;for _ in pairs(sources) do count=count+1 end
        local note
        if options.walkingOnly then note='Walking-only search; flights and other vehicles are excluded.'
        elseif A.db and A.db.useFlights==false then note='Flight paths are disabled in Navigation settings.'
        elseif flights==0 and A.Flights and type(A.Flights.Stats)=='function' then
            local _,recorded=A.Flights.Stats()
            note=recorded==0 and 'No outbound flights recorded. Open departure flight masters.' or 'No eligible recorded flights. Check availability and fares.'
        end
        A.PlanningJob.Report('Checking travel options',{flightRoutes=flights,flightSources=count,flightNote=note})
    end
    local bound=A.TravelBounds and A.TravelBounds.Build(b,transports,options.speed)
    local function heuristic(p) return bound and bound(p) or math.min(P.Distance(p,b) or 0,minimum) end
    local graph={}
    for i,e in ipairs(d.edges or {}) do
        if A.PlanningJob then A.PlanningJob.Report('Checking zone connections',{checked=i,total=#d.edges}) end
        local length=validEdge(e)
        if length then
            local floor=e.structure and A.Structures.Get(e)
            local deferBridge=floor and floor.endpointAccess and e.a.mapID==e.b.mapID
            -- A bridge joining separate ground regions can be the only way
            -- to reach a zone exit. Compare it before accepting a vehicle detour.
            if deferBridge and P.SeparateGround(e.a,e.b) then
                deferBridge=false
            end
            for direction=1,2 do
                local from,to=direction==1 and e.a or e.b,direction==1 and e.b or e.a
                graph[from.mapID]=graph[from.mapID] or {}
                table.insert(graph[from.mapID],{key=i..':'..direction,from=from,to=to,distance=length,structure=e.structure,
                    deferBridge=deferBridge})
            end
        end
        if i%16==0 and A.Terrain.Checkpoint then A.Terrain.Checkpoint() end
    end
    for _,e in ipairs(transports) do graph[e.from.mapID]=graph[e.from.mapID] or {};table.insert(graph[e.from.mapID],e) end
    local startAccess=A.Structures and A.Structures.Access(a,options.liveStart)
    local goalAccess=A.Structures and A.Structures.Access(b,false)
    local function addAccess(rows,p,reverse)
        for i,row in ipairs(rows or {}) do
            if row.distance>.000001 then
            local from,to=reverse and row.landing or p,reverse and p or row.landing
            local path=row.path
            if reverse then path={};for k=#row.path,1,-1 do path[#path+1]=row.path[k] end end
            graph[from.mapID]=graph[from.mapID] or {}
            table.insert(graph[from.mapID],{key=(reverse and 'deck-goal:' or 'deck-start:')..i,from=from,to=to,distance=row.distance,structure=row.structure,path=path})
            end
        end
    end
    addAccess(startAccess,a,false);addAccess(goalAccess,b,true)
    if startAccess and goalAccess then
        local path,length,id=A.Structures.Between(startAccess,goalAccess)
        if path then
            table.insert(graph[a.mapID],{key='deck-direct',from=a,to=b,distance=length,structure=id,path=path})
        end
    end
    local connected={[a.mapID]=true};local queue={a.mapID};local cursor=1
    while cursor<=#queue do
        for _,e in ipairs(graph[queue[cursor]] or {}) do if not connected[e.to.mapID] then connected[e.to.mapID]=true;queue[#queue+1]=e.to.mapID end end
        cursor=cursor+1
    end
    if not connected[b.mapID] then return nil,'No verified outdoor walking crossings connect these zones yet.' end
    local incoming={}
    for map,rows in pairs(graph) do for _,e in ipairs(rows) do incoming[e.to.mapID]=incoming[e.to.mapID] or {};incoming[e.to.mapID][map]=true end end
    local hops={[b.mapID]=0};local reverseQueue={b.mapID};local nextMap=1
    while nextMap<=#reverseQueue do
        local map=reverseQueue[nextMap]
        for source in pairs(incoming[map] or {}) do if hops[source]==nil then hops[source]=hops[map]+1;reverseQueue[#reverseQueue+1]=source end end
        nextMap=nextMap+1
    end
    if (hops[a.mapID] or 0)>=3 and not startAccess and not goalAccess then
        if A.PlanningJob then A.PlanningJob.Report('Checking reachable connections') end
        if regionNetworkConnected(graph,a,b,transports,options)==false then
            if options.walkingOnly then return nil,'No verified walking network connects the start and destination ground regions.' end
            return nil,'No verified route connects these areas with your current travel settings.'
        end
    end
    local budget=A.Flights and A.Flights.Money()
    local function fare(edge) local row=edge.transport;return row and row.kind=='flight' and row.fare or 0 end
    local initial={key='start',p=a,g=0,f=heuristic(a),fare=0}
    local frontier={initial};local scores={start=0};local closed={};local work=0;local limited=false
    local paths={};local spent,calls=0,0
    local cellBudget=math.max(0,math.min(2000000,options.maxWalkingCells or 2000000))
    local probing,deferredProbes=false,false;local probeSpent,probeCalls=0,0
    local probeBudget=math.min(262144,math.floor(cellBudget/4))
    local function portalPath(from,to,allowed)
        if allowed==false then return end
        if A.CityNavigation then
            local points,length=A.CityNavigation.Path(from,to,options);if points then return points,length end
        end
        if A.Trams then return A.Trams.Access(from,to,transports,allowed) end
    end
    local function groundPath(from,to,allowPortal)
        if (startAccess and from==a or goalAccess and to==b) and from.mapID==to.mapID and math.abs(from.x-to.x)<1e-10 and math.abs(from.y-to.y)<1e-10 then return {from},0 end
        if from==a and to==b and startAccess and goalAccess and startAccess.structure==goalAccess.structure then return nil,'Use the certified bridge deck' end
        if from==a and A.Flights and A.Flights.ContextValid(options.boardingContext,a) and from.mapID==to.mapID and math.abs(from.x-to.x)<1e-8 and math.abs(from.y-to.y)<1e-8 then return {from},0 end
        if options.candidatePoints and from==a and to==b then return options.candidatePoints,options.candidateDistance end
        if A.WalkingRegions then
            local first,last=A.WalkingRegions.Get(from),A.WalkingRegions.Get(to)
            if first and last and first~=last then
                local access,length=portalPath(from,to,allowPortal);if access then return access,length end
                return nil,'disconnected ground regions'
            end
        end
        local key=string.format('%d:%.17g,%.17g:%.17g,%.17g',from.mapID,from.x,from.y,to.x,to.y)..(allowPortal==false and ':strict' or ':portal')
        local allowance=math.min(262144,cellBudget-spent,probing and math.min(16384,probeBudget-probeSpent) or math.huge)
        local known=paths[key]
        if known and (known[1] or known[2]~='budget' or allowance<=(known.allowance or 0)) then return known[1],known[2] end
        if calls>=128 or allowance<=0 or probing and probeCalls>=32 then
            local access,length=portalPath(from,to,allowPortal);if access then return access,length end
            if not probing then limited=true end;return nil,'budget'
        end
        calls=calls+1;if probing then probeCalls=probeCalls+1 end;local previous=0
        if A.Terrain.Checkpoint then A.Terrain.Checkpoint() end
        local points,length=A.Terrain.Path(from,to,{maxExpansions=allowance,preferRoads=options.preferRoads,roadPreferenceStrength=options.roadPreferenceStrength,yield=function(count)
            local used=count-previous;spent=spent+used;if probing then probeSpent=probeSpent+used end;previous=count
            if A.Terrain.Checkpoint then A.Terrain.Checkpoint() end
        end})
        if not points then
            local access,accessLength=portalPath(from,to,allowPortal)
            if access then points,length=access,accessLength end
        end
        if not points and length=='budget' then
            if probing then deferredProbes=true else limited=true end
        end
        paths[key]={points,length,allowance=allowance}
        return points,length
    end
    -- Dock handoffs must follow their proven static floor, rather than a
    -- shorter terrain/swimming chord underneath the pier. Keep the access
    -- constraint separate from the optional preference for ordinary roads.
    local dockStarts,dockEnds={},{}
    local function pointKey(p) return string.format('%d:%.17g:%.17g',p.mapID,p.x,p.y) end
    if A.HarbourAccessData and A.TransportData and A.Structures and
        A.HarbourAccessData.proofSha256==A.TransportData.harbourProofSha256 then
        for _,edge in ipairs(transports) do
            local row=edge.transport
            if row.boardingCorridor and A.Transports.DockCorridor(row.boardingCorridor) then dockEnds[pointKey(row.a)]=row.boardingCorridor end
            if row.arrivalCorridor and A.Transports.DockCorridor(row.arrivalCorridor) then dockStarts[pointKey(row.b)]=row.arrivalCorridor end
        end
    end
    local function floorTail(id,p)
        local row=A.HarbourAccessData.corridors[id]
        local path=row and A.Structures.Path(id,row.a)
        if not path then return end
        local best,bestDistance
        local x,y=P.World(p)
        for i=2,#path do
            local a,b=path[i-1],path[i];local dx,dy=b.worldX-a.worldX,b.worldY-a.worldY
            local length=dx*dx+dy*dy
            local t=length>0 and math.max(0,math.min(1,((x-a.worldX)*dx+(y-a.worldY)*dy)/length)) or 0
            local distance=(x-a.worldX-t*dx)^2+(y-a.worldY-t*dy)^2
            if distance<=6.25 and (not bestDistance or distance<bestDistance) then best=i;bestDistance=distance end
        end
        local result={}
        if best then result[1]=p else best=1 end
        for i=best,#path do result[#result+1]=P.Transform(path[i],row.a.mapID) end
        return result,bestDistance~=nil
    end
    local function localPath(from,to)
        if from.mapID==to.mapID and math.abs(from.x-to.x)<1e-10 and math.abs(from.y-to.y)<1e-10 then return groundPath(from,to) end
        local firstID,lastID=dockStarts[pointKey(from)],dockEnds[pointKey(to)]
        if not firstID and not lastID then return groundPath(from,to) end
        local function measured(points)
            local length=0;for i=2,#points do length=length+(P.Distance(points[i-1],points[i]) or 0) end
            return points,length
        end
        local prefix,suffix
        if lastID then
            local tail,onFloor=floorTail(lastID,from)
            if onFloor then return measured(tail)
            else suffix=tail;to=A.HarbourAccessData.corridors[lastID].a end
        end
        if firstID then
            local tail,onFloor=floorTail(firstID,to)
            prefix={}
            for i=#tail,1,-1 do prefix[#prefix+1]=tail[i] end
            if onFloor then return measured(prefix) else from=A.HarbourAccessData.corridors[firstID].a end
        end
        local middle,why=groundPath(from,to,false)
        if not middle then return nil,why end
        local result={}
        for _,part in ipairs({prefix or {},middle,suffix or {}}) do
            for _,p in ipairs(part) do
                if #result==0 or (P.Distance(result[#result],p) or math.huge)>.000001 then result[#result+1]=p end
            end
        end
        return measured(result)
    end
    -- Adjacent zones normally need only one verified crossing. Try their
    -- nearest direct connectors first instead of exploring unrelated regions.
    -- This prefers a feasible direct-zone journey, not a global time optimum.
    local direct={}
    for _,e in ipairs(graph[a.mapID] or {}) do if e.to.mapID==b.mapID then direct[#direct+1]=e end end
    local function cost(e) return e.seconds and e.seconds*options.speed or e.distance end
    table.sort(direct,function(x,y) return (P.Distance(a,x.from) or 0)+cost(x)+(P.Distance(x.to,b) or 0)<(P.Distance(a,y.from) or 0)+cost(y)+(P.Distance(y.to,b) or 0) end)
    local bestGoal
    if options.candidatePoints then bestGoal={previous=initial,walk=options.candidatePoints,length=options.candidateDistance,g=options.candidateDistance,f=options.candidateDistance,key='goal'} end
    -- Preserve the quick adjacent-zone case for walking-only graphs. Mixed
    -- journeys must prioritize complete itineraries before expensive paths.
    for _,e in ipairs(not mixed and direct or {}) do if not budget or fare(e)<=budget then
        local first,one=localPath(a,e.from)
        if first then
            local last,two=localPath(e.to,b)
            if last then
                local arrival={previous=initial,walk=first,length=one,bridge=e,g=one+cost(e),fare=fare(e)}
                local candidate={previous=arrival,walk=last,length=two,g=arrival.g+two,f=arrival.g+two,key='goal',fare=fare(e)}
                if not mixed and (not bestGoal or candidate.g<bestGoal.g) or mixed and candidate.g<=minimum then return assemble(candidate,a,b,options) end
                if not bestGoal or candidate.g<bestGoal.g then bestGoal=candidate end
            end
        end
    end end
    -- Search complete itineraries using lower bounds for their walking joins.
    -- Probe joins on promising complete candidates with a small shared slice.
    -- Defer exhausted probes temporarily, so an inexpensive good itinerary
    -- can finish before an unrelated long detour spends the whole allowance.
    -- A long journey may finish within 5% of the cheapest complete estimate
    -- in the current phase. Short trips still compare at full precision.
    -- Exhausted probes permit a 20% margin; otherwise restore them and retry.
    -- The established graph search remains the bounded fallback.
    local joins={};local itineraryWork=0
    local function knownJoin(from,to) return joins[from] and joins[from][to] end
    local joinRegions={}
    local function region(p)
        local id=joinRegions[p]
        if id==nil then id=A.WalkingRegions.Get(p) or false;joinRegions[p]=id end
        return id
    end
    -- Ranking a multi-zone itinerary can otherwise keep choosing a different
    -- impossible approach to the same crossing. Consult the same ground
    -- regions used by localPath before spending a terrain search on its prefix.
    local filterRegions=(hops[a.mapID] or 0)>=3 and A.WalkingRegions
    local function impossibleJoin(from,to)
        local first,last=region(from),region(to)
        if not first or not last or first<=0 or last<=0 or first==last then return false end
        if options.candidatePoints and from==a and to==b then return false end
        if dockStarts[pointKey(from)] or dockEnds[pointKey(to)] then return false end
        return not portalPath(from,to)
    end
    local function eligible(e,p,phase)
        return (phase==2 or options.candidatePoints or not e.deferBridge or startAccess and startAccess.structure==e.structure or goalAccess and goalAccess.structure==e.structure) and
            (phase==2 or mixed or e.structure or hops[e.to.mapID] and hops[p.mapID] and hops[e.to.mapID]<hops[p.mapID])
    end
    -- Many routes share a flight master or crossing. Its remaining travel
    -- estimate is independent of the path taken to reach it and of the fare.
    local remaining={}
    local function remainingCost(edge)
        if not edge or ai==bi or not bound then return 0 end
        local p=edge.to
        if remaining[p]==nil then remaining[p]=bound(p) or 0 end
        return remaining[p]
    end
    local function optimisticItinerary(phase,includeDeferred)
        local open={initial};local costs={start=0};local done={};local labels={};local expanded=0
        if bestGoal then open[#open+1]=bestGoal;costs.goal=bestGoal.g end
        local function add(parent,to,edge)
            local known=knownJoin(parent.p,to)
            if not known and filterRegions and impossibleJoin(parent.p,to) then return end
            if known and not known.path then
                if not known.deferred or not includeDeferred then return end
                known=nil
            end
            local length=known and known.length or P.Distance(parent.p,to) or 0
            local g=parent.g+length+(edge and cost(edge) or 0)
            local nextFare=(parent.fare or 0)+(edge and fare(edge) or 0)
            local key=edge and (budget and edge.key..':fare:'..nextFare or edge.key) or 'goal'
            if budget and nextFare>budget or done[key] or costs[key] and g>=costs[key] or costs.goal and g>=costs.goal then return end
            if budget and edge then
                local rows=labels[edge.key] or {}
                for _,label in ipairs(rows) do if label.g<=g and label.fare<=nextFare then return end end
                for i=#rows,1,-1 do if g<=rows[i].g and nextFare<=rows[i].fare then table.remove(rows,i) end end
                rows[#rows+1]={g=g,fare=nextFare};labels[edge.key]=rows
            end
            costs[key]=g
            open[#open+1]={key=key,p=edge and edge.to or b,g=g,f=g+remainingCost(edge),previous=parent,bridge=edge,fare=nextFare,
                walk=known and known.path,length=length,joinFrom=parent.p,joinTo=to}
        end
        while #open>0 do
            if #open>8192 or expanded>512 then return end
            local at=1;for i=2,#open do
                if open[i].f<open[at].f then at=i end
                if i%1024==0 and A.Terrain.Checkpoint then A.Terrain.Checkpoint() end
            end
            local current=table.remove(open,at)
            if not done[current.key] and current.g==costs[current.key] then
                if current.key=='goal' then return current end
                done[current.key]=true;expanded=expanded+1
                if current.p.mapID==b.mapID then add(current,b) end
                for _,e in ipairs(graph[current.p.mapID] or {}) do
                    if eligible(e,current.p,phase) then add(current,e.from,e) end
                    itineraryWork=itineraryWork+1
                    if itineraryWork%256==0 and A.Terrain.Checkpoint then A.Terrain.Checkpoint() end
                    if itineraryWork>=262144 then return end
                end
            end
        end
    end
    for effort=cellBudget>=65536 and 1 or 2,2 do
    probing=effort==1
    if not probing then
        for _,rows in pairs(joins) do for target,known in pairs(rows) do if known.deferred then rows[target]=nil end end end
    end
    for phase=1,2 do
        for attempt=1,128 do
            local candidate=optimisticItinerary(phase)
            if not candidate then break end
            local chain={};local cursor=candidate
            while cursor.previous do table.insert(chain,1,cursor);cursor=cursor.previous end
            local checked,complete=false,true;local actual=0
            for _,step in ipairs(chain) do
                if not step.walk then
                    checked=true
                    local path,length=localPath(step.joinFrom,step.joinTo)
                    joins[step.joinFrom]=joins[step.joinFrom] or {}
                    joins[step.joinFrom][step.joinTo]={path=path,length=length,deferred=probing and not path and length=='budget'}
                    if not path then complete=false;break end
                    step.walk=path;step.length=length
                end
                actual=actual+step.length+(step.bridge and cost(step.bridge) or 0);step.g=actual;step.f=actual
            end
            if complete then
                if not probing and not checked then return assemble(candidate,a,b,options) end
                if not bestGoal or candidate.g<bestGoal.g then bestGoal=candidate end
                if probing then
                    local lower=optimisticItinerary(phase,true)
                    local tolerance=deferredProbes and 1.20 or (hops[a.mapID] or 0)>=5 and 1.05 or 1
                    if lower and bestGoal.g<=lower.g*tolerance+.000001 then return assemble(bestGoal,a,b,options) end
                    if not checked then break end
                end
            end
            if itineraryWork>=262144 or probing and (probeSpent>=probeBudget or probeCalls>=32) then break end
        end
    end
    end
    probing=false
    -- Try the shortest zone itinerary first. Validate its actual local paths;
    -- if a pass is disconnected, retry the unrestricted graph with the same
    -- memoized results and bounded shared work budget.
    for phase=1,2 do
    frontier={initial};scores={start=0};closed={};work=0
    local labels={}
    if bestGoal then frontier[#frontier+1]=bestGoal;scores.goal=bestGoal.g end
    local iterations=0
    while #frontier>0 do
        iterations=iterations+1
        if iterations%32==0 and A.Terrain.Checkpoint then A.Terrain.Checkpoint() end
        if #frontier>8192 then
            if bestGoal then return assemble(bestGoal,a,b,options) end
            return nil,'Walking network search reached its limit.'
        end
        local at=1;for i=2,#frontier do
            if frontier[i].f<frontier[at].f then at=i end
            if i%1024==0 and A.Terrain.Checkpoint then A.Terrain.Checkpoint() end
        end
        local current=table.remove(frontier,at)
        if current.attempt=='goal' then
            local parent=current.previous
            if not scores.goal or current.f<scores.goal then
                local path,length=localPath(parent.p,b)
                if path and (not scores.goal or parent.g+length<scores.goal) then
                    scores.goal=parent.g+length
                    local goal={key='goal',p=b,g=scores.goal,f=scores.goal,previous=parent,walk=path,length=length,fare=parent.fare}
                    frontier[#frontier+1]=goal;bestGoal=goal
                end
            end
        elseif current.attempt=='connection' then
            local parent,e=current.previous,current.edge
            if not closed[current.key] and (not scores.goal or current.f<scores.goal) and
                (not scores[current.key] or current.lower<scores[current.key]) then
                local path,length=localPath(parent.p,e.from)
                local g=path and parent.g+length+cost(e)
                local dominated=false
                if budget and g then
                    for _,label in ipairs(labels[e.key] or {}) do if label.g<=g and label.fare<=current.fare then dominated=true;break end end
                end
                if g and not dominated and (not scores[current.key] or g<scores[current.key]) then
                    scores[current.key]=g
                    if budget then
                        labels[e.key]=labels[e.key] or {};local rows=labels[e.key]
                        for i=#rows,1,-1 do if g<=rows[i].g and current.fare<=rows[i].fare then table.remove(rows,i) end end
                        rows[#rows+1]={g=g,fare=current.fare}
                    end
                    frontier[#frontier+1]={key=current.key,p=e.to,g=g,f=g+heuristic(e.to),previous=parent,walk=path,length=length,bridge=e,fare=current.fare}
                end
            end
        elseif not closed[current.key] and current.g==scores[current.key] then
            if current.key=='goal' then return assemble(current,a,b,options) end
            closed[current.key]=true;work=work+1
            if work>512 then
                if bestGoal then return assemble(bestGoal,a,b,options) end
                return nil,'Walking network search reached its limit.'
            end
            if current.p.mapID==b.mapID then
                local lower=current.g+(P.Distance(current.p,b) or 0)
                if not scores.goal or lower<scores.goal then frontier[#frontier+1]={attempt='goal',f=lower,previous=current} end
            end
            for _,e in ipairs(graph[current.p.mapID] or {}) do
                local nextFare=(current.fare or 0)+fare(e)
                local key=budget and e.key..':fare:'..nextFare or e.key
                local lower=current.g+(P.Distance(current.p,e.from) or 0)+cost(e)
                local estimate=lower+heuristic(e.to)
                if estimate<math.huge and (not budget or nextFare<=budget) and not closed[key] and
                    (not scores[key] or lower<scores[key]) and (not scores.goal or estimate<scores.goal) and
                    eligible(e,current.p,phase) then
                    -- Queue a cheap lower bound first. Do not eagerly spend
                    -- the walking budget on every exit before the promising
                    -- flight/boat journey can advance to its final short walk.
                    frontier[#frontier+1]={attempt='connection',key=key,edge=e,previous=current,fare=nextFare,lower=lower,f=estimate}
                end
            end
        end
    end
    end
    return nil,limited and 'Some walking connections exceeded the search budget. Try an intermediate waypoint.' or 'No walking route was found through the verified zone crossings.'
end
