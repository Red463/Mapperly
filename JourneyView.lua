local _,A=...
local V={lines={}};A.JourneyView=V
local function finite(v) return not (issecretvalue and issecretvalue(v)) and type(v)=='number' and v==v and math.abs(v)<math.huge end
function V.Project(p,map)
    if p.mapID==map then return p.x,p.y end
    local hbd=LibStub and LibStub('HereBeDragons-2.0',true)
    if not hbd then return end
    local ok,wx,wy,instance=pcall(hbd.GetWorldCoordinatesFromZone,hbd,p.x,p.y,p.mapID)
    if not ok or not finite(wx) or not finite(wy) or not finite(instance) then return end
    local good,x,y=pcall(hbd.GetZoneCoordinatesFromWorldInstance,hbd,wx,wy,instance,map)
    if good and finite(x) and finite(y) then return x,y end
end
local function layerLevel(canvas)
    local level=canvas:GetFrameLevel()+10
    if A.map.GetPinFrameLevelsManager then
        local ok,manager=pcall(A.map.GetPinFrameLevelsManager,A.map)
        if ok and (type(manager)=='table' or type(manager)=='userdata') and type(manager.GetFrameLevelStart)=='function' then
            -- Exploration/highlight art is drawn by pins above the tile canvas.
            -- Use the top of those art tiers, as Gatherly's route layer does.
            for _,kind in ipairs({'PIN_FRAME_LEVEL_DEFAULT','PIN_FRAME_LEVEL_MAP_EXPLORATION','PIN_FRAME_LEVEL_MAP_HIGHLIGHT'}) do
                local good,base=pcall(manager.GetFrameLevelStart,manager,kind)
                if good and finite(base) then
                    local range=1
                    if type(manager.GetFrameLevelRange)=='function' then
                        local valid,n=pcall(manager.GetFrameLevelRange,manager,kind)
                        if valid and finite(n) and n>=1 then range=n end
                    end
                    level=math.max(level,base+range)
                end
            end
        end
    end
    local api=OpenMapAPI
    if type(api)=='table' and api.major==1 and type(api.IsStitched)=='function' and type(api.ArtTopLevel)=='function' then
        local ok,stitched=pcall(api.IsStitched)
        if ok and stitched then
            local good,top=pcall(api.ArtTopLevel)
            if good and finite(top) then level=math.max(level,top+1) end
        end
    end
    return level
end
function V.Refresh()
    for _,line in pairs(V.lines) do line:Hide() end
    if V.window and V.window:IsShown() and V.followActive then
        local active=A.Journey and A.Journey.active
        if not active then V.window:Hide()
        elseif active~=V.plan then
            V.plan=active;V.candidate=A.Navigation.target;V.WriteSummary()
        end
    end
    local plan=V.window and V.window:IsShown() and V.plan or A.Journey and A.Journey.active
    if not plan or not A.map or not A.db.showJourneyRoute then return end
    if #plan.points>2049 then return end -- Never replace omitted bends with unsafe shortcuts.
    local canvas=A.map:GetCanvas()
    if not V.overlay then
        V.overlay=CreateFrame('Frame',nil,canvas);V.overlay:SetAllPoints(canvas)
        V.overlay:EnableMouse(false);V.overlay:SetClipsChildren(true)
    end
    V.overlay:SetFrameLevel(layerLevel(canvas))
    local map=A.map:GetMapID();local width,height=canvas:GetWidth(),canvas:GetHeight()
    for i=1,#plan.points-1 do
        local ax,ay=V.Project(plan.points[i],map);local bx,by=V.Project(plan.points[i+1],map)
        if ax and bx then
            local line=V.lines[i]
            if not line then line=V.overlay:CreateLine(nil,'OVERLAY');line:SetThickness(2);line:SetColorTexture(1,.77,.18,.9);V.lines[i]=line end
            line:SetStartPoint('TOPLEFT',V.overlay,ax*width,-ay*height)
            line:SetEndPoint('TOPLEFT',V.overlay,bx*width,-by*height);line:Show()
        end
    end
end
function V.Show(plan,candidate)
    V.plan=plan;V.candidate=candidate;V.followActive=A.Journey and A.Journey.active==plan
    local U=A.Dialogs
    if not V.window then
        local f=U.Window('MapperlyJourneyPreview','Journey preview','Review the route before starting, or manage your active journey.',640,524);V.window=f
        local summary=U.Card(f,24,104,592,124)
        V.summary=U.Label(summary,'',16,14,'GameFontNormal');V.summary:SetSize(558,94);V.summary:SetWordWrap(true)
        local steps=U.Card(f,24,242,592,124)
        V.steps=U.Label(steps,'',16,14);V.steps:SetSize(558,98);V.steps:SetWordWrap(true)
        local warning=U.Label(f,'Terrain estimate: check obstacles in game. Swimming is currently allowed. Start replans from your current position.',28,380,'GameFontDisableSmall')
        warning:SetSize(580,42);warning:SetWordWrap(true)
        V.start=U.Action(f,'Start',24,440,100,function()
            local p=V.candidate
            local ok,reason=A.Navigation.Start(p.map or p.mapID,p.x*100,p.y*100,p.name,{mode='terrain'})
            if ok then f:Hide() else V.steps:SetText(reason or 'Unable to start route.') end
        end);A.Theme.ButtonRole(V.start,'primary')
        V.pause=U.Action(f,'Pause',134,440,100,function() A.Navigation.Pause() end)
        V.resume=U.Action(f,'Resume',244,440,100,function() A.Navigation.Resume() end)
        V.skip=U.Action(f,'Skip bend',354,440,110,function() A.Navigation.Skip() end)
        U.Action(f,'Replan',474,440,110,function() A.Navigation.Replan() end)
        U.Action(f,'Stop',24,484,112,function() A.Navigation.Stop();f:Hide() end)
        U.Action(f,'Close',504,484,112,function() f:Hide() end)
        f:HookScript('OnHide',V.Refresh)
    end
    V.WriteSummary()
    U.Show(V.window);V.Refresh()
end
function V.WriteSummary()
    local plan=V.plan
    V.summary:SetText(string.format('%s\nWalking distance: %d yd || About %d min on foot\nTerrain coverage: %s',plan.name or 'Destination',math.floor(plan.distance+.5),math.max(1,math.ceil(plan.estimatedSeconds/60)),plan.coverage or 'unknown'))
    local text={}
    for i,leg in ipairs(plan.legs or {}) do text[#text+1]=i..'. '..leg.name end
    V.steps:SetText(table.concat(text,'\n'))
    local active=A.Journey and A.Journey.active==plan
    V.pause:SetEnabled(active);V.resume:SetEnabled(active);V.skip:SetEnabled(active)
end
function V.OpenCurrent()
    if A.Journey and A.Journey.active and A.Navigation.target then V.Show(A.Journey.active,A.Navigation.target)
    else A.Print('Start or preview a walking journey first.') end
end
function V.Preview(candidate)
    if A.PlanningJob.IsRunning() then return nil,'A route is already being planned. Wait or stop it first.' end
    return A.Journey.Request(candidate,function(plan)
        V.Show(plan,candidate)
        if A.navigationWindow then A.navigationWindow.status:SetText('Walking preview ready.') end
    end,function(reason)
        A.Print(reason)
        if A.navigationWindow then A.navigationWindow.status:SetText(reason or 'No walking route found.') end
    end)
end
