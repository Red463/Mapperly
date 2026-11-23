local _,A=...
local B={};A.TravelBounds=B
local function valid(v)
    return not (issecretvalue and issecretvalue(v)) and type(v)=='number' and v==v and math.abs(v)<math.huge
end
local function world(p)
    if type(p)~='table' or not A.TravelNetwork or type(A.TravelNetwork.World)~='function' then return end
    local ok,x,y,instance=pcall(A.TravelNetwork.World,p)
    if ok and valid(x) and valid(y) and valid(instance) then return {x,y,instance} end
end
local function distance(p,q)
    if p[3]~=q[3] then return math.huge end
    local dx,dy=math.abs(p[1]-q[1]),math.abs(p[2]-q[2])
    local scale=math.max(dx,dy)
    if scale==0 then return 0 end
    if scale==math.huge then return math.huge end
    return scale*math.sqrt((dx/scale)^2+(dy/scale)^2)
end
local function pointKey(p) return string.format('%.17g:%.17g:%.17g',p[1],p[2],p[3]) end
function B.Build(goal,edges,speed)
    local destination=world(goal)
    if not destination or type(edges)~='table' or not valid(speed) or speed<=0 then return end
    local count=#edges
    for key in pairs(edges) do
        if not valid(key) or key%1~=0 or key<1 or key>count then return end
    end
    local links,arrivals,arrivalIDs,incoming,remaining,closed={},{},{},{},{},{}
    local work=0
    local function checkpoint()
        work=work+1
        if work%256==0 and A.Terrain and A.Terrain.Checkpoint then A.Terrain.Checkpoint() end
    end
    for i=1,count do
        local edge=edges[i]
        if type(edge)~='table' or not valid(edge.seconds) or edge.seconds<0 then return end
        local from,to=world(edge.from),world(edge.to)
        local cost=edge.seconds*speed
        if not from or not to or not valid(cost) then return end
        local key=pointKey(to);local arrival=arrivalIDs[key]
        if not arrival then
            arrival=#arrivals+1;arrivalIDs[key]=arrival;arrivals[arrival]=to
            incoming[arrival]={};remaining[arrival]=distance(to,destination)
        end
        local link={from=from,arrival=arrival,cost=cost}
        links[i]=link;incoming[arrival][#incoming[arrival]+1]=link
        checkpoint()
    end
    -- Reverse Dijkstra over transport arrival states. Walking may cross any
    -- barriers within an instance; fares and permissions are deliberately
    -- ignored here. Actual route search still enforces them.
    for _=1,#arrivals do
        local at,best
        for i=1,#arrivals do
            if not closed[i] and remaining[i]<math.huge and (not best or remaining[i]<best) then at,best=i,remaining[i] end
            checkpoint()
        end
        if not at then break end
        closed[at]=true
        for i,position in ipairs(arrivals) do
            if not closed[i] then
                for _,link in ipairs(incoming[at]) do
                    local candidate=distance(position,link.from)+link.cost+best
                    if candidate<remaining[i] then remaining[i]=candidate end
                    checkpoint()
                end
            end
            checkpoint()
        end
    end
    -- A recorded offer can share its master with hundreds of other offers.
    -- Keep one arrival state per exact world position, then keep only the
    -- cheapest continuation at each departure position for bound queries.
    local departures,departureIDs={},{}
    for _,link in ipairs(links) do
        local cost=link.cost+remaining[link.arrival]
        local key=pointKey(link.from);local at=departureIDs[key]
        if not at then
            at=#departures+1;departureIDs[key]=at;departures[at]={from=link.from,cost=cost}
        elseif cost<departures[at].cost then departures[at].cost=cost end
        checkpoint()
    end
    local cache={}
    return function(p)
        local start=world(p)
        if not start then return end
        local key=pointKey(start)
        if cache[key]~=nil then return cache[key] end
        local best=distance(start,destination)
        for _,link in ipairs(departures) do
            local candidate=distance(start,link.from)+link.cost
            if candidate<best then best=candidate end
            checkpoint()
        end
        cache[key]=best
        return best
    end
end
