local _,A=...
local UI={};A.NearestServicesUI=UI
function UI.Cancel(f)
    local u=f and f.serviceUI;if not u or not u.busy then return end
    local p=A.PlanningJob.Progress()
    if p and p.id==u.jobID then
        A.PlanningJob.Cancel()
        if A.PlanningStatus then A.PlanningStatus.Clear() end
    end
    u.busy=false;u.find:SetText('Find nearest');f.status:SetText('Service search cancelled. Navigation is unchanged.')
end
local function act(f,result,preview)
    local pin,why=A.NearestServices.Resolve(result.pin)
    if not pin then f.status:SetText(why);return end
    local ok,reason
    if preview then ok,reason=A.JourneyView.Preview(pin)
    else ok,reason=A.Navigation.ToPin(pin) end
    if not ok then f.status:SetText(reason or 'Unable to navigate to this service.')
    elseif not preview then f:Hide() end
end
function UI.Build(f)
    local U=A.Dialogs
    local page=CreateFrame('Frame',nil,f);page:SetAllPoints(f);page:Hide();f.servicePage=page
    local card=U.Card(page,24,132,572,344)
    local u={kind='inn',buttons={}};f.serviceUI=u
    local function selected(kind)
        UI.Cancel(f);u.kind=kind;u.result=nil;u.list:Render({},function()end)
        u.summary:SetText('Choose a service and find the shortest verified walking route.')
        u.notice:SetText('Uses bundled locations and your observations. Hidden map-marker layers are included. Flight paths and boats are excluded.')
        for key,b in pairs(u.buttons) do b.active=key==kind;b:UpdateVisual() end
        if f.status then f.status:SetText('') end
    end
    for i,kind in ipairs({'inn','mail','flight','dungeon'}) do
        u.buttons[kind]=U.Action(card,A.NearestServices.categories[kind],16+(i-1)*136,16,128,function() selected(kind) end,'choice')
    end
    u.find=U.Action(card,'Find nearest',16,62,132,function()
        if u.busy then UI.Cancel(f);return end
        u.result=nil;u.list:Render({},function()end);u.summary:SetText('Finding a reachable '..A.NearestServices.categories[u.kind]:lower()..'...')
        local statusID
        local ok,why=A.NearestServices.Request(u.kind,function(result)
            u.busy=false;u.find:SetText('Find nearest');u.result=result
            u.summary:SetText(result.complete and 'Nearest verified walking route' or 'Best found so far - some candidates remain unverified')
            local exact=result.pin.serviceExact or result.pin
            local info=C_Map and C_Map.GetMapInfo and C_Map.GetMapInfo(exact.map)
            local zone=info and info.name or 'Map '..exact.map
            u.list:Render({result},function(row,r)
                A.SetPinTexture(row.icon,u.kind,nil,24);row.title:SetWidth(264);row.title:SetText(exact.name)
                row.detail:SetText(string.format('%s  |  %.0f yd walking  |  %.1f, %.1f  |  %s',zone,r.plan.distance,exact.x*100,exact.y*100,r.pin.source))
                row.detail:SetSize(466,26);row.detail:SetWordWrap(true)
                if not row.preview then
                    row.preview=U.Action(row,'Preview',316,5,92,function() act(f,row.record,true) end)
                    row.go=U.Action(row,'Go',416,5,76,function() act(f,row.record,false) end)
                    row:EnableMouse(true)
                    row:SetScript('OnEnter',function(self)
                        local p=self.record and self.record.pin;if not p then return end
                        GameTooltip:SetOwner(self,'ANCHOR_RIGHT');GameTooltip:SetText((p.serviceExact or p).name)
                        GameTooltip:AddLine('Verified walking route from the search position. Preview or Go recalculates from your current location.',1,.82,0,true);GameTooltip:Show()
                    end)
                    row:SetScript('OnLeave',function() GameTooltip:Hide() end)
                end
            end)
            local notice=result.complete and 'Shortest calculated route among accessible recorded candidates under your road settings.' or 'A search limit or difficult candidate prevents confirming the nearest. Preview this verified result, move closer, or search again.'
            if result.pin.approachDistance then notice=notice..string.format('\nStops %.0f yd from the service. Final building/platform access is manual.',result.pin.approachDistance) end
            u.notice:SetText(notice)
            f.status:SetText(string.format('%d route%s checked. Distance is from the search position.',result.checked,result.checked==1 and '' or 's'))
            if statusID and A.PlanningStatus then A.PlanningStatus.Ready(statusID,result.pin,result.plan) end
        end,function(reason)
            u.busy=false;u.find:SetText('Find nearest');u.summary:SetText('No verified service route found.')
            u.notice:SetText(reason);f.status:SetText('Current navigation is unchanged.')
            if statusID and A.PlanningStatus then A.PlanningStatus.Failed(statusID,{name='Nearest '..A.NearestServices.categories[u.kind]:lower()},reason) end
        end)
        if not ok then u.summary:SetText(why);f.status:SetText('Current navigation is unchanged.');return end
        u.busy=true;u.find:SetText('Cancel search')
        local progress=A.PlanningJob.Progress();u.jobID=progress and progress.id
        if A.PlanningStatus then statusID=A.PlanningStatus.Begin({name='Nearest '..A.NearestServices.categories[u.kind]:lower()},true) end
        f.status:SetText('Searching services. Current navigation is unchanged.')
    end)
    U.Label(card,'Shortest walking route, following your road settings.',164,70,'GameFontDisableSmall'):SetWidth(388)
    u.summary=U.Label(card,'',16,108,'GameFontNormal');u.summary:SetSize(536,32);u.summary:SetWordWrap(true)
    u.list=U.List(card,10,148,548,100)
    u.notice=U.Label(card,'',16,258,'GameFontDisableSmall');u.notice:SetSize(536,70);u.notice:SetWordWrap(true)
    page:SetScript('OnUpdate',function()
        if not u.busy then return end
        local p=A.PlanningJob.Progress()
        if not p or p.id~=u.jobID then UI.Cancel(f);return end
        f.status:SetText(string.format('Searching: %d walking paths, %d terrain cells checked.',p.paths,p.cells))
    end)
    f:HookScript('OnHide',function() UI.Cancel(f) end)
    selected('inn');return page
end
