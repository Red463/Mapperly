local _, A = ...
A.categories = { 'mail', 'inn', 'dungeon', 'flight', 'transport', 'portal', 'border', 'notes' }
local defaults = { compact=true, scale=1, questPane=false, locked=false, coordinates=true, reveal=false, iconSize=18, alpha=1, movingAlpha=.65 }
A.noteIcons={'note_enemy','note_chest','note_poi','note_scenic','note_building','note_danger','note_camp','note_meeting','note_resource','note_fishing','note_cave','note_travel'}
A.noteIconNames={note_enemy='Enemy',note_chest='Chest / loot',note_poi='POI',note_scenic='Scenic spot',note_building='Building',note_danger='Avoid area',note_camp='Camp / rest',note_meeting='Meeting point',note_resource='Resources',note_fishing='Fishing',note_cave='Cave',note_travel='Travel / route'}
local legacyIcons={notes='Note',inn='Inn',mail='Mailbox',flight='Flight master',dungeon='Dungeon',portal='Portal',quest='Quest',navigation='Destination',transport='Boat',border='Zone exit'}
local function noteFields(fields)
    fields=type(fields)=='table' and fields or {}
    local name=type(fields.name)=='string' and fields.name:sub(1,120) or ''
    if name:match('^%s*$') then return end
    local icon='notes'
    for _,key in ipairs(A.noteIcons) do if fields.icon==key then icon=key;break end end
    if type(fields.icon)=='string' and legacyIcons[fields.icon] then icon=fields.icon end
    return {name=name,description=type(fields.description)=='string' and fields.description:sub(1,1000) or '',group=type(fields.group)=='string' and fields.group:sub(1,40) or '',icon=icon}
end
function A.NoteIconName(key) return A.noteIconNames[key] or legacyIcons[key] or 'Note' end
function A.Number(v, lo, hi, fallback)
    if type(v) ~= 'number' or v ~= v then return fallback end
    return math.max(lo, math.min(hi, v))
end
function A.ArrayValues(source)
    local keys,values={},{}
    for key in pairs(source) do
        if type(key)=='number' and key>0 and key<math.huge and key%1==0 then keys[#keys+1]=key end
    end
    table.sort(keys)
    for _,key in ipairs(keys) do values[#values+1]=source[key] end
    return values
end
function A.ValidateRouteStepsAnchor(p)
    local anchors={TOPLEFT=true,TOP=true,TOPRIGHT=true,LEFT=true,CENTER=true,RIGHT=true,BOTTOMLEFT=true,BOTTOM=true,BOTTOMRIGHT=true}
    if type(p)=='table' and anchors[p.point] and anchors[p.relativePoint] and A.Number(p.x,-10000,10000,nil)==p.x and A.Number(p.y,-10000,10000,nil)==p.y and type(p.x)=='number' and type(p.y)=='number' then
        return {point=p.point,relativePoint=p.relativePoint,x=p.x,y=p.y}
    end
end
function A.InitStore(raw)
    local db = type(raw)=='table' and raw or {}
    if db.theme~='gatherly' and db.theme~='original' then db.theme='gatherly' end
    if db.navigationMode~='terrain' and db.navigationMode~='direct' then db.navigationMode='terrain' end
    if type(db.showJourneyRoute)~='boolean' then db.showJourneyRoute=true end
    if type(db.showMinimapRoute)~='boolean' then db.showMinimapRoute=true end
    if type(db.showTransportLinks)~='boolean' then db.showTransportLinks=true end
    if type(db.showRouteSteps)~='boolean' then db.showRouteSteps=true end
    -- Older close buttons persisted false, indistinguishable from an opt-out.
    -- Restore the requested default once; later explicit settings remain saved.
    if db.routeStepsVisibilityVersion~=1 then db.showRouteSteps=true;db.routeStepsVisibilityVersion=1 end
    if type(db.routeStepsCollapsed)~='boolean' then db.routeStepsCollapsed=false end
    db.routeStepsAnchor=A.ValidateRouteStepsAnchor(db.routeStepsAnchor)
    if type(db.preferRoads)~='boolean' then db.preferRoads=false end
    if type(db.avoidSwimming)~='boolean' then db.avoidSwimming=db.allowSwimming==false end
    -- Former hard exclusion becomes dry-first planning with a swimming retry.
    db.allowSwimming=true
    if type(db.rememberJourney)~='boolean' then db.rememberJourney=true end
    db.roadPreferenceStrength=math.floor(A.Number(db.roadPreferenceStrength,1,5,3)+.5)
    for _,key in ipairs({'useBoats','useZeppelins','useAirships','useFlights','useTrams','useLifts'}) do if type(db[key])~='boolean' then db[key]=true end end
    if type(db.flightKnowledge)~='table' then db.flightKnowledge={} end
    for k,v in pairs(defaults) do
        if type(v)=='boolean' then if type(db[k])~='boolean' then db[k]=v end end
    end
    -- v2 sizes are fractions of the screen rather than native-window scale.
    if db.layoutVersion~=2 then db.scale=1;db.position=nil;db.layoutVersion=2 end
    db.scale=A.Number(db.scale,.5,1.1,1)
    db.iconSize=A.Number(db.iconSize,12,36,18)
    db.alpha=A.Number(db.alpha,.2,1,1)
    db.movingAlpha=A.Number(db.movingAlpha,.2,1,.65)
    db.filters=type(db.filters)=='table' and db.filters or {}
    for _,k in ipairs(A.categories) do if type(db.filters[k])~='boolean' then db.filters[k]=true end end
    db.continentFilters=type(db.continentFilters)=='table' and db.continentFilters or {}
    for _,k in ipairs(A.categories) do
        if type(db.continentFilters[k])~='boolean' then db.continentFilters[k]=k=='dungeon' end
    end
    db.notes=type(db.notes)=='table' and db.notes or {}
    db.observed=type(db.observed)=='table' and db.observed or {}
    for _,key in ipairs({'position','largePosition'}) do
        local p=db[key]
        if type(p)~='table' or type(p.x)~='number' or type(p.y)~='number' or A.Number(p.x,-10000,10000,nil)~=p.x or A.Number(p.y,-10000,10000,nil)~=p.y then db[key]=nil end
    end
    A.db=db
    local notes={}
    for _,p in ipairs(A.ArrayValues(db.notes)) do
        if A.ValidPin(p) then
            local known=false;for _,category in ipairs(A.categories) do if p.category==category then known=true;break end end
            if not known then p.category='notes' end
            local fields=noteFields(p)
            if fields then for k,v in pairs(fields) do p[k]=v end;notes[#notes+1]=p end
        end
    end
    db.notes=notes
    db.savedDestinations=type(db.savedDestinations)=='table' and db.savedDestinations or {}
    db.destinationHistory=type(db.destinationHistory)=='table' and db.destinationHistory or {}
    if A.Destinations then A.Destinations.Normalize() end
    local anchor=db.navigationAnchor
    local anchors={CENTER=true,TOP=true,BOTTOM=true,LEFT=true,RIGHT=true,TOPLEFT=true,TOPRIGHT=true,BOTTOMLEFT=true,BOTTOMRIGHT=true}
    if type(anchor)~='table' or not anchors[anchor.point] or not anchors[anchor.relativePoint] or A.Number(anchor.x,-10000,10000,nil)~=anchor.x or A.Number(anchor.y,-10000,10000,nil)~=anchor.y or type(anchor.x)~='number' or type(anchor.y)~='number' then db.navigationAnchor=nil end
    if A.JourneySession then A.JourneySession.Normalize(db) end
    return db
end
function A.ValidPin(p)
    return type(p)=='table' and type(p.map)=='number' and p.map>0 and p.map<math.huge and p.map%1==0 and type(p.x)=='number' and p.x==p.x and p.x>=0 and p.x<=1 and type(p.y)=='number' and p.y==p.y and p.y>=0 and p.y<=1 and type(p.name)=='string'
end
function A.UpdateNote(note,fields)
    local values=noteFields(fields)
    if not values or not A.ValidPin(note) then return false end
    for k,v in pairs(values) do note[k]=v end
    return note
end
function A.RemoveNote(note)
    for i,v in ipairs(A.db.notes) do if v==note then table.remove(A.db.notes,i);return true end end
    return false
end
function A.AddNote(map,x,y,name,fields)
    local p={map=tonumber(map),x=tonumber(x),y=tonumber(y),name=type(name)=='string' and name:sub(1,120) or '',category='notes'}
    fields=type(fields)=='table' and fields or {}
    local values=noteFields({name=p.name,description=fields.description,icon=fields.icon,group=fields.group})
    if not A.ValidPin(p) or not values then return false end
    for k,v in pairs(values) do p[k]=v end
    table.insert(A.db.notes,p);return p
end
function A.Observe(category,name)
    if not C_Map or not C_Map.GetBestMapForUnit or not C_Map.GetPlayerMapPosition then return end
    local map=C_Map.GetBestMapForUnit('player');if not map then return end
    local v=C_Map.GetPlayerMapPosition(map,'player');if not v then return end
    local x,y=v:GetXY()
    local p={map=map,x=x,y=y,name=name or category,category=category,description='Recorded at your interaction location.',access=UnitFactionGroup('player')=='Horde' and 'H' or 'A'}
    if not A.ValidPin(p) then return end
    for _,old in ipairs(A.db.observed) do
        if A.ValidPin(old) and old.map==map and old.category==category and math.abs(old.x-x)<.003 and math.abs(old.y-y)<.003 then return end
    end
    table.insert(A.db.observed,p)
end
