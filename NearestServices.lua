local _,A=...
local S={categories={inn='Inn',mail='Mailbox',flight='Flight master',dungeon='Dungeon entrance'}};A.NearestServices=S
local function number(n) return not (issecretvalue and issecretvalue(n)) and type(n)=='number' and n==n and math.abs(n)<math.huge end
local function faction()
    local ok,side=pcall(UnitFactionGroup or function()end,'player')
    if ok and not (issecretvalue and issecretvalue(side)) then return side=='Alliance' and 'A' or side=='Horde' and 'H' or nil end
end
local function point(p) return {mapID=p.mapID or p.map,x=p.x,y=p.y} end
local function copy(p) local r={};for k,v in pairs(p) do r[k]=v end;return r end
local function checkpoint() if A.Terrain.Checkpoint then A.Terrain.Checkpoint() end end
function S.Candidates(kind,start)
    local side=faction();if not side or not S.categories[kind] then return {} end
    if type(start)~='table' or not number(start.mapID or start.map) or not number(start.x) or not number(start.y) then return {} end
    local rows={};local _,_,instance=A.TravelNetwork.World(point(start))
    local function project(world)
        if not number(world.worldX) or not number(world.worldY) or not number(world.instance) then return end
        -- Map artwork rectangles overlap. Prefer the player's existing map
        -- when it contains this exact world position, avoiding a gratuitous
        -- zone detour to the same physical point on a smaller neighbor map.
        local id=start.mapID or start.map;local m=A.CrossingData and A.CrossingData.maps[id]
        if m and m.instance==world.instance then
            local x,y=(m.west-world.worldX)/m.width,(m.north-world.worldY)/m.height
            if x>=0 and x<=1 and y>=0 and y<=1 then return {map=id,x=x,y=y} end
        end
        return A.QuestNavigation.Project(world)
    end
    local function add(p,source,identity)
        if not p or not A.ValidPin(p) or not A.Terrain.Zone(p.map) then return end
        p=copy(p);p.map=A.TravelNetwork.Canonical(p.map)
        local x,y,i=A.TravelNetwork.World(point(p));if not number(x) or not number(y) or i~=instance then return end
        for _,other in ipairs(rows) do
            local distance=(other.worldX-x)^2+(other.worldY-y)^2
            if other.instance==i and (distance<=.0001 or distance<=16^2 and (other.source=='Observed' or other.name==p.name)) then return end
        end
        p.category=kind;p.source=source;p.worldX=x;p.worldY=y;p.instance=i
        -- World round trips through overlapping maps can differ by a few
        -- floating-point bits. Keep the source identity stable across zones.
        p.serviceKey=source..':'..kind..':'..tostring(identity)..':'..string.format('%.6f:%.6f:%s',x,y,i)
        p.serviceKind=kind;p.walkingOnly=true
        local d=A.TravelNetwork.Distance(point(start),point(p))
        if not number(d) then return end
        -- A blocked exact location may have a permitted approach up to30yd
        -- closer. Subtract that bound so such a candidate is never pruned.
        p.lowerBound=math.max(0,d-30);rows[#rows+1]=p
    end
    -- Prefer actual interaction locations when they duplicate a static spawn.
    for _,p in ipairs(A.db and A.db.observed or {}) do
        if type(p)=='table' and p.category==kind and type(p.access)=='string' and p.access:find(side,1,true) then add(p,'Observed',p.name) end
    end
    if kind=='inn' or kind=='mail' then
        for _,row in ipairs(A.BundledServices or {}) do
            if row.category==kind and type(row.access)=='string' and row.access:find(side,1,true) then
                local p=project({worldX=row.y,worldY=row.x,instance=row.instance})
                if p then p.name=row.name;add(p,'Snapshot',row.id) end
            end
        end
    elseif kind=='flight' then
        local _,class
        if UnitClass then local ok,a,b=pcall(UnitClass,'player');if ok then class=b end end
        for id,node in pairs(A.FlightData and A.FlightData.nodes or {}) do
            local mask=node.factionMask
            if node.eligible~=false and (not node.classToken or node.classToken==class) and number(mask) and
                (side=='A' and mask%2==1 or side=='H' and math.floor(mask/2)%2==1) and node.a and node.world and node.destinationAvailable~=false then
                local p=project(node.world)
                if p then
                    p.name=node.name;p.manualAccess=node.manualAccess
                    local d=A.TravelNetwork.Distance(node.a,node.world)
                    if node.manualAccess or d and d>1 then p.serviceApproach=copy(node.a) end
                    add(p,'Native',id)
                end
            end
        end
    elseif kind=='dungeon' then
        for index,row in ipairs(A.MapPlaces and A.MapPlaces.instances or {}) do
            local p=row.map and {map=row.map,x=row[2],y=row[3]} or project({worldX=row[3],worldY=row[2],instance=row[1]})
            if p then
                local names={};for _,d in ipairs(row[4] or {}) do names[#names+1]=d[2] end
                p.name=table.concat(names,', ');add(p,'Bundled',index)
            end
        end
    end
    table.sort(rows,function(a,b) return a.lowerBound==b.lowerBound and a.serviceKey<b.serviceKey or a.lowerBound<b.lowerBound end)
    return rows
end
local function approach(pin)
    local target=copy(pin);local exact=point(pin)
    target.serviceExact={map=pin.map,x=pin.x,y=pin.y,name=pin.name}
    if not pin.serviceApproach and A.Terrain.Segment(exact,exact) then return target end
    local near
    if pin.serviceApproach then
        local x,y,instance=A.TravelNetwork.World(pin.serviceApproach);local m=A.CrossingData.maps[pin.map]
        if m and m.instance==instance then near={mapID=pin.map,x=(m.west-x)/m.width,y=(m.north-y)/m.height} end
    else near=A.Terrain.Approach(exact,30) end
    local z=A.Terrain.Zone(pin.map)
    local distance=near and near.mapID==pin.map and math.sqrt(((near.x-pin.x)*z.widthYards)^2+((near.y-pin.y)*z.heightYards)^2)
    if not distance or distance>30.000001 or not A.Terrain.Segment(near,near) then return end
    target.x=near.x;target.y=near.y;target.approachDistance=distance;target.name=pin.name:sub(1,109)..' (approach)'
    return target
end
function S.Resolve(selected)
    if type(selected)~='table' or not S.categories[selected.serviceKind] or type(selected.serviceKey)~='string' then return nil,'Choose a service result first.' end
    if A.db.navigationMode=='direct' then return nil,'Enable Smart routing to use a walking-service result.' end
    local start,why=A.Journey.PlayerPosition();if not start then return nil,why end
    for _,pin in ipairs(S.Candidates(selected.serviceKind,start)) do
        if pin.serviceKey==selected.serviceKey then
            local target=approach(pin)
            if target then return target end
            return nil,'No permitted approach remains within 30 yards of this service.'
        end
    end
    return nil,'This service or its faction access changed. Find services again.'
end
local function limited(why)
    why=tostring(why or ''):lower()
    return why:find('budget',1,true) or why:find('limit',1,true)
end
function S.Find(kind,start,options)
    options=options or {};local rows=S.Candidates(kind,start)
    local cap=math.max(1,math.min(24,tonumber(options.maxCandidates) or 12))
    local maxCells=math.max(1024,math.min(750000,tonumber(options.maxCells) or 350000))
    local begin=A.PlanningJob.Progress();local initialCells=begin and begin.cells or 0
    local best,checked,uncertain= nil,0,math.huge
    for index,pin in ipairs(rows) do
        checkpoint()
        if best and pin.lowerBound>=best.plan.distance then break end
        local progress=A.PlanningJob.Progress();local spent=progress and progress.cells-initialCells or 0
        if checked>=cap or spent>=maxCells then uncertain=math.min(uncertain,pin.lowerBound);break end
        A.PlanningJob.Report('Checking nearby '..(S.categories[kind] or 'service'):lower(),{checked=index,total=#rows})
        local target=approach(pin)
        if target then
            checked=checked+1
            local plan,why=A.Journey.Plan(start,target,{walkingOnly=true,preferRoads=A.db.preferRoads,roadPreferenceStrength=A.db.roadPreferenceStrength,maxWalkingCells=math.min(100000,maxCells-spent)})
            if plan and number(plan.distance) and (not best or plan.distance<best.plan.distance) then best={pin=target,plan=plan}
            elseif not plan and limited(why) then uncertain=math.min(uncertain,pin.lowerBound) end
        end
    end
    if not best then return nil,string.format('No verified walking route found (%d service routes checked). Unverified or budget-limited locations may still exist.',checked) end
    best.complete=uncertain>=best.plan.distance;best.checked=checked;best.total=#rows;best.start=point(start)
    return best
end
function S.Request(kind,done,failed)
    if not S.categories[kind] then return nil,'Choose a service type.' end
    if A.db.navigationMode=='direct' then return nil,'Enable Smart routing to find a reachable service.' end
    if A.PlanningJob.IsRunning() then return nil,'A route is already being planned. Wait or cancel it first.' end
    if A.Flights and A.Flights.OnTaxi()==true then return nil,'Wait until you land before finding nearby services.' end
    if A.Transports and A.Transports.ShouldDefer and A.Transports.ShouldDefer() then return nil,'Finish the current transport ride before finding nearby services.' end
    local start,why=A.Journey.PlayerPosition();if not start then return nil,why end
    if not faction() then return nil,'Your faction is unavailable. Try again after loading.' end
    if not A.Terrain.Zone(start.mapID or start.map) or not A.Terrain.Segment(point(start),point(start)) then return nil,'Move onto known walkable terrain before finding nearby services.' end
    A.PlanningJob.Start(function() return S.Find(kind,start) end,done,failed)
    return true
end
