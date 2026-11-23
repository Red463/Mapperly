local _,A=...
local Q={};A.QuestNavigation=Q
local function public(v) return not (issecretvalue and issecretvalue(v)) end
local function number(v) return public(v) and type(v)=='number' and v==v and math.abs(v)<math.huge end
local function text(v) return public(v) and type(v)=='string' and v~='' and v or nil end
local function flag(v)
    if not public(v) then return end
    if v==true or v==1 then return true elseif v==false or v==0 then return false end
end
local function read(fn,...)
    if type(fn)~='function' then return end
    local ok,a,b,c,d,e,f,g,h=pcall(fn,...)
    if ok then return a,b,c,d,e,f,g,h end
end
local function api(name) return C_QuestLog and C_QuestLog[name] end
local function objectiveProgress(quest)
    local progress={};local objectives=read(api('GetQuestObjectives'),quest.id)
    if public(objectives) and type(objectives)=='table' then
        for i=1,math.min(#objectives,100) do
            local row=objectives[i]
            if public(row) and type(row)=='table' then
                local id=number(row.objectiveID) and row.objectiveID or row.questObjectiveID
                if number(id) then progress[id]=flag(row.finished) end
            end
        end
    end
    return progress
end
function Q.Search(query)
    query=text(query) or '';query=query:lower():match('^%s*(.-)%s*$')
    local modern=true;local count=read(api('GetNumQuestLogEntries'))
    if not number(count) or type(api('GetInfo'))~='function' then modern=false;count=read(GetNumQuestLogEntries) end
    if not number(count) or count<0 then return {},'Quest log is unavailable. Try again after loading.' end
    local result,seen={},{}
    for i=1,math.min(math.floor(count),1000) do
        local info
        if modern then info=read(api('GetInfo'),i)
        else
            local title,level,_,header,_,complete,_,id=read(GetQuestLogTitle,i)
            info={title=title,level=level,isHeader=header,questID=id,complete=flag(complete),failed=complete==-1}
        end
        if public(info) and type(info)=='table' and flag(info.isHeader)~=true and flag(info.isHidden)~=true then
            local id,title=info.questID,text(info.title)
            if number(id) and id>0 and id%1==0 and title and not seen[id] then
                seen[id]=true
                local complete=flag(read(api('IsComplete'),id))
                if complete==nil then complete=info.complete end
                local failed=flag(read(api('IsFailed'),id))
                if failed==nil then failed=info.failed end
                if query=='' or title:lower():find(query,1,true) or tostring(id):find(query,1,true) then
                    result[#result+1]={id=id,title=title,level=number(info.level) and info.level or nil,complete=complete,failed=failed,logIndex=i}
                end
            end
        end
    end
    table.sort(result,function(a,b) local x,y=a.title:lower(),b.title:lower();return x==y and a.id<b.id or x<y end)
    return result
end
function Q.Find(id)
    local quests,why=Q.Search('')
    for _,quest in ipairs(quests) do if quest.id==id then return quest end end
    return nil,why
end
local function validPin(map,x,y)
    return number(map) and map>0 and map%1==0 and number(x) and number(y) and x>=0 and x<=1 and y>=0 and y<=1 and not (x==0 and y==0)
end
function Q.Project(world)
    if not number(world.worldX) or not number(world.worldY) or not number(world.instance) then return end
    local best,area
    for id,m in pairs(A.CrossingData and A.CrossingData.maps or {}) do
        if m.instance==world.instance and number(m.width) and m.width>0 and number(m.height) and m.height>0 and number(m.west) and number(m.north) then
            local x,y=(m.west-world.worldX)/m.width,(m.north-world.worldY)/m.height
            if validPin(id,x,y) and (not area or m.width*m.height<area or m.width*m.height==area and id<best.map) then
                best={map=id,x=x,y=y};area=m.width*m.height
            end
        end
    end
    return best
end
local function zoneName(map)
    local info=read(C_Map and C_Map.GetMapInfo,map)
    return public(info) and type(info)=='table' and text(info.name) or 'Map '..map
end
function Q.Locations(id)
    local quest,unavailable=Q.Find(id)
    if not quest then return {},unavailable or 'This quest is no longer in your active quest log.' end
    if quest.failed then return {},'This quest has failed; no active destination is available.' end
    local result,keys={},{}
    local function add(pin,kind,label,source,objectiveID,progressUnknown)
        if not pin or not validPin(pin.map,pin.x,pin.y) then return end
        local key=string.format('%s:%d:%.9f:%.9f',kind,pin.map,pin.x,pin.y)
        if keys[key] then return end
        keys[key]=true
        result[#result+1]={map=pin.map,x=pin.x,y=pin.y,name=(quest.title..' - '..label):sub(1,120),
            label=label,questID=quest.id,questTitle=quest.title,kind=kind,source=source,objectiveID=objectiveID,
            progressUnknown=progressUnknown,zone=zoneName(pin.map),key=key}
    end
    -- Native current quest pins are distinct from travel waypoints. Never
    -- select a quest or move the native map just to obtain its coordinates.
    local map=read(GetQuestUiMapID,id,true)
    if number(map) then
        local pins=read(api('GetQuestsOnMap'),map)
        if public(pins) and type(pins)=='table' then
            for i=1,math.min(#pins,500) do
                local p=pins[i]
                if public(p) and type(p)=='table' and public(p.questID) and p.questID==id and flag(p.isQuestStart)~=true and flag(p.isMapIndicatorQuest)~=true then
                    if quest.complete~=true or flag(p.inProgress)~=true then
                        -- Like the native provider, interpret x/y in the map
                        -- passed to GetQuestsOnMap, not another record map ID.
                        add({map=map,x=p.x,y=p.y},quest.complete and 'turnin' or 'objective',quest.complete and 'Turn in quest' or 'Quest objective area','native')
                    end
                end
            end
        end
    end
    local waypoint,x,y=read(api('GetNextWaypoint'),id)
    add({map=waypoint,x=x,y=y},'waypoint','Travel waypoint','native')
    local data=A.QuestLocationData
    local rows=data and data.version==1 and data.quests and data.quests[id]
    local progress=objectiveProgress(quest)
    local side=read(UnitFactionGroup,'player');side=side=='Alliance' and 'A' or side=='Horde' and 'H' or nil
    for i=1,math.min(type(rows)=='table' and #rows or 0,128) do
        local row=rows[i]
        local kind=row.kind;local allowed=kind=='objective' or kind=='turnin'
        if quest.complete==true and kind~='turnin' or quest.complete==false and kind~='objective' then allowed=false end
        if kind=='objective' and row.objectiveID and progress[row.objectiveID]==true then allowed=false end
        if kind=='turnin' and row.faction and row.faction~='AH' and row.faction~=side then allowed=false end
        if allowed then
            local label=text(row.label) or (kind=='turnin' and 'Turn in quest' or 'Quest objective')
            add(Q.Project(row),kind,label,'snapshot',row.objectiveID,kind=='objective' and (not row.objectiveID or progress[row.objectiveID]==nil))
        end
    end
    if #result==0 then return result,'No verified location is available for this quest. Your current navigation is unchanged.' end
    return result
end
function Q.Resolve(selected)
    if type(selected)~='table' then return nil,'Choose a quest location first.' end
    if selected.catalog then return A.QuestCatalog.Resolve(selected) end
    local locations,why=Q.Locations(selected.questID)
    for _,pin in ipairs(locations) do if pin.key==selected.key and pin.source==selected.source then return pin end end
    return nil,why or 'The quest or its location changed. Choose a location again.'
end
function Q.RouteTarget(selected,mode)
    local pin,why=Q.Resolve(selected)
    if not pin then return nil,why end
    if (mode or A.db and A.db.navigationMode)=='direct' or not A.Terrain or not A.Terrain.Zone(pin.map) then return pin end
    local exact={mapID=pin.map,x=pin.x,y=pin.y}
    if A.Terrain.Segment(exact,exact) then return pin end
    -- NPC and object coordinates can be inside a building or a prohibited
    -- root-terrain cell. Route only to nearby permitted ground; do not invent
    -- a walking segment through the excluded area to the exact quest point.
    local approach=A.Terrain.Approach(exact,30)
    local zone=A.Terrain.Zone(pin.map)
    local distance=approach and approach.mapID==pin.map and math.sqrt(((approach.x-pin.x)*zone.widthYards)^2+((approach.y-pin.y)*zone.heightYards)^2)
    if not distance or distance>30.000001 or not A.Terrain.Segment(approach,approach) then
        return nil,'No walkable nearby approach is available within 30 yards of this quest location. Your current navigation is unchanged.'
    end
    local target={};for k,v in pairs(pin) do target[k]=v end
    target.questTarget={map=pin.map,x=pin.x,y=pin.y,name=pin.name}
    target.x=approach.x;target.y=approach.y;target.approachDistance=distance
    target.name=pin.name:sub(1,109)..' (approach)'
    return target
end
