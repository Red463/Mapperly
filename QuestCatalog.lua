local _,A=...
local C={};A.QuestCatalog=C
local function number(v) return not (issecretvalue and issecretvalue(v)) and type(v)=='number' and v==v and math.abs(v)<math.huge end
local function text(v) return not (issecretvalue and issecretvalue(v)) and type(v)=='string' and v or '' end
local function read(fn,...)
    if type(fn)~='function' then return end
    local ok,a,b,c=pcall(fn,...);if ok then return a,b,c end
end
local function flag(v)
    if issecretvalue and issecretvalue(v) then return end
    if v==true or v==1 then return true elseif v==false or v==0 then return false end
end
local function api(name) return C_QuestLog and C_QuestLog[name] end
local indexed,index={},{}
local function data()
    local d=A.QuestCatalogData
    return d and d.version==1 and type(d.quests)=='table' and d.quests or nil
end
local function refreshIndex()
    local quests=data()
    if indexed==quests then return end
    indexed=quests;index={}
    local order=A.QuestCatalogData and A.QuestCatalogData.searchOrder
    if type(order)=='table' then
        for _,id in ipairs(order) do
            local row=quests[id]
            if row and text(row.title)~='' then index[#index+1]={id=id,title=row.title:lower()} end
        end
        return
    end
    for id,row in pairs(quests or {}) do
        if number(id) and id>0 and type(row)=='table' and text(row.title)~='' then index[#index+1]={id=id,title=row.title:lower()} end
    end
    table.sort(index,function(a,b) return a.title==b.title and a.id<b.id or a.title<b.title end)
end
local function context()
    local active,why=A.QuestNavigation.Search('');local set={}
    for _,q in ipairs(active) do set[q.id]=q end
    local _,_,race=read(UnitRace,'player');local _,_,class=read(UnitClass,'player')
    local side=read(UnitFactionGroup,'player');side=side=='Alliance' and 'A' or side=='Horde' and 'H' or nil
    local level=read(UnitLevel,'player')
    if not number(level) or level<=0 then level=nil end
    if not number(race) or race<=0 then race=nil end
    if not number(class) or class<=0 then class=nil end
    return {active=set,activeReady=not why,level=level,race=race,class=class,side=side,completed={}}
end
local function onQuest(ctx,id)
    if ctx.active[id] then return true end
    local known=flag(read(api('IsOnQuest'),id))
    if known~=nil then return known end
    if ctx.activeReady then return false end
end
local function completed(ctx,id)
    if ctx.completed[id]~=nil then return ctx.completed[id] end
    local v=flag(read(api('IsQuestFlaggedCompleted') or IsQuestFlaggedCompleted,id))
    ctx.completed[id]=v;return v
end
local function record(id,ctx)
    local meta=data() and data()[id]
    if type(meta)~='table' then return end
    local blocked,unknown={},{}
    local function restrict(reason) blocked[#blocked+1]=reason end
    local function uncertain(reason) unknown[#unknown+1]=reason end
    local active=onQuest(ctx,id)
    if active then restrict('Already in your active quest log. Use Active quests.') elseif active==nil then uncertain('Active quest status is unavailable.') end
    local done=completed(ctx,id)
    if meta.repeatable then uncertain('Repeatable quest: current reset and pickup availability need checking in-game.')
    elseif done==true then restrict('Already completed on this character.')
    elseif done==nil then uncertain('Character completion history is unavailable.') end
    if meta.disabled then restrict('This quest is disabled in the bundled snapshot.') end
    if meta.minLevel and meta.minLevel>0 then
        if not number(ctx.level) then uncertain('Your level is unavailable.')
        elseif ctx.level<meta.minLevel then restrict('Requires level '..meta.minLevel..'.') end
    end
    if meta.maxLevel and meta.maxLevel>0 then
        if not number(ctx.level) then uncertain('Your level is unavailable.')
        elseif ctx.level>meta.maxLevel then restrict('Maximum pickup level is '..meta.maxLevel..'.') end
    end
    local function identity(ids,value,label)
        if type(ids)~='table' or #ids==0 then return end
        if not number(value) then uncertain('Your '..label..' is unavailable.');return end
        for _,id in ipairs(ids) do if id==value then return end end
        restrict('Not offered to your '..label..' in the snapshot.')
    end
    identity(meta.raceIDs,ctx.race,'race');identity(meta.classIDs,ctx.class,'class')
    if #(meta.starters or {})==0 then uncertain('No verified starter location is bundled.')
    else
        local friendly=false
        for _,p in ipairs(meta.starters) do if not p.faction or p.faction=='AH' or p.faction==ctx.side then friendly=true;break end end
        if not friendly then
            if not ctx.side then uncertain('Your faction is unavailable.')
            elseif not meta.startItemIDs or #meta.startItemIDs==0 then restrict('No recorded starter is available to your faction.') end
        end
    end
    local previous=meta.prevQuestID
    if number(previous) and previous~=0 then
        local prior=data()[math.abs(previous)];local name=prior and prior.title or 'quest '..math.abs(previous)
        if previous>0 then
            local v=completed(ctx,previous)
            if v==false then restrict('Complete '..name..' first.') elseif v==nil then uncertain('Prerequisite completion is unavailable: '..name..'.') end
        else
            local id=-previous;local on=onQuest(ctx,id)
            local q=ctx.active[id]
            local ready=q and q.complete;local failed=q and q.failed
            if ready==nil then ready=flag(read(api('IsComplete'),id)) end
            if failed==nil then failed=flag(read(api('IsFailed'),id)) end
            if on==false or ready==true or failed==true then restrict('Requires '..name..' to be in progress.')
            elseif on==nil or ready==nil or failed==nil then uncertain('The required in-progress quest state is unavailable.') end
        end
    end
    if meta.requiredSkillID and meta.requiredSkillID~=0 then uncertain('Skill requirements need checking in-game.') end
    for _,id in ipairs(meta.dependentBreadcrumbIDs or {}) do
        local state=onQuest(ctx,id);local other=data()[id];local name=other and other.title or 'quest '..id
        if state==true then restrict('Finish or abandon '..name..' first.')
        elseif state==nil then uncertain('Breadcrumb quest state is unavailable: '..name..'.') end
    end
    if meta.requiredMinRepFaction and meta.requiredMinRepFaction~=0 or meta.requiredMaxRepFaction and meta.requiredMaxRepFaction~=0 then uncertain('Reputation requirements need checking in-game.') end
    if meta.exclusiveGroup and meta.exclusiveGroup~=0 then uncertain('Exclusive quest-group requirements need checking in-game.') end
    if meta.availabilityUnverified then uncertain('Additional snapshot or live realm requirements are unconfirmed.') end
    local status=#blocked>0 and 'unavailable' or #unknown>0 and 'unknown' or 'possible'
    local available
    if status=='possible' then available=true elseif status=='unavailable' then available=false end
    return {id=id,title=meta.title,level=meta.level,catalog=true,status=status,available=available,
        active=active,reason=blocked[1] or unknown[1] or 'Possible pickup: no known restrictions found in the snapshot.',requirements=blocked,uncertainties=unknown}
end
function C.Find(id) return record(id,context()) end
function C.Search(query)
    query=text(query):lower():match('^%s*(.-)%s*$')
    if query=='' or #query<2 and not tonumber(query) then return {},'Enter at least two letters or an exact quest ID.' end
    if not data() then return {},'The bundled quest catalogue is unavailable.' end
    refreshIndex();local ctx=context();local results={}
    local exact=tonumber(query)
    if exact and data()[exact] then local q=record(exact,ctx);return q.active and {} or {q} end
    for _,entry in ipairs(index) do
        if entry.title:find(query,1,true) then
            local q=record(entry.id,ctx)
            if not q.active then
                if #results>=100 then return results,'Showing the first 100 matches. Narrow your search.' end
                results[#results+1]=q
            end
        end
    end
    return results,#results==0 and 'No quests in the bundled catalogue match your search.' or nil
end
function C.Locations(id)
    local q=C.Find(id);local meta=data() and data()[id]
    if not q then return {},'This quest is not in the bundled catalogue.' end
    local side=read(UnitFactionGroup,'player');side=side=='Alliance' and 'A' or side=='Horde' and 'H' or nil
    local result,seen={},{}
    for _,starter in ipairs(meta.starters or {}) do
        if not starter.faction or starter.faction=='AH' or starter.faction==side then
            local p=A.QuestNavigation.Project(starter)
            if p then
                local key=string.format('catalog:%d:%d:%.9f:%.9f',id,p.map,p.x,p.y)
                if not seen[key] then
                    seen[key]=true
                    local info=read(C_Map and C_Map.GetMapInfo,p.map)
                    local label=text(starter.label);if label=='' then label='Quest starter' end
                    result[#result+1]={map=p.map,x=p.x,y=p.y,questID=id,questTitle=q.title,name=(q.title..' - '..label):sub(1,120),label=label,
                        catalog=true,kind='queststart',source='snapshot',zone=info and text(info.name)~='' and info.name or 'Map '..p.map,key=key,
                        available=q.available,availabilityStatus=q.status,availabilityReason=q.reason}
                end
            end
        end
    end
    local why
    if #result==0 then
        why='No verified starter location is available for this quest and faction.'
        if meta.startItemIDs and #meta.startItemIDs>0 then why=why..' It may begin with an item; no item-drop location is inferred.' end
    end
    return result,why,q
end
function C.Resolve(selected)
    local q=C.Find(selected.questID)
    if not q then return nil,'This quest is not in the bundled catalogue.' end
    if q.available==false then return nil,q.reason end
    local locations,why=C.Locations(selected.questID)
    for _,p in ipairs(locations) do if p.key==selected.key then return p end end
    return nil,why or 'The starter location changed. Choose it again.'
end
