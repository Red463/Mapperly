local _,A=...
local R={};A.RouteReport=R
local requests={}
local function readable(v) return not (issecretvalue and issecretvalue(v)) end
local function scalar(v)
    if not readable(v) then return 'unavailable' end
    if type(v)=='string' then return v:sub(1,360) end
    if type(v)=='boolean' then return v and 'true' or 'false' end
    if type(v)=='number' and v==v and math.abs(v)<math.huge then return string.format('%.6g',v) end
    return 'unavailable'
end
local function call(fn,...)
    if type(fn)~='function' then return end
    local ok,v=pcall(fn,...);if ok and readable(v) then return v end
end
local function position(p)
    if not readable(p) or type(p)~='table' then return 'unavailable' end
    return 'map='..scalar(p.map or p.mapID)..' x='..scalar(p.x)..' y='..scalar(p.y)
end
local function fields(p,keys)
    local out={};if not readable(p) or type(p)~='table' then return '' end
    for _,key in ipairs(keys) do if not readable(p[key]) or p[key]~=nil then out[#out+1]=key..'='..scalar(p[key]) end end
    return table.concat(out,' ')
end
function R.RecordRequest(candidate,reason,start)
    requests[#requests+1]={destination=position(candidate),start=position(start),reason=scalar(reason)}
    while #requests>4 do table.remove(requests,1) end
end
local function redact(report)
    for _,private in ipairs({call(UnitGUID,'player') or false,call(UnitName,'player') or false,call(GetRealmName) or false}) do
        if type(private)=='string' and #private>0 then
            report=report:gsub(private:gsub('([^%w])','%%%1'),'[private]')
        end
    end
    -- Reports are plain, copyable text. Never permit injected game hyperlinks.
    return report:gsub('|','/'):sub(1,16000)
end
function R.Build()
    local N,J=A.Navigation or {},A.Journey or {};local db=A.db or {};local lines={}
    local function add(label,value) lines[#lines+1]=label..': '..value end
    add('Mapperly route report',scalar(A.version));add('Client',scalar(call(GetBuildInfo)))
    if type(GetBuildInfo)=='function' then
        local ok,_,build,_,interface=pcall(GetBuildInfo)
        if ok then add('Client build',scalar(build)..' interface='..scalar(interface)) end
    end
    local start=J.PlayerPosition and call(J.PlayerPosition)
    add('Actual position',position(start));add('Destination',position(N.deferredRoutingTarget or N.target));add('Pending destination',position(N.pending))
    local native={}
    if type(UnitPosition)=='function' then
        local ok,north,east,z,instance=pcall(UnitPosition,'player')
        if ok then native={north=north,east=east,z=z,instance=instance} end
    end
    add('Native position','north='..scalar(native.north)..' east='..scalar(native.east)..' z='..scalar(native.z)..' instance='..scalar(native.instance))
    add('Movement flags','swimming='..scalar(call(IsSwimming))..' taxi='..scalar(call(UnitOnTaxi,'player'))..' vehicle='..scalar(call(UnitInVehicle,'player')))
    add('Options',fields(db,{'navigationMode','preferRoads','roadPreferenceStrength','allowSwimming','avoidSwimming','rememberJourney'}))
    add('Journey',fields(J,{'paused','index','legIndex','crossing','inStructure','structureIndex'}))
    local leg=J.Leg and call(J.Leg)
    add('Current step',fields(leg,{'kind','mapID','first','last'}))
    if readable(leg) and type(leg)=='table' and readable(leg.transport) and type(leg.transport)=='table' then add('Method',fields(leg.transport,{'kind','id','source','verified'})) end
    add('Plan',fields(J.active,{'kind','mapID','distance','estimatedSeconds','coverage','source'}))
    add('Planning error',scalar(N.planningError));add('Recovery error',scalar(N.recoveryError))
    if A.WaterData then add('Water data',fields(A.WaterData,{'version','source','build','coverage'})) end
    local water='unavailable'
    if type(start)=='table' and readable(start) and readable(start.mapID) and type(start.mapID)=='number' and A.Terrain and A.Water then
        local zone=call(A.Terrain.Zone,start.mapID)
        local native=zone and call(A.Water.Zone,start.mapID,zone)
        water='map='..scalar(start.mapID)..' '..(native and 'native liquid grid matched to terrain' or 'unknown (no matching native liquid grid)')
        if native then add('Water source',fields(native,{'source','baseSha256','w','h','status'})) end
    end
    add('Water coverage',water)
    if A.PathReuse and A.PathReuse.Stats then add('Path reuse cache',fields(call(A.PathReuse.Stats),{'hits','bakedHits','misses','entries','points','contexts'})) end
    if A.TerrainData then add('Terrain source',fields(A.TerrainData,{'version','source','build'})) end
    local counterKeys={'id','stage','paths','cells','mapID','checked','total','flightRoutes','flightSources','cacheHits','cacheMisses','source','waterCells','waterUnknown','waterRejected'}
    local progress=A.PlanningJob and A.PlanningJob.Progress()
    if progress then add('Active calculation',fields(progress,counterKeys)) end
    for _,row in ipairs(A.PlanningJob and A.PlanningJob.Recent and A.PlanningJob.Recent() or {}) do
        add('Recent calculation',fields(row,{'state','elapsedMS','reason','kind','coverage','source','distance'}))
        add('Calculation destination',position(row.destination));add('Calculation counters',fields(row.progress,counterKeys))
    end
    for _,row in ipairs(requests) do add('Rejected request',row.destination..' from '..row.start..' reason='..row.reason) end
    return redact(table.concat(lines,'\n'))
end
function R.Open()
    local U=A.Dialogs;local f=R.frame
    if not f then
        f=U.CompactWindow(UIParent,650,480);R.frame=f;f:SetPoint('CENTER');f:SetFrameStrata('DIALOG');f:SetClampedToScreen(true);f:EnableMouse(true)
        U.Label(f,'Route report',18,12,'GameFontNormalLarge')
        U.Label(f,'Select the text and press Ctrl+C to copy. Nothing is sent automatically.',18,44,'GameFontDisableSmall')
        local scroll=CreateFrame('ScrollFrame',nil,f,'UIPanelScrollFrameTemplate');scroll:SetPoint('TOPLEFT',f,'TOPLEFT',18,-76);scroll:SetSize(588,344)
        local edit=U.Input(scroll,0,0,584,344,16000,true);f.edit=edit;scroll:SetScrollChild(edit)
        edit:SetScript('OnEscapePressed',function() f:Hide() end)
        edit:SetScript('OnTextChanged',function(self,user) if user then self:SetText(f.report or '') end end)
        U.Action(f,'Refresh',390,438,112,function() R.Open() end)
        U.Action(f,'Close',518,438,112,function() f:Hide() end)
    end
    f.report=R.Build();f.edit:SetText(f.report);f.edit:SetHeight(math.max(344,select(2,f.report:gsub('\n',''))*15+24));U.Show(f)
    f.edit:SetFocus();f.edit:HighlightText()
end
