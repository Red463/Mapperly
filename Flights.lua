local _,A=...
local F={worldReady=true};A.Flights=F
local function secret(v) return issecretvalue and issecretvalue(v) end
local function number(v) return not secret(v) and type(v)=='number' and v==v and math.abs(v)<math.huge end
local function id(v) return number(v) and v>0 and v%1==0 and v<=100000000 end
local function call(fn,...)
    if type(fn)~='function' then return end
    local ok,a,b,c=pcall(fn,...);if ok then return a,b,c end
end
local function identity()
    local guid=call(UnitGUID,'player')
    if secret(guid) or type(guid)~='string' or not guid:match('^Player%-') or #guid>100 then return end
    local side=call(UnitFactionGroup,'player')
    if secret(side) or side~='Alliance' and side~='Horde' then side='Unknown' end
    local _,class=call(UnitClass,'player')
    if secret(class) or type(class)~='string' then class='Unknown' end
    return guid,side,class
end
function F.Character()
    local guid,side,class=identity();local d=A.FlightData
    if not guid or not A.db or not d or d.version~=1 then return end
    A.db.flightKnowledge=A.db.flightKnowledge or {}
    local c=A.db.flightKnowledge[guid]
    if type(c)~='table' or c.build~=d.build or c.version~=1 then
        c={version=1,build=d.build,nodes={},offers={},side=side,class=class};A.db.flightKnowledge[guid]=c
    end
    if type(c.nodes)~='table' then c.nodes={} end
    if type(c.offers)~='table' then c.offers={} end
    if side~='Unknown' and class~='Unknown' and (c.side~=side or c.class~=class) then c.side=side;c.class=class;c.offers={} end
    return c,guid
end
function F.Stats()
    local c=F.Character();local known,routes=0,0
    if c then
        for node,value in pairs(c.nodes) do if value==true and A.FlightData.nodes[node] then known=known+1 end end
        for _,offers in pairs(c.offers) do if type(offers)=='table' then for _ in pairs(offers) do routes=routes+1 end end end
    end
    return known,routes
end
-- One lookup per visible pin batch. A zone and an overview can return
-- different subsets of taxi nodes, so also try the node's home map.
function F.MapDiscovery(map)
    local queried,undiscovered={},{}
    local character=F.Character()
    local mapInfo=call(C_Map and C_Map.GetMapInfo,map)
    local function read(mapID)
        if not id(mapID) or queried[mapID] then return end
        queried[mapID]=true
        local rows=call(C_TaxiMap and C_TaxiMap.GetTaxiNodesForMap,mapID)
        if secret(rows) or type(rows)~='table' then return end
        for _,row in pairs(rows) do
            if not secret(row) and type(row)=='table' and id(row.nodeID) and
                not secret(row.isUndiscovered) and row.isUndiscovered==true then
                -- Forever can return false even for unlearned stops.
                undiscovered[row.nodeID]=true
            end
        end
    end
    return function(nodeID)
        if not id(nodeID) then return end
        read(map)
        if not undiscovered[nodeID] then
            local node=A.FlightData and A.FlightData.nodes[nodeID]
            if node and node.a then read(node.a.mapID) end
        end
        if not undiscovered[nodeID] and mapInfo then read(mapInfo.parentMapID) end
        if undiscovered[nodeID] then return 'locked' end
        if character and character.nodes[nodeID]==true then return 'unlocked' end
    end
end
local function notify(changed)
    if A.RefreshFlightPinStates then A.RefreshFlightPinStates() end
    if A.NavigationSettings then A.NavigationSettings.Sync() end
    if changed and A.Navigation and A.Navigation.OnFlightsChanged then A.Navigation.OnFlightsChanged() end
end
function F.Collect()
    if not F.open then return false end
    local c,guid=F.Character();local _,side,class=identity()
    if not c or side=='Unknown' or class=='Unknown' then return false end
    local map=call(GetTaxiMapID)
    if not id(map) or not C_TaxiMap or type(C_TaxiMap.GetAllTaxiNodes)~='function' then return false end
    local rows=call(C_TaxiMap.GetAllTaxiNodes,map)
    if secret(rows) or type(rows)~='table' then return false end
    local slots,ambiguous,valid={}, {}, {};local current;local count=0
    for _,row in pairs(rows) do
        count=count+1;if count>512 then break end
        if not secret(row) and type(row)=='table' and not secret(row.isMapLayerTransition) and not row.isMapLayerTransition and id(row.nodeID) and number(row.state) and (row.state==0 or row.state==1 or row.state==2) then
            valid[#valid+1]=row
            if row.state==0 then if current and current~=row.nodeID then return false end;current=row.nodeID end
            if id(row.slotIndex) and row.slotIndex<=4096 then
                if slots[row.slotIndex] and slots[row.slotIndex]~=row.nodeID then ambiguous[row.slotIndex]=true end
                slots[row.slotIndex]=row.nodeID
            end
        end
    end
    if not current then return false end
    for slot in pairs(ambiguous) do slots[slot]=nil end
    F.source=current;F.sessionGUID=guid
    local changed=false
    c.offers[current]=type(c.offers[current])=='table' and c.offers[current] or {}
    local offers=c.offers[current]
    for _,row in ipairs(valid) do
        if row.state==0 or row.state==1 then if not c.nodes[row.nodeID] then c.nodes[row.nodeID]=true;changed=true end end
        if row.state==2 and offers[row.nodeID] then offers[row.nodeID]=nil;changed=true end
        if row.state==1 and id(row.slotIndex) and slots[row.slotIndex]==row.nodeID then
            local fare=call(TaxiNodeCost,row.slotIndex)
            if not number(fare) or fare<0 or fare%1~=0 or fare>10000000000 then fare=nil end
            local hops={current};local seen={[current]=true};local complete=true;local routes=call(GetNumRoutes,row.slotIndex)
            if not number(routes) or routes<1 or routes>64 or routes%1~=0 then complete=false else
                for i=1,routes do
                    local source=call(TaxiGetNodeSlot,row.slotIndex,i,true);local target=call(TaxiGetNodeSlot,row.slotIndex,i,false)
                    if not id(source) or not id(target) or not slots[source] or not slots[target] or seen[slots[target]] or slots[source]~=hops[#hops] then complete=false;break end
                    hops[#hops+1]=slots[target]
                    seen[slots[target]]=true
                end
                if hops[#hops]~=row.nodeID then complete=false end
            end
            if not complete then hops=nil end
            local signature=tostring(fare)..':'..(hops and table.concat(hops,',') or 'incomplete')
            if type(offers[row.nodeID])~='table' or offers[row.nodeID].signature~=signature then
                offers[row.nodeID]={from=current,to=row.nodeID,fare=fare,hops=hops,signature=signature};changed=true
            end
        end
    end
    local force=F.forceReplan;F.forceReplan=nil
    notify(changed or force);return true
end
function F.Opened()
    F.open=true;F.source=nil;F.sessionGUID=nil;F.forceReplan=true
    local ok=F.Collect();F.retry=not ok
    return ok
end
function F.Closed() F.open=false;F.retry=false;F.source=nil;F.sessionGUID=nil;F.forceReplan=nil end
function F.WorldChanged(ready) F.worldReady=ready;F.worldGeneration=(F.worldGeneration or 0)+1;if not ready then F.Closed() end end
function F.OnTaxi()
    local v=call(UnitOnTaxi,'player')
    if not secret(v) and type(v)=='boolean' then return v end
end
function F.Money() local v=call(GetMoney);if number(v) and v>=0 then return v end end
local function allowed(n,side,class)
    if not n or n.eligible==false or n.classToken and n.classToken~=class then return false end
    local mask=n.factionMask
    return number(mask) and (side=='Alliance' and mask%2==1 or side=='Horde' and math.floor(mask/2)%2==1)
end
local function clock() local t=call(GetTime);return number(t) and t end
F.contexts=setmetatable({},{__mode='k'})
function F.BoardingContext(p)
    local c,guid=F.Character();local d=A.FlightData;local n=d and d.nodes[F.source]
    if not F.open or not c or guid~=F.sessionGUID or not allowed(n,c.side,c.class) or F.OnTaxi()==true or not p then return end
    local distance=A.TravelNetwork.Distance(p,n.world)
    if not distance or distance>40 then return end
    local context={guid=guid,source=F.source,build=d.build,point={mapID=p.mapID,x=p.x,y=p.y},time=clock()}
    F.contexts[context]=true;return context
end
function F.ContextValid(context,p)
    if not context or not F.contexts[context] or not p then return false end
    local _,guid=F.Character();local t=clock();local q=context.point
    return guid==context.guid and A.FlightData.build==context.build and p.mapID==q.mapID and math.abs(p.x-q.x)<1e-8 and math.abs(p.y-q.y)<1e-8 and (not t or not context.time or t>=context.time and t-context.time<=30)
end
function F.Edges(options)
    local result={};local d=A.FlightData;local c,guid=F.Character();local _,side,class=identity()
    if not c or not d or not A.CrossingData or d.build~=A.CrossingData.build or A.db.useFlights==false or side=='Unknown' or class=='Unknown' or options and options.faction and options.faction~=side then return result end
    local money=F.Money()
    for source,offers in pairs(c.offers) do if id(source) and type(offers)=='table' then
        local first=d.nodes[source]
        if c.nodes[source] and allowed(first,side,class) then for target,offer in pairs(offers) do
            local last=d.nodes[target]
            if id(target) and type(offer)=='table' and offer.from==source and offer.to==target and c.nodes[target] and allowed(last,side,class) and last.destinationAvailable~=false and first.a and last.a and first.world.instance==last.world.instance then
                local cost,seconds,keys=0,0,{};local complete=type(offer.hops)=='table' and #offer.hops>=2 and #offer.hops<=65 and offer.hops[1]==source and offer.hops[#offer.hops]==target
                local seen={[source]=true}
                if complete then for i=2,#offer.hops do
                    local key=tostring(offer.hops[i-1])..':'..tostring(offer.hops[i]);local segment=d.segments[key]
                    if not segment or seen[offer.hops[i]] then complete=false;break end
                    seen[offer.hops[i]]=true
                    keys[#keys+1]=key;cost=cost+(segment.cost or 0);seconds=seconds+(segment.seconds or 0)
                end end
                local fare=offer.fare;local estimated=false
                if not number(fare) or fare<0 or fare%1~=0 then fare=nil end
                if fare==nil and complete then fare=cost;estimated=true end
                local context=options and options.boardingContext;local from=first.a;local override=false
                if options and F.ContextValid(context,options.start) and context.source==source then from=options.start;override=true end
                if (not money or not fare or fare<=money) and (override or A.Terrain.Segment(from,from)) and A.Terrain.Segment(last.a,last.a) then
                    if not complete then seconds=math.max(30,(A.TravelNetwork.Distance(first.world,last.world) or 0)/32);keys=nil end
                    local row={id='flight:'..source..':'..target,kind='flight',name=first.name..' to '..last.name,
                        fromName=first.name,toName=last.name,fromNodeID=source,toNodeID=target,a=from,b=last.a,
                        board=first.world,arrival=last.world,arrivalGroundHeight=last.landingZ or last.z,
                        planningSeconds=seconds+20,flightPaths=keys,geometryUnknown=not complete,fare=fare,fareEstimated=estimated,
                        characterGUID=guid,boardingAccess=first.manualAccess and 'flight-master access' or nil,arrivalAccess=last.manualAccess and 'flight-master access' or nil}
                    result[#result+1]={key=row.id,from=from,to=last.a,distance=0,seconds=row.planningSeconds,transport=row,boardingOverride=override}
                end
            end
        end end
    end end
    return result
end
function F.Path(row)
    local result={}
    local function append(p,split)
        result[#result+1]={worldX=p.worldX,worldY=p.worldY,instance=p.instance,breakBefore=split or p.breakBefore or false}
    end
    append(row.board,true)
    for _,key in ipairs(row.flightPaths or {}) do
        local segment=A.FlightData.segments[key]
        if segment then for i,p in ipairs(segment.path or {}) do append(p,i==1) end end
    end
    append(row.arrival,true);return result
end
function F.Fare(copper,estimated)
    if not number(copper) then return 'fare unknown; check flight master' end
    local gold=math.floor(copper/10000);local silver=math.floor(copper/100)%100;local c=copper%100
    return (estimated and 'estimated ' or 'last quote ')..(gold>0 and gold..'g ' or '')..(silver>0 and silver..'s ' or '')..c..'c'
end
function F.ShouldDefer(state)
    local taxi=F.OnTaxi()
    return taxi==true or state and state.flightSeen and not state.interrupted or false
end
function F.Guide(leg,p,state)
    local row=leg.transport;local _,guid=F.Character()
    if state.worldGeneration~=F.worldGeneration then state.landedSince=nil;state.worldGeneration=F.worldGeneration end
    if guid~=row.characterGUID then return nil,'Flight information is unavailable for this character.' end
    if not F.worldReady then state.landedSince=nil;return nil,'Waiting for the world to load...' end
    local taxi=F.OnTaxi()
    if taxi==true then
        state.flightSeen=true;state.departed=true;state.landedSince=nil;state.interrupted=nil;state.replanAttempted=nil
        return nil,'Flying to '..row.toName
    end
    if taxi==nil then state.landedSince=nil;return nil,'Waiting for flight status...' end
    if not p then state.landedSince=nil;return nil,'Waiting for player position...' end
    local shore=A.TravelNetwork.Distance(p,row.b)
    if shore and shore<=18 then
        if A.Transports.CanDisembark(row,p,state) then return nil,nil,true end
        if state.needsConfirmation then return nil,'On land? Open Active journey and choose Continue on foot.' end
        return A.Transports.Aim({worldX=select(1,A.TravelNetwork.World(row.b)),worldY=select(2,A.TravelNetwork.World(row.b)),instance=row.arrival.instance},p.mapID),'Land at '..row.toName..'; follow the flight-master access to the land marker.'
    end
    if state.flightSeen then
        local pad=A.TravelNetwork.Distance(p,row.arrival)
        if pad and pad<=40 then state.arrivalSeen=true end
        if state.arrivalSeen and pad and pad<=150 then
            local x,y,instance=A.TravelNetwork.World(row.b)
            return A.Transports.Aim({worldX=x,worldY=y,instance=instance},p.mapID),'Landed at '..row.toName..'; use flight-master access to reach the land marker.'
        end
        local t=clock()
        if t then state.landedSince=state.landedSince or t;if t-state.landedSince>=2 then state.interrupted=true end end
        return nil,state.interrupted and 'Flight ended early. Updating the journey...' or 'Checking landing position...'
    end
    local aim=A.Transports.Aim(row.board,p.mapID)
    return aim,'Speak to the flight master; choose '..row.toName..' in the flight window.'
end
F.driver=CreateFrame('Frame',nil,UIParent);F.driver:SetSize(1,1);F.driver:EnableMouse(false)
F.driver:SetScript('OnUpdate',function()
    if F.retry and F.open then F.retry=false;F.Collect() end
end)
