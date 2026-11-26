local _,A=...
-- Reuse only walking geometry. Transport permissions and proven dock floors
-- remain the responsibility of the journey planner around Terrain.Path.
local R={revision=1};A.PathReuse=R
local T=A.Terrain;local original=T.Path;R.OriginalPath=original
local contexts,cache,order={}, {}, {};local serial,points=0,0
local failures,failureOrder={},{}
local counters={hits=0,bakedHits=0,misses=0,failureHits=0}
local function finite(n) return type(n)=='number' and n==n and math.abs(n)<math.huge end
local function valid(p) return type(p)=='table' and finite(p.mapID) and finite(p.x) and finite(p.y) and p.x>=0 and p.x<=1 and p.y>=0 and p.y<=1 end
local function copy(path,reverse)
    if type(path)~='table' or #path<1 or #path>2048 then return end
    for k in pairs(path) do if not finite(k) or k%1~=0 or k<1 or k>#path then return end end
    local result={}
    for i=1,#path do local p=path[reverse and #path-i+1 or i];if not valid(p) then return end;result[i]={mapID=p.mapID,x=p.x,y=p.y} end
    return result
end
function R.Key(a,b)
    local first=string.format('%.17g,%.17g',a.x,a.y);local last=string.format('%.17g,%.17g',b.x,b.y)
    if first>last then return a.mapID..':'..last..':'..first,true end
    return a.mapID..':'..first..':'..last,false
end
local function snapshot(rows) local r={};for i,v in ipairs(rows or {}) do r[i]=v end;return r end
local function same(rows,saved)
    if #(rows or {})~=#saved then return false end
    for i,v in ipairs(saved) do if rows[i]~=v then return false end end
    return true
end
local function signature(z,roads,factor,dry,water)
    -- Adler32 over resolved row contents, with lengths and separators. This
    -- detects stale generated inputs; SHA256 source proofs live in the build
    -- manifest. Runtime does not depend on a crypto library.
    local a,b,work=1,0,0
    local function feed(value)
        local s=tostring(value);s=#s..':'..s..';'
        for i=1,#s do
            a=(a+s:byte(i))%65521;b=(b+a)%65521
            if i%4096==0 and T.Checkpoint then T.Checkpoint() end
        end
        work=work+#s
        if work>=8192 then work=0;if T.Checkpoint then T.Checkpoint() end end
    end
    feed(R.revision)
    for _,v in ipairs({z.w,z.h,z.widthYards,z.heightYards,z.status,factor}) do feed(v) end
    for _,rows in ipairs({z.rows,z.groundRows or {},roads and roads.rows or {}}) do
        feed(#rows);for _,row in ipairs(rows) do feed(row) end
    end
    -- Allowed-mode geometry and signatures are byte-for-byte compatible with
    -- revision 1. Dry mode has its own policy and native-liquid input identity.
    if dry then
        feed('no-swimming-v1');feed(water and water.baseSha256 or 'unknown')
        local rows=water and water.rows or {};feed(#rows);for _,row in ipairs(rows) do feed(row) end
    end
    return string.format('%d:%d',a,b)
end
local function context(map,options)
    local z=T.Zone(map);if not z then return end
    local dry=A.Water and not A.Water.AllowSwimming(options) or not A.Water and (options.allowSwimming==false or options.allowSwimming==nil and A.db and A.db.allowSwimming==false) or false
    local water=dry and A.Water and A.Water.Zone(map,z) or nil
    local roads=options.preferRoads and A.Roads and A.Roads.Zone(map,z)
    local mode=roads and select(1,A.Roads.Strength(options.roadPreferenceStrength)) or 0
    local factor=roads and select(3,A.Roads.Strength(options.roadPreferenceStrength)) or 1
    local roadCell=roads and A.Roads.Cell;local waterCell=water and A.Water.Cell
    for i,c in ipairs(contexts) do
        if c.map==map and c.mode==mode and c.z==z and c.roads==roads and c.factor==factor and c.dry==dry and c.water==water and same(water and water.rows,c.waterRows) and
            c.segment==T.Segment and c.roadCell==roadCell and c.waterCell==waterCell and c.guide==A.WalkingPortalData and
            c.w==z.w and c.h==z.h and c.width==z.widthYards and c.height==z.heightYards and c.status==z.status and
            same(z.rows,c.rows) and same(z.groundRows,c.ground) and same(roads and roads.rows,c.roadRows) then
            table.remove(contexts,i);contexts[#contexts+1]=c;return c
        end
    end
    serial=serial+1
    local c={id=serial,map=map,mode=mode,z=z,roads=roads,factor=factor,w=z.w,h=z.h,width=z.widthYards,height=z.heightYards,status=z.status,
        rows=snapshot(z.rows),ground=snapshot(z.groundRows),roadRows=snapshot(roads and roads.rows),dry=dry,water=water,waterRows=snapshot(water and water.rows),
        segment=T.Segment,roadCell=roadCell,waterCell=waterCell,guide=A.WalkingPortalData}
    c.signature=signature(z,roads,factor,dry,water);contexts[#contexts+1]=c
    if #contexts>16 then
        local evicted=table.remove(contexts,1).id
        for i=#order,1,-1 do local key=order[i];local e=cache[key]
            if e.context==evicted then points=points-#e.path;cache[key]=nil;table.remove(order,i) end
        end
        for i=#failureOrder,1,-1 do local key=failureOrder[i]
            if failures[key].context==evicted then failures[key]=nil;table.remove(failureOrder,i) end
        end
    end
    return c
end
function R.Signature(map,options)
    local c=context(map,options or {});return c and c.signature,c and c.mode
end
local function geometry(path,a,b,length,z,options)
    if type(path)~='table' or #path<1 or #path>2048 or not finite(length) or length<0 then return false end
    local first,last=path[1],path[#path]
    if not valid(first) or not valid(last) or first.mapID~=a.mapID or last.mapID~=b.mapID or first.x~=a.x or first.y~=a.y or last.x~=b.x or last.y~=b.y then return false end
    local measured=0
    for i,p in ipairs(path) do
        if not valid(p) or p.mapID~=a.mapID or not T.Segment(path[math.max(1,i-1)],p,options) then return false end
        if i>1 then local q=path[i-1];measured=measured+math.sqrt(((p.x-q.x)*z.widthYards)^2+((p.y-q.y)*z.heightYards)^2) end
        if i%32==0 and T.Checkpoint then T.Checkpoint() end
    end
    return math.abs(measured-length)<.00001
end
local function remember(key,c,path,length,reverse)
    if #path>2048 then return end
    if cache[key] then points=points-#cache[key].path;cache[key]=nil;for i,k in ipairs(order) do if k==key then table.remove(order,i);break end end end
    while #order>=512 or points+#path>16384 do local old=table.remove(order,1);points=points-#cache[old].path;cache[old]=nil end
    cache[key]={path=copy(path,reverse),length=length,context=c.id};order[#order+1]=key;points=points+#path
end
local function effectiveBudget(options)
    local budget=options.maxExpansions or options.budget or 16384
    if finite(budget) and budget>=0 then return math.min(262144,math.floor(budget)) end
end
local function rememberFailure(key,c,budget)
    local previous=failures[key]
    if previous then previous.budget=math.max(previous.budget,budget);return end
    if #failureOrder>=512 then failures[table.remove(failureOrder,1)]=nil end
    failures[key]={context=c.id,budget=budget};failureOrder[#failureOrder+1]=key
end
function R.Clear() contexts={};cache={};order={};points=0;failures={};failureOrder={} end
function R.Stats()
    return {hits=counters.hits,bakedHits=counters.bakedHits,misses=counters.misses,failureHits=counters.failureHits,
        entries=#order,points=points,contexts=#contexts,failureEntries=#failureOrder}
end
function T.Path(a,b,options)
    options=type(options)=='table' and options or {}
    if not valid(a) or not valid(b) or a.mapID~=b.mapID or options.maxDistance~=nil and (not finite(options.maxDistance) or options.maxDistance<0) then return original(a,b,options) end
    local c=context(a.mapID,options);if not c then return original(a,b,options) end
    local pair,reverse=R.Key(a,b);local key=c.id..':'..pair
    local hit=cache[key];local path,length
    if hit then
        path=copy(hit.path,reverse);length=hit.length
        -- Same source context, but still honor a changed live segment guard.
        if path then for i,p in ipairs(path) do
            if not T.Segment(path[math.max(1,i-1)],p,options) then path=nil;break end
            if i%32==0 and T.Checkpoint then T.Checkpoint() end
        end end
    end
    local baked=false
    if not path then
        local data=A.WalkingPathData
        local zone=type(data)=='table' and data.version==1 and data.revision==R.revision and type(data.zones)=='table' and data.zones[a.mapID]
        local mode=type(zone)=='table' and zone[c.mode]
        local entry=type(mode)=='table' and mode.signature==c.signature and type(mode.paths)=='table' and mode.paths[pair]
        if type(entry)=='table' and type(entry.points)=='table' then
            local candidate=copy(entry.points,reverse)
            if geometry(candidate,a,b,entry.length,c.z,options) then path=candidate;length=entry.length;baked=true;remember(key,c,path,length,reverse) end
        end
    end
    -- A verified unrestricted route can include a guide or road detour.
    -- Its length does not prove a shorter bounded query is impossible.
    -- Retain it while the bounded core search answers that separate query.
    local rangeRetry=path and options.maxDistance and length>options.maxDistance+.000001
    if path and not rangeRetry then
        if A.PlanningJob then A.PlanningJob.BeginPath(a.mapID) end
        counters.hits=counters.hits+1;if baked then counters.bakedHits=counters.bakedHits+1 end
        return path,length
    end
    -- Exhaustion records only work already attempted, never unreachability.
    -- A finite A* allowance is directional; a different range changes its
    -- search order too. Larger allowances must always get a fresh attempt.
    local budget=effectiveBudget(options)
    local failureKey=key..':'..(reverse and 'reverse' or 'forward')..':'..(options.maxDistance and string.format('%.17g',options.maxDistance) or 'unlimited')
    -- Hierarchical searches split the allowance between stages. Unlike a
    -- single A* frontier, smaller allowances need not follow the same order.
    if budget and budget>=16384 and not options.maxDistance and c.guide then
        failureKey=failureKey..':guided:'..budget
    end
    local failed=failures[failureKey]
    if failed and budget and budget<=failed.budget and T.Segment(a,a,options) and T.Segment(b,b,options) then
        local direct=math.sqrt(((a.x-b.x)*c.z.widthYards)^2+((a.y-b.y)*c.z.heightYards)^2)
        if (not options.maxDistance or direct<=options.maxDistance+.000001) and (c.roads or not T.Segment(a,b,options)) then
            if A.PlanningJob then A.PlanningJob.BeginPath(a.mapID) end
            counters.failureHits=counters.failureHits+1;return nil,'budget'
        end
    end
    counters.misses=counters.misses+1
    -- A miss must not inherit the legacy cache's stale mutable road/ground rows.
    if T.ClearPathCache then T.ClearPathCache() end
    path,length=original(a,b,options)
    if path and not rangeRetry then remember(key,c,path,length,reverse)
    elseif length=='budget' and budget then rememberFailure(failureKey,c,budget) end
    return path,length
end
