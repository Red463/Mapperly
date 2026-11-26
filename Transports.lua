local _,A=...
local T={};A.Transports=T
local preferences={boat='useBoats',zeppelin='useZeppelins',airship='useAirships',tram='useTrams',lift='useLifts'}
local function number(n) return not (issecretvalue and issecretvalue(n)) and type(n)=='number' and n==n and math.abs(n)<math.huge end
local function position(p)
    if not UnitPosition then return end
    local ok,north,east,z,instance=pcall(UnitPosition,'player')
    if not ok or not number(north) or not number(east) then return end
    if p then
        local x,y,i=A.TravelNetwork.World(p)
        if not x or (east-x)^2+(north-y)^2>=64 or number(instance) and instance~=i then return nil,nil,'conflict' end
    end
    if not number(z) then return nil,number(instance) and instance or nil end
    return z,number(instance) and instance or nil
end
local function liftHeight(row,p)
    local z,_,reason=position(p)
    if reason=='conflict' then return nil,reason end
    -- Forever can return a public, constant zero for Z. When neither landing
    -- is at sea level this cannot establish the player's floor or movement.
    if z==0 and number(row.boardingGroundHeight) and math.abs(row.boardingGroundHeight)>8 and number(row.arrivalGroundHeight) and math.abs(row.arrivalGroundHeight)>8 then return end
    return z
end
local function clearLiftExit(row,p)
    if not p or not A.WalkingRegions then return false end
    local grid=row.arrivalExitMask
    if grid and grid.version==1 and number(grid.cellSize) and grid.cellSize>0 and grid.cellSize<=4 and
        number(grid.originNorth) and number(grid.originEast) and number(grid.width) and grid.width<=128 and number(grid.height) and grid.height<=128 and
        number(grid.minHeight) and number(grid.maxHeight) and type(grid.rows)=='table' then
        local x,y,instance=A.TravelNetwork.World(p)
        if x and instance==grid.instance then
            local column=math.floor((grid.originEast-x)/grid.cellSize)
            local line=math.floor((grid.originNorth-y)/grid.cellSize)
            local bits=line>=0 and line<grid.height and grid.rows[line+1]
            if column>=0 and column<grid.width and type(bits)=='string' and bits:sub(column+1,column+1)=='1' then
                local q=A.TravelNetwork.Transform(p,grid.mapID)
                if q and A.WalkingRegions.Get(q)==grid.region and A.Terrain.Segment(q,q) then return grid end
            end
        end
    end
    for _,zone in ipairs(row.arrivalExits or {}) do
        local q=A.TravelNetwork.Transform(p,zone.mapID)
        local distance=q and A.TravelNetwork.Distance(q,zone)
        if distance and number(zone.radius) and zone.radius>0 and zone.radius<=12 and distance<=zone.radius and
            number(zone.minHeight) and number(zone.maxHeight) and
            A.WalkingRegions.Get(q)==zone.region and A.Terrain.Segment(q,zone) then return zone end
    end
    return false
end
local function faction(options)
    if options and options.faction then return options.faction end
    if UnitFactionGroup then local ok,v=pcall(UnitFactionGroup,'player');if ok and not (issecretvalue and issecretvalue(v)) then return v end end
end
function T.DockCorridor(id)
    local h,d=A.HarbourAccessData,A.TransportData
    local row=h and h.corridors and h.corridors[id]
    if not row or h.version~=1 or not d or h.build~=d.build or h.proofSha256~=d.harbourProofSha256 or not A.Structures then return end
    if A.Structures.Get({structure=id,a=row.a,b=row.b})==row then return row end
end
function T.Edges(options)
    local result={}
    local side=faction(options)
    for _,key in ipairs({'TransportData','LocalTransportData','TramData'}) do
      local d=A[key]
      if d and d.version==1 and A.CrossingData and d.build==A.CrossingData.build then
      for _,row in ipairs(d.edges or {}) do
        local preference=preferences[row.kind]
        local allowed=preference and (not A.db or A.db[preference]~=false) and (row.faction=='Neutral' or row.faction==side and (side=='Alliance' or side=='Horde'))
        if row.boardingCorridor and not T.DockCorridor(row.boardingCorridor) or row.arrivalCorridor and not T.DockCorridor(row.arrivalCorridor) then allowed=false end
        if row.kind=='lift' then
            allowed=allowed and number(row.boardingGroundHeight) and number(row.arrivalGroundHeight) and math.abs(row.boardingGroundHeight-row.arrivalGroundHeight)>16
        end
        if allowed and row.a and row.b and row.board and row.arrival and number(row.planningSeconds) and row.planningSeconds>0 and row.planningSeconds<=7200 then
            local approach=A.TravelNetwork.Distance(row.a,row.board);local exit=A.TravelNetwork.Distance(row.b,row.arrival)
            if approach and exit and approach<=300 and exit<=300 and A.Terrain.Segment(row.a,row.a) and A.Terrain.Segment(row.b,row.b) then
                result[#result+1]={key='transport:'..row.id,from=row.a,to=row.b,distance=0,transport=row,seconds=row.planningSeconds}
            end
        end
      end
      end
    end
    if A.Flights then for _,edge in ipairs(A.Flights.Edges(options)) do result[#result+1]=edge end end
    return result
end
function T.HasMethod(kind)
    for _,key in ipairs({'TransportData','LocalTransportData','TramData'}) do
        local d=A[key]
        if d and d.version==1 and A.CrossingData and d.build==A.CrossingData.build then
            for _,row in ipairs(d.edges or {}) do if row.kind==kind then return true end end
        end
    end
    return false
end
function T.MinimumSeconds(edges)
    local minimum=math.huge
    for _,e in ipairs(edges or T.Edges()) do minimum=math.min(minimum,e.seconds) end
    return minimum
end
function T.Aim(world,map)
    local m=A.CrossingData and A.CrossingData.maps[map]
    if not m or world.instance~=m.instance then return end
    return {mapID=map,x=(m.west-world.worldX)/m.width,y=(m.north-world.worldY)/m.height}
end
function T.CanDisembark(row,p,state,confirm)
    if row.automaticTram and A.Trams then return A.Trams.CanDisembark(row,p,state) end
    if row.kind=='flight' and A.Flights then
        if not A.Flights.worldReady or A.Flights.OnTaxi()~=false then return false end
        if not state.flightSeen and not state.confirmed and not confirm then state.needsConfirmation=true;return false end
    end
    state.needsConfirmation=false
    local shore=p and A.TravelNetwork.Distance(p,row.b)
    local from=p and A.TravelNetwork.Distance(p,row.board)
    -- A certified pier continues inland beyond the tiny shore handoff. On
    -- zero-altitude clients require walking clear of the vessel's footprint;
    -- simply arriving on the ship's deck must not finish the sailing leg.
    if p and row.arrivalCorridor and T.DockCorridor(row.arrivalCorridor) and
        A.Structures and A.Structures.Contains(p,row.arrivalCorridor) then
        local _,_,reason=position(p)
        local aboard=A.TravelNetwork.Distance(p,row.arrival)
        if reason~='conflict' and aboard and aboard>25 and (not from or from>90 or state.departed) then return true end
    end
    if row.kind=='lift' then
        -- A lift can have the same XY on both floors. A readable destination
        -- height is sufficient even when the source-floor sample was missed.
        if not number(row.arrivalGroundHeight) then return false end
        local z,reason=liftHeight(row,p)
        if reason=='conflict' then return false end
        local exit=clearLiftExit(row,p)
        if exit then return not z or z>=exit.minHeight-8 and z<=exit.maxHeight+8 end
        if z and math.abs(z-row.arrivalGroundHeight)>8 then return false end
        if not shore or shore>18 then return false end
        if confirm then state.confirmed=true end
        if z or state.confirmed then return true end
        state.needsConfirmation=true;return false
    end
    if not shore or shore>18 then return false end
    if from and from<=90 and not state.departed then return false end
    if not number(row.arrivalGroundHeight) then if confirm then state.confirmed=true end;return true end
    if row.kind=='flight' then
        local z,_,reason=position(p)
        if reason=='conflict' then return false end
        if z==0 and math.abs(row.arrivalGroundHeight)>8 then z=nil end
        if z and math.abs(z-row.arrivalGroundHeight)>8 then return false end
        -- Unlike a lift/deck, a witnessed taxi ending on foot at the destination
        -- supplies positive landing evidence even when native altitude is zero.
        if z or state.flightSeen or state.confirmed or confirm then
            if confirm then state.confirmed=true end
            return true
        end
        state.needsConfirmation=true;return false
    end
    local x,y=A.TravelNetwork.World(p)
    if UnitPosition then
        local ok,north,east,z=pcall(UnitPosition,'player')
        if ok and number(north) and number(east) and number(z) and (z~=0 or row.arrivalGroundHeight==0) and (east-x)^2+(north-y)^2<64 then
            if math.abs(z-row.arrivalGroundHeight)>8 then return false end
            if confirm then state.confirmed=true end
            return true
        end
    end
    if confirm then state.confirmed=true end
    if state.confirmed then return true end
    local aboard=A.TravelNetwork.Distance(p,row.arrival)
    -- Protected height cannot distinguish a tower from a deck at the same XY.
    state.needsConfirmation=not aboard or aboard<=25
    return aboard and aboard>25 or false
end
function T.Guide(leg,p,state)
    if leg.transport.automaticTram and A.Trams then return A.Trams.Guide(leg,p,state) end
    if leg.transport.kind=='flight' and A.Flights then return A.Flights.Guide(leg,p,state) end
    local row=leg.transport;local label=({boat='boat',zeppelin='zeppelin',airship='airship',tram='tram',lift='lift'})[row.kind] or 'transport'
    local from=p and A.TravelNetwork.Distance(p,row.board)
    local shore=p and A.TravelNetwork.Distance(p,row.b)
    local arrival=p and A.TravelNetwork.Distance(p,row.arrival)
    if row.kind=='lift' then
        local z=p and liftHeight(row,p)
        if z and from and from<=90 and number(row.boardingGroundHeight) and number(row.arrivalGroundHeight) then
            if math.abs(z-row.boardingGroundHeight)<=8 then state.boardingSeen=true end
            local low=math.min(row.boardingGroundHeight,row.arrivalGroundHeight)-8
            local high=math.max(row.boardingGroundHeight,row.arrivalGroundHeight)+8
            if z>=low and z<=high and math.abs(z-row.boardingGroundHeight)>10 then state.departed=true end
        end
    elseif row.kind=='tram' and number(row.interiorInstance) then
        local _,instance=position()
        if instance==row.interiorInstance then state.departed=true;state.interiorSeen=true end
    end
    if from and from>320 or p and not from and A.TravelNetwork.World(p) then state.departed=true end
    if T.CanDisembark(row,p,state) then return nil,nil,true end
    if state.needsConfirmation then return nil,'On land? Open Active journey and choose Continue on foot.' end
    if row.kind=='tram' and state.interiorSeen then return nil,'Ride the tram to '..(row.toName or 'the destination')..'; leave the station through the city portal.' end
    if row.kind=='lift' then
        local z=p and liftHeight(row,p)
        if z and number(row.arrivalGroundHeight) and math.abs(z-row.arrivalGroundHeight)<=8 and shore and shore<=65 then
            local x,y,instance=A.TravelNetwork.World(row.b)
            return T.Aim({worldX=x,worldY=y,instance=instance},p.mapID),'Leave the lift; walk to the landing marker.'
        end
        if state.departed then return nil,'Stay aboard the lift to '..(row.toName or 'the destination') end
        return p and T.Aim(row.board,p.mapID),'Take the lift to '..(row.toName or 'the destination')..'; step off onto the destination side.'
    end
    if arrival and arrival<=65 then state.arrivalSeen=true end
    if state.arrivalSeen and arrival and arrival>320 then state.arrivalSeen=false end
    if state.arrivalSeen then
        local x,y,instance=A.TravelNetwork.World(row.b)
        local aim=p and T.Aim({worldX=x,worldY=y,instance=instance},p.mapID)
        return aim,row.arrivalAccess and 'Disembark; use '..row.arrivalAccess..' to reach the land marker.' or 'Disembark at '..(row.toName or 'the destination')
    end
    if state.departed then return nil,'Stay aboard to '..(row.toName or 'the destination') end
    if row.boardingPlank and p and from and not state.reachedPlank then
        local pier=A.TravelNetwork.Distance(p,row.boardingPlank)
        if pier and pier>8 and from>25 then
            return A.TravelNetwork.Transform(row.boardingPlank,p.mapID),'Walk to the boarding plank for '..row.toName
        end
        if pier then state.reachedPlank=true end
    end
    local aim=p and T.Aim(row.board,p.mapID)
    return aim,row.boardingAccess and 'Use '..row.boardingAccess..'; board for '..(row.toName or 'the destination') or 'Board the '..label..' to '..(row.toName or 'the destination')
end
function T.ShouldDefer()
    if A.Flights and A.Flights.OnTaxi()==true then return true end
    local leg=A.Journey and A.Journey.Leg()
    if not leg or leg.kind~='transport' then return false end
    if leg.transport.kind~='flight' then return true end
    return A.Flights.ShouldDefer(A.Journey.transportState)
end
