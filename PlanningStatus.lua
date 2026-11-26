local _,A=...
local S={};A.PlanningStatus=S
local function actionText(f,text) f.action:SetText(text);f.action:UpdateVisual() end
local function safe(text) return tostring(text or ''):gsub('|','||') end
local function setReport(f,report)
    f.failureReport=report
    f.copyReport:SetShown(report~=nil);f.reportHint:SetShown(report~=nil)
    f:SetHeight(report and 216 or 188)
end
local function build()
    if S.frame then return S.frame end
    local U=A.Dialogs
    local f=U.CompactWindow(UIParent,420,188);S.frame=f
    f:SetFrameStrata('FULLSCREEN_DIALOG');f:SetClampedToScreen(true);f:EnableMouse(true)
    f.title=U.Label(f,'Planning route',16,6,'GameFontNormal')
    f.title:SetWidth(388);f.title:SetJustifyH('CENTER')
    f.destination=U.Label(f,'',16,42,'GameFontDisableSmall');f.destination:SetSize(388,16);f.destination:SetWordWrap(false)
    f.phase=U.Label(f,'',16,64);f.phase:SetSize(326,18);f.phase:SetWordWrap(false)
    f.elapsed=U.Label(f,'',350,64,'GameFontDisableSmall');f.elapsed:SetWidth(53);f.elapsed:SetJustifyH('RIGHT')
    f.detail=U.Label(f,'',16,88,'GameFontHighlightSmall');f.detail:SetSize(388,52);f.detail:SetWordWrap(true)
    for _,text in ipairs({f.destination,f.phase,f.detail}) do text:SetJustifyH('LEFT') end
    f.reportHint=U.Label(f,"Help us fix this route. Share the report in Mapperly’s CurseForge comments.",16,140,'GameFontHighlightSmall')
    f.reportHint:SetSize(388,32);f.reportHint:SetJustifyH('LEFT');f.reportHint:SetWordWrap(true)
    f.action=U.Action(f,'Cancel',306,148,96,function()
        if f.state=='running' then
            local p=A.PlanningJob.Progress()
            if p and p.id==f.jobID then
                if A.Navigation.CancelPlanning then A.Navigation.CancelPlanning() else A.PlanningJob.Cancel() end
            end
            f.state='cancelled';f.finishedAge=0;f.title:SetText('Calculation cancelled');f.phase:SetText('Previous navigation is unchanged.');f.detail:SetText('')
            setReport(f,nil)
            actionText(f,'Dismiss')
        else f:Hide() end
    end)
    f.action:ClearAllPoints();f.action:SetPoint('BOTTOMRIGHT',f,'BOTTOMRIGHT',-18,12)
    f.copyReport=U.Action(f,'Copy report',0,0,116,function()
        if f.failureReport then A.RouteReport.Open(f.failureReport) end
    end)
    f.copyReport:ClearAllPoints();f.copyReport:SetPoint('RIGHT',f.action,'LEFT',-8,0)
    setReport(f,nil)
    if A.Theme then A.Theme.ButtonRole(f.action,'primary') end
    f:SetScript('OnUpdate',function(_,elapsed) S.Update(elapsed) end)
    f:Hide();return f
end
local function position(f)
    local anchor=A.map and A.map:IsShown() and A.map
    if f.anchor==(anchor or UIParent) then return end
    f.anchor=anchor or UIParent
    f:ClearAllPoints()
    if anchor then f:SetPoint('BOTTOM',anchor,'BOTTOM',0,28)
    else f:SetPoint('TOP',UIParent,'TOP',0,-110) end
end
function S.Begin(candidate,preview)
    local progress=A.PlanningJob.Progress();if not progress then return end
    local f=build();f.jobID=progress.id;f.age=0;f.finishedAge=0;f.notice=nil;f.state='running';f.preview=preview
    setReport(f,nil)
    f.flightRoutes=nil;f.flightSources=nil;f.flightNote=nil
    f.title:SetText('Planning route');f.destination:SetText(safe(candidate and candidate.name or 'Destination'))
    f.phase:SetText('Preparing route');f.detail:SetText('');f.elapsed:SetText('0s');actionText(f,'Cancel')
    position(f);f:Show();f:Raise();return progress.id
end
function S.Ready(id,candidate,plan)
    local f=S.frame;if not id or not f or f.jobID~=id then return end
    setReport(f,nil)
    f.state='ready';f.finishedAge=0;f.title:SetText('Route ready');f.phase:SetText('Navigation updated')
    local walks,transports=0,0
    for _,leg in ipairs(plan.legs or {}) do if leg.kind=='transport' then transports=transports+1 else walks=walks+1 end end
    f.detail:SetText(string.format('%d yd  |  %d walking leg%s%s',math.floor((plan.distance or 0)+.5),walks,walks==1 and '' or 's',transports>0 and string.format('  |  %d transport',transports) or ''))
    actionText(f,'Dismiss')
    if f.preview then f.phase:SetText('Preview ready');f:Hide() end
end
function S.Failed(id,candidate,reason)
    local f=S.frame
    if id and (not f or f.jobID~=id) then return end
    reason=reason or 'No walking route was found.'
    local report=A.RouteReport.Build(candidate,reason,id)
    local progress=A.PlanningJob.Progress()
    if not id and progress then
        -- An invalid new click must not conceal the calculation still running.
        if f and f:IsShown() and f.state=='running' and f.jobID==progress.id then
            f.notice='New destination rejected: '..safe(reason);f.detail:SetText(f.notice)
            setReport(f,report);return
        end
    end
    f=f or build();f.state='failed';f.jobID=id;f.age=f.age or 0;f.title:SetText('Unable to plan route')
    if not id then f.age=0;f.elapsed:SetText('0s') end
    f.destination:SetText(safe(candidate and candidate.name or 'Destination'))
    local detail=safe(reason)
    if id and f.flightRoutes~=nil then detail=detail..'\n'..safe(f.flightNote or string.format('Recorded flight routes considered: %d.',f.flightRoutes)) end
    f.phase:SetText('Previous navigation is unchanged.');f.detail:SetText(detail)
    setReport(f,report)
    actionText(f,'Dismiss');position(f);f:Show();f:Raise()
end
function S.Clear() if S.frame then S.frame:Hide();setReport(S.frame,nil);S.frame.jobID=nil;S.frame.state=nil end end
function S.Update(elapsed)
    local f=S.frame;if not f or not f:IsShown() then return end
    elapsed=type(elapsed)=='number' and math.max(0,elapsed) or 0
    position(f)
    if f.state~='running' then
        f.finishedAge=(f.finishedAge or 0)+elapsed
        if f.state=='ready' and f.finishedAge>=5 or f.state=='cancelled' and f.finishedAge>=3 then f:Hide() end
        return
    end
    f.age=f.age+elapsed;f.elapsed:SetText(string.format('%ds',math.floor(f.age+.5)))
    local p=A.PlanningJob.Progress()
    if not p or p.id~=f.jobID then
        setReport(f,nil)
        f.state='cancelled';f.finishedAge=0;f.title:SetText('Calculation cancelled');f.phase:SetText('Previous navigation is unchanged.');f.detail:SetText('');actionText(f,'Dismiss');return
    end
    f.title:SetText('Planning route'..string.rep('.',math.floor(f.age*2)%3+1))
    local stage=p.stage
    if stage=='Finding a walking path' and p.mapID and C_Map and C_Map.GetMapInfo then
        local ok,info=pcall(C_Map.GetMapInfo,p.mapID)
        if ok and info and type(info.name)=='string' then stage='Finding a path in '..safe(info.name) end
    elseif p.total then stage=stage..string.format(' (%d/%d)',p.checked or 0,p.total) end
    f.phase:SetText(stage)
    local detail=string.format('Paths checked: %d  |  Terrain locations checked: %d',p.paths,p.cells)
    f.flightRoutes=p.flightRoutes;f.flightSources=p.flightSources;f.flightNote=p.flightNote
    if p.flightRoutes~=nil then detail=detail..'\n'..safe(p.flightNote or string.format('Flight routes considered: %d (from %d departure masters).',p.flightRoutes,p.flightSources or 0)) end
    if f.age>=10 then detail=detail..'\nLong routes can take a while. You can cancel this calculation.' end
    f.detail:SetText(f.notice or detail)
end
