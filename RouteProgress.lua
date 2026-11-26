local _, A = ...
local P = {}
A.RouteProgress = P

local function finite(n)
    return not (issecretvalue and issecretvalue(n)) and type(n) == 'number' and n == n and math.abs(n) < math.huge
end

-- The segment starts at this point and ends at the follower's current target.
-- During a vehicle leg the index points at the break before boarding.
function P.Segment(plan)
    local j = A.Journey
    if not plan or not j or j.active ~= plan or not j.index then return end
    if j.crossing then
        local leg = j.Leg()
        if leg and leg.exitPath and leg.corridorStart then
            return leg.corridorStart + (j.structureIndex or 2) - 2
        end
        return j.index
    end
    return j.index - 1
end

function P.World(point, hbd)
    if finite(point.worldX) and finite(point.worldY) and finite(point.instance) then
        return point.worldX, point.worldY, point.instance
    end
    local map = point.mapID
    if not finite(map) then map = point.map end
    if not finite(point.x) or not finite(point.y) or not finite(map) then return end
    local ok, x, y, instance = pcall(hbd.GetWorldCoordinatesFromZone, hbd, point.x, point.y, map)
    if ok and finite(x) and finite(y) and finite(instance) then return x, y, instance end
end

-- Only project onto the follower's chosen segment. Later bends sometimes
-- double back alongside it. RouteRecovery owns the decision to rejoin them.
function P.Split(plan, hbd, px, py, instance)
    local index = P.Segment(plan)
    if not index or index < 1 or plan.kind == 'direct' or A.Journey.paused then return end
    local a, b = plan.points[index], plan.points[index + 1]
    if not a or not b or b.breakBefore or a.transport or b.transport then return end
    local leg = A.Journey.Leg()
    if leg and leg.kind == 'transport' then return end
    if A.RouteRecovery and A.RouteRecovery.IsOffRoute() then return end
    if A.Flights and (A.Flights.worldReady == false or A.Flights.OnTaxi() == true) then return end

    if not hbd then
        hbd = LibStub and LibStub('HereBeDragons-2.0', true)
        if not hbd then return end
        local ok
        ok, px, py, instance = pcall(hbd.GetPlayerWorldPosition, hbd)
        if not ok then return end
    end
    if not finite(px) or not finite(py) or not finite(instance) then return end
    local ax, ay, ai = P.World(a, hbd)
    local bx, by, bi = P.World(b, hbd)
    if ai ~= instance or bi ~= instance then return end

    local dx, dy = bx - ax, by - ay
    local lengthSquared = dx*dx + dy*dy
    if lengthSquared == 0 then return end
    local fraction = math.min(1, ((px - ax)*dx + (py - ay)*dy) / lengthSquared)
    if fraction <= 0 then return end
    local offsetX, offsetY = px - ax - fraction*dx, py - ay - fraction*dy
    -- Use the same 12-yard on-route tolerance as RouteRecovery.
    if offsetX*offsetX + offsetY*offsetY > 12*12 then return end
    return index, fraction, math.sqrt(lengthSquared)
end
