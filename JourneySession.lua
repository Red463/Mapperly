local _,A=...
local S={};A.JourneySession=S
local pending,resuming,driver
local function readable(v) return not (issecretvalue and issecretvalue(v)) end
local function number(v) return readable(v) and type(v)=='number' and v==v and math.abs(v)<math.huge end
local function text(v,n) if readable(v) and type(v)=='string' then return v:sub(1,n or 120) end end
local function flag(v) return readable(v) and (v==nil or type(v)=='boolean') end
local function call(fn,...)
    if type(fn)~='function' then return end
    local ok,v=pcall(fn,...);if ok and readable(v) then return v end
end
local function guid() return text(call(UnitGUID,'player'),100) end
local function build()
    local interface,client
    if type(GetBuildInfo)=='function' then
        local ok,_,c,_,v=pcall(GetBuildInfo)
        if ok then client=text(c,40);if number(v) then interface=v end end
    end
    return (text(A.version) or 'unknown')..':'..(client or 'unknown')..':'..tostring(interface or 'unknown')
end
local function target(p)
    if type(p)~='table' or not readable(p) then return end
    if not flag(p.walkingOnly) then return end
    local m=p.map or p.mapID
    if not number(m) or m<1 or m%1~=0 or not number(p.x) or not number(p.y) or p.x<0 or p.x>1 or p.y<0 or p.y>1 then return end
    return {map=m,x=p.x,y=p.y,name=text(p.name) or 'Destination',walkingOnly=p.walkingOnly==true or nil}
end
local function profile(p)
    p=type(p)=='table' and p or {}
    local strength=number(p.roadPreferenceStrength) and math.max(1,math.min(5,p.roadPreferenceStrength)) or 3
    return {navigationMode=p.navigationMode=='direct' and 'direct' or 'terrain',preferRoads=p.preferRoads~=false,
        roadPreferenceStrength=strength,allowSwimming=p.allowSwimming~=false,avoidSwimming=p.avoidSwimming==true}
end
local function valid(row)
    if type(row)~='table' or row.schema~=1 or not text(row.build,160) then return end
    if not flag(row.paused) or not flag(row.transit) or not flag(row.manualFloor) then return end
    local t=target(row.target);if not t then return end
    return {schema=1,build=text(row.build,160),target=t,profile=profile(row.profile),paused=row.paused==true,
        transit=row.transit==true or row.manualFloor==true,manualFloor=row.manualFloor==true,savedAt=number(row.savedAt) and row.savedAt or 0}
end
function S.Normalize(db)
    if type(db)~='table' then return end
    local rows=type(db.journeySessions)=='table' and db.journeySessions or {};local list={}
    for key,row in pairs(rows) do
        local entry=text(key,100) and valid(row)
        if entry and #key<=100 then list[#list+1]={key=key,row=entry} end
    end
    local current=guid()
    table.sort(list,function(a,b)
        if a.key==current or b.key==current then return a.key==current end
        if a.row.savedAt==b.row.savedAt then return a.key<b.key end;return a.row.savedAt>b.row.savedAt
    end)
    db.journeySessions={};for i=1,math.min(8,#list) do db.journeySessions[list[i].key]=list[i].row end
end
local function hide() if S.frame then S.frame:Hide() end end
function S.Intent() pending=nil;resuming=nil;hide();if driver then driver:Hide() end end
function S.Clear()
    S.Intent();local key=guid();if key and A.db and type(A.db.journeySessions)=='table' then A.db.journeySessions[key]=nil end
end
function S.Capture(candidate)
    local db=A.db;local key=guid()
    if not db or db.rememberJourney==false or not key then return false end
    local N,J=A.Navigation or {},A.Journey
    local selected=candidate or N.deferredRoutingTarget or N.target
    local t=target(selected);if not t then return false end
    local leg=J and J.Leg and J.Leg()
    local manualFloor=selected.recordedConnection~=nil or leg and leg.transport and leg.transport.recorded==true or false
    local state=J and J.transportState
    local transit=leg and leg.kind=='transport' and (not state or not state.arrived) or J and (J.crossing or J.inStructure) or false
    transit=transit or A.Flights and A.Flights.OnTaxi and A.Flights.OnTaxi()==true or false
    db.journeySessions=type(db.journeySessions)=='table' and db.journeySessions or {}
    db.journeySessions[key]={schema=1,build=build(),target=t,profile=profile(db),paused=J and J.paused==true or false,
        transit=not not (transit or manualFloor),manualFloor=not not manualFloor,savedAt=call(GetServerTime) or call(time) or 0}
    S.Normalize(db);return true
end
local function same(a,b) return a and b and a.map==b.map and a.x==b.x and a.y==b.y end
function S.Installed(candidate)
    if resuming and same(target(candidate),resuming.target) then
        if A.Journey and A.Journey.active then A.Journey.paused=resuming.paused end
        resuming=nil
    end
    S.Capture(candidate)
end
local function available()
    if A.Flights and A.Flights.OnTaxi and A.Flights.OnTaxi()~=false then return end
    if call(UnitOnTaxi,'player')==true or call(UnitInVehicle,'player')==true or call(IsPlayerMoving)==true then return end
    if type(IsSwimming)=='function' and call(IsSwimming)~=false then return end
    return A.Journey and A.Journey.PlayerPosition and A.Journey.PlayerPosition()
end
local function offer()
    local U=A.Dialogs;if not U then return end
    local f=S.frame
    if not f then
        f=U.CompactWindow(UIParent,390,190);S.frame=f;f:SetPoint('CENTER');f:SetFrameStrata('DIALOG');f:SetClampedToScreen(true);f:EnableMouse(true)
        U.Label(f,'Resume your journey?',16,10,'GameFontNormal')
        f.detail=U.Label(f,'',16,42,'GameFontHighlightSmall');f.detail:SetSize(358,92);f.detail:SetWordWrap(true);f.detail:SetJustifyH('LEFT')
        f.resume=U.Action(f,'Resume',16,148,218,function() S.Resume(pending and pending.transit==true) end)
        f.discard=U.Action(f,'Discard',246,148,128,S.Clear)
        f:Hide()
    end
    if f:IsShown() then return end
    f.resume:SetText(pending.transit and 'On land: Resume' or 'Resume')
    local p=pending.target
    local label=(p.name or 'Destination'):gsub('[%c]',' '):sub(1,44):gsub('|','||')
    local destination=string.format('%s\nMap %d: %.1f, %.1f\n\n',label,p.map,p.x*100,p.y*100)
    f.detail:SetText(destination..(pending.manualFloor and 'Complete recorded ride manually and stand on correct destination floor before resuming.' or pending.transit and 'Disembark onto safe land, then confirm to replan using current navigation settings.' or 'Replans from your actual position using current navigation settings. Your saved paused state will be kept.'))
    U.Show(f)
end
function S.Poll()
    if not pending then return end
    local key=guid()
    if not A.db or A.db.rememberJourney==false or key~=pending.guid or pending.build~=build() then S.Intent();return end
    if A.Navigation and (A.Navigation.target or A.Navigation.pending or A.Navigation.deferredRoutingTarget) then S.Intent();return end
    if not available() then hide();return end
    offer()
end
function S.Resume(onLand)
    local row=pending
    local current=available()
    if not row or not current then return nil,'Wait until you are on land and your position is available.' end
    if row.transit and onLand~=true then return nil,'Confirm you have disembarked onto safe land first.' end
    if row.guid~=guid() or row.build~=build() or A.db.rememberJourney==false then S.Intent();return nil,'The saved journey is no longer available.' end
    if row.manualFloor then
        local P,T=A.TravelNetwork,A.Terrain
        local destination={mapID=row.target.map,x=row.target.x,y=row.target.y}
        local distance=P and P.Distance(current,destination)
        if not number(distance) or distance>18 or not T or not T.Segment(current,current) or not T.Segment(destination,destination) then
            return nil,'Complete the recorded ride manually and stand on its safe destination floor within 18 yards before resuming.'
        end
        local joined=current.mapID==destination.mapID and current or P.Transform(current,destination.mapID)
        if not joined or not T.Segment(joined,destination) then return nil,'The short approach to the saved destination is blocked.' end
        local ok,north,east,_,instance
        if type(UnitPosition)=='function' then ok,north,east,_,instance=pcall(UnitPosition,'player') end
        local x,y,i=P.World(current)
        if not ok or not number(north) or not number(east) or not number(instance) or not number(x) or not number(y) or not number(i) or instance~=i or (east-x)^2+(north-y)^2>=64 then
            return nil,'Wait for matching native world and map coordinates on the correct destination floor.'
        end
    end
    resuming=row
    local p=row.target
    local ok,why=A.Navigation.Start(p.map,p.x*100,p.y*100,p.name,{sessionResume=true,mode=A.db.navigationMode,walkingOnly=p.walkingOnly})
    if ok then pending=nil;hide();if driver then driver:Hide() end
    else resuming=nil;if S.frame then S.frame.detail:SetText(text(why,240) or 'Unable to calculate this route yet.') end end
    return ok,why
end
-- World transitions may precede SavedVariables initialization or a readable GUID.
-- Retry on a throttled frame rather than assuming event ordering or map readiness.
local events=CreateFrame('Frame',nil,UIParent)
S.events=events
events:RegisterEvent('PLAYER_ENTERING_WORLD');events:RegisterEvent('PLAYER_LOGOUT')
local waiting,age=false,0
events:SetScript('OnEvent',function(_,event)
    if event=='PLAYER_LOGOUT' then S.Capture()
    else waiting=true;age=0 end
end)
events:SetScript('OnUpdate',function(_,dt)
    if not waiting then return end
    age=age+dt;if age<1 then return end;age=0
    if A.db and guid() then waiting=false;S.OnWorldReady() end
end)
function S.OnWorldReady()
    if resuming then return end
    S.Intent();if not A.db or A.db.rememberJourney==false then return end
    S.Normalize(A.db)
    local key=guid();local row=key and A.db.journeySessions[key]
    if not row or row.build~=build() then return end
    pending=valid(row);pending.guid=key
    if not driver then
        driver=CreateFrame('Frame',nil,UIParent);local elapsed=0
        driver:SetScript('OnUpdate',function(_,dt) elapsed=elapsed+dt;if elapsed>=1 then elapsed=0;S.Poll() end end)
    end
    driver:Show()
end
function S.Open()
    if not A.db or A.db.rememberJourney==false then return nil,'Enable Remember journey before resuming a saved destination.' end
    if A.Navigation and (A.Navigation.target or A.Navigation.pending or A.Navigation.deferredRoutingTarget) then return nil,'A journey is already active or being calculated.' end
    S.OnWorldReady();S.Poll()
    if not pending then return nil,'No compatible saved journey is available for this character and build.' end
    if not available() then return nil,'Wait until you are on land and your position is available. The resume offer will appear then.' end
    return true
end
