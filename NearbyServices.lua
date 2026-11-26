local _, A = ...
local S = {radius = 2000}
A.NearbyServices = S

local labels = {inn = 'Innkeeper', vendor = 'Vendor', repair = 'Gear repairs', trainer = 'Trainer', flight = 'Flight master', mail = 'Mailbox'}
local refreshMargin = 250
local poolRadiusSquared = (S.radius + refreshMargin)^2
local cache

local function within(ax, ay, bx, by, squaredLimit)
    return (ax - bx)^2 + (ay - by)^2 <= squaredLimit
end

local function continentFor(map)
    if not (C_Map and C_Map.GetMapInfo and C_Map.GetMapInfoAtPosition) then return end
    for depth = 1, 8 do
        local info = C_Map.GetMapInfo(map)
        if not info then return end
        if info.mapType == (Enum and Enum.UIMapType and Enum.UIMapType.Continent or 2) then return map end
        if not info.parentMapID or info.parentMapID == 0 or info.parentMapID == map then return end
        map = info.parentMapID
    end
end

local function buildPool(map, wx, wy, instance, side, classToken, classID, observed)
    local lists = {all = {}, inn = {}, vendor = {}, repair = {}, trainer = {}, flight = {}, mail = {}}
    local byKey = {}
    local continent = continentFor(map)
    local hbd = continent and LibStub and LibStub('HereBeDragons-2.0', true)
    local function project(world)
        -- Zone rectangles overlap. The continent's native area hit-test can
        -- distinguish, for example, Darkshire from nearby Deadwind Pass.
        if hbd then
            local x, y = hbd:GetZoneCoordinatesFromWorldInstance(world.worldX, world.worldY, instance, continent)
            local area = x and C_Map.GetMapInfoAtPosition(continent, x, y)
            local zone = area and A.TravelNetwork.Transform(world, area.mapID)
            if zone then
                local child = C_Map.GetMapInfoAtPosition(zone.mapID, zone.x, zone.y)
                return child and A.TravelNetwork.Transform(world, child.mapID) or zone
            end
        end
        return A.TravelNetwork.Transform(world, map) or A.QuestNavigation.Project(world)
    end
    local function add(category, name, detail, key, x, y, point, approach, npcID, repairs)
        local world = {worldX = x, worldY = y, instance = instance}
        point = point or project(world)
        if not point then return end
        local row = {name = name, category = category, detail = detail or labels[category], key = key, npcID = npcID,
            worldX = x, worldY = y, map = point.map or point.mapID, x = point.x, y = point.y, approach = approach}
        lists[category][#lists[category] + 1] = row
        if category == 'vendor' and repairs then lists.repair[#lists.repair + 1] = row end
        local first = byKey[key]
        if first then
            -- The same NPC can sell goods and train or keep an inn. Give each
            -- filter its own row, and keep one destination on the All tab.
            local combined = lists.all[first]
            local secondRole = combined.detail == row.detail and labels[category] or row.detail
            local both = {}
            for k,v in pairs(combined) do both[k] = v end
            both.detail = combined.detail .. ' / ' .. secondRole
            lists.all[first] = both
        else
            lists.all[#lists.all + 1] = row
            byKey[key] = #lists.all
        end
    end
    local function addSpawn(spawn)
        if not labels[spawn.category] then return end
        if not (spawn.access and spawn.access:find(side, 1, true)) then return end
        if spawn.trainerClass and spawn.trainerClass ~= classID then return end
        -- Database spawns store north/east. Map navigation uses east/north.
        local x, y = spawn.y, spawn.x
        if not within(x, y, wx, wy, poolRadiusSquared) then return end
        local category = spawn.category
        local key = string.format('%s:%d:%d:%.3f:%.3f', category == 'mail' and 'object' or 'npc', instance, spawn.id, x, y)
        local detail = spawn.specialty or labels[category]
        local point = spawn.mapID and A.TravelNetwork.Transform({worldX = x, worldY = y, instance = instance}, spawn.mapID)
        add(category, spawn.name, detail, key, x, y, point, nil, category ~= 'mail' and spawn.id or nil, spawn.repairs)
    end
    for _,spawn in ipairs(A.BundledServices or {}) do
        if spawn.instance == instance then addSpawn(spawn) end
    end
    for _,spawn in ipairs(A.ServiceDirectory and A.ServiceDirectory[instance] or {}) do addSpawn(spawn) end
    for id,node in pairs(A.FlightData and A.FlightData.nodes or {}) do
        local w, mask = node.world, node.factionMask or 0
        local eligible = side == 'A' and mask % 2 == 1 or side == 'H' and math.floor(mask / 2) % 2 == 1
        if eligible and node.eligible ~= false and node.destinationAvailable ~= false and node.a and w and w.instance == instance
            and (not node.classToken or node.classToken == classToken) and within(w.worldX, w.worldY, wx, wy, poolRadiusSquared) then
            local exact = A.TravelNetwork.Transform(w, node.a.mapID)
            add('flight', node.name, nil, 'flight:' .. id, w.worldX, w.worldY, exact, node.approachVerified and node.a)
        end
    end
    for _,pin in ipairs(observed) do
        local category = type(pin) == 'table' and pin.category
        if labels[category] and type(pin.access) == 'string' and pin.access:find(side, 1, true) and A.ValidPin(pin) then
            local x, y, world = A.TravelNetwork.World({mapID = pin.map, x = pin.x, y = pin.y})
            if world == instance and within(x, y, wx, wy, poolRadiusSquared) then
                -- Discoveries record the player standing beside the service.
                local duplicate = false
                for _,known in ipairs(lists[category]) do
                    if within(x, y, known.worldX, known.worldY, 16^2) then duplicate = true; break end
                end
                if not duplicate then
                    local key = string.format('discovery:%s:%d:%.3f:%.3f', category, instance, x, y)
                    add(category, pin.name, nil, key, x, y, pin)
                end
            end
        end
    end
    return {map = map, centerX = wx, centerY = wy, side = side, classToken = classToken, classID = classID,
        observed = observed, observedCount = #observed, lists = lists}
end

local function nearestFirst(a, b)
    if a.distance ~= b.distance then return a.distance < b.distance end
    if a.name ~= b.name then return a.name < b.name end
    return a.key < b.key
end

local function playerServices()
    local player, reason = A.Journey.PlayerPosition()
    if not player then return nil, nil, reason end
    local map = player.mapID
    local geometry = A.CrossingData.maps[map]
    local info = C_Map and C_Map.GetMapInfo and C_Map.GetMapInfo(map)
    local zone = info and info.name or geometry and geometry.name
    local wx, wy, instance = A.TravelNetwork.World(player)
    if not wx then return nil, zone, 'Service locations are unavailable on this map.' end
    local faction = UnitFactionGroup('player')
    if issecretvalue and issecretvalue(faction) then faction = nil end
    local side = faction == 'Alliance' and 'A' or faction == 'Horde' and 'H'
    if not side then return nil, zone, 'Your faction is unavailable.' end
    local _, classToken, classID = UnitClass('player')
    local observed = A.db.observed
    if not cache or cache.map ~= map or cache.side ~= side or cache.classToken ~= classToken or cache.classID ~= classID
        or cache.observed ~= observed or cache.observedCount ~= #observed
        or not within(wx, wy, cache.centerX, cache.centerY, refreshMargin^2) then
        cache = buildPool(map, wx, wy, instance, side, classToken, classID, observed)
    end
    if cache.x ~= wx or cache.y ~= wy then
        cache.x, cache.y, cache.results, cache.byRole = wx, wy, {}, nil
    end
    return cache, zone
end

local function rowsFor(pool, category)
    if pool.results[category] then return pool.results[category] end
    local rows = {}
    for _,row in ipairs(pool.lists[category] or {}) do
        local d2 = (pool.x - row.worldX)^2 + (pool.y - row.worldY)^2
        if d2 <= S.radius^2 then
            row.distance = math.sqrt(d2)
            rows[#rows + 1] = row
        end
    end
    table.sort(rows, nearestFirst)
    pool.results[category] = rows
    return rows
end

function S.List(category)
    local pool, zone, reason = playerServices()
    return pool and rowsFor(pool, category or 'all') or {}, zone, reason
end

function S.ListByRole()
    local pool, zone, reason = playerServices()
    if not pool then return nil, zone, reason end
    if not pool.byRole then
        pool.byRole = {}
        for role in pairs(labels) do pool.byRole[role] = rowsFor(pool, role) end
    end
    return pool.byRole, zone
end

function S.Navigate(selected)
    if type(selected) ~= 'table' or not labels[selected.category] then return nil, 'Choose a nearby service.' end
    local rows, _, reason = S.List(selected.category)
    for _,row in ipairs(rows) do
        if row.key == selected.key then
            local destination = {mapID = row.map, x = row.x, y = row.y}
            local name = row.name
            if A.db.navigationMode ~= 'direct' then
                if row.approach then
                    destination = row.approach
                    local x, y = A.TravelNetwork.World(destination)
                    if x and not within(x, y, row.worldX, row.worldY, 1) then
                        name = name .. ' (approach)'
                    end
                elseif A.Terrain.Zone(row.map) and not (A.CityNavigation and A.CityNavigation.Supports(destination))
                    and not A.Terrain.Segment(destination,destination)
                    and not (A.Structures and A.Structures.Access(destination, false)) then
                    local nearby = A.Terrain.Approach(destination, 30)
                    if nearby then destination, name = nearby, name .. ' (approach)' end
                end
            end
            return A.Navigation.Start(destination.mapID, destination.x*100, destination.y*100, name)
        end
    end
    return nil, reason or 'This service is no longer nearby.'
end
