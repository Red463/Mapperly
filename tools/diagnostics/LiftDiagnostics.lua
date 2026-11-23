-- Opt-in diagnostic package only. Observes routing without changing it.
local _,A=...
local D={lines={},limit=600};A.LiftDiagnostics=D
local function value(v)
    if issecretvalue and issecretvalue(v) then return '<secret>' end
    if type(v)=='number' then return v==v and math.abs(v)<math.huge and string.format('%.3f',v) or '<invalid>' end
    if type(v)=='string' then return v:sub(1,180) end
    if type(v)=='boolean' then return tostring(v) end
    return '-'
end
local function read(fn,...)
    if type(fn)~='function' then return '<unavailable>' end
    local ok,a,b,c,d=pcall(fn,...)
    if not ok then return '<unavailable>' end
    return table.concat({value(a),value(b),value(c),value(d)},',')
end
local function point(p)
    return p and table.concat({value(p.mapID),value(p.x),value(p.y)},',') or '-'
end
function D.Sample()
    if not D.enabled then return end
    local J=A.Journey;local leg=J and J.Leg();local row=leg and leg.transport
    local servicePhase='current'
    if not row and J and J.active and J.active.legs then
        local nextLeg=J.active.legs[(J.legIndex or 0)+1]
        if nextLeg and nextLeg.transport and nextLeg.transport.kind=='lift' then row=nextLeg.transport;servicePhase='upcoming' end
    end
    local p=J and J.PlayerPosition();local state=J and J.transportState or {}
    local world=p and read(A.TravelNetwork.World,p) or '-'
    local function distance(q) return p and q and value(A.TravelNetwork.Distance(p,q)) or '-' end
    local line='t='..read(GetTime)..' map,x,y='..point(p)..' mappedWorld(e,n,instance)='..world..
        ' UnitPosition(n,e,z,instance)='..read(UnitPosition,'player')
    if A.hbd then line=line..' HBD='..read(A.hbd.GetPlayerWorldPosition,A.hbd) end
    line=line..' leg='..value(J and J.legIndex)..' legKind='..value(leg and leg.kind)..' kind='..value(row and row.kind)..' service='..value(row and row.id)..' servicePhase='..servicePhase
    local target=J and J.Current()
    line=line..' currentAim='..(target and read(A.TravelNetwork.World,target) or '-')..' aimDistance='..distance(target)
    if row then
        line=line..' source='..point(row.a)..' destination='..point(row.b)..
            ' sourceZ='..value(row.boardingGroundHeight)..' destinationZ='..value(row.arrivalGroundHeight)..
            ' distanceBoard='..distance(row.board)..' distanceDestination='..distance(row.b)..' distanceLanding='..distance(row.arrival)
        local grid=row.arrivalExitMask
        if grid and p then
            local x,y,instance=A.TravelNetwork.World(p)
            if x and y then
                local column=math.floor((grid.originEast-x)/grid.cellSize)
                local index=math.floor((grid.originNorth-y)/grid.cellSize)
                local bits=index>=0 and index<grid.height and grid.rows[index+1]
                local bit=column>=0 and column<grid.width and type(bits)=='string' and bits:sub(column+1,column+1) or 'outside'
                local q=A.TravelNetwork.Transform(p,grid.mapID)
                line=line..' exitCell='..column..','..index..','..bit..' exitInstance='..value(instance)..
                    ' exitRegion='..value(q and A.WalkingRegions.Get(q))..' expectedRegion='..value(grid.region)..
                    ' dry='..value(q and A.Terrain.Segment(q,q))
            end
        end
    end
    line=line..' boardingSeen='..value(state and state.boardingSeen)..' departed='..value(state and state.departed)..
        ' needsConfirmation='..value(state and state.needsConfirmation)..' instruction='..value(J and J.transportMessage)
    D.lines[#D.lines+1]=line
    if #D.lines>D.limit then table.remove(D.lines,1) end
end
function D.Start()
    D.lines={};D.enabled=true;D.Sample()
end
function D.Report()
    return 'Mapperly lift diagnostics\nBuild: '..value(A.version)..'\n'..
        'Client: '..read(GetBuildInfo)..'\nLifts enabled: '..value(A.db and A.db.useLifts)..
        '\nLast '..#D.lines..' samples (0.5-second intervals; maximum 600).\n'..table.concat(D.lines,'\n')
end
function D.Show()
    local saved=#D.lines==0 and not D.enabled and MapperlyLiftDiagnosticsDB and MapperlyLiftDiagnosticsDB.report
    D.Sample();D.enabled=false
    local text=type(saved)=='string' and saved or D.Report();MapperlyLiftDiagnosticsDB={report=text}
    if not D.window then
        local U=A.Dialogs
        D.window=U.Window('MapperlyLiftDiagnosticsWindow','Lift diagnostics','Copy this report after waiting, riding and walking off the lift.',740,580)
        local scroll=CreateFrame('ScrollFrame',nil,D.window,'UIPanelScrollFrameTemplate')
        scroll:SetPoint('TOPLEFT',D.window,'TOPLEFT',24,-100);scroll:SetPoint('BOTTOMRIGHT',D.window,'BOTTOMRIGHT',-46,64)
        local edit=CreateFrame('EditBox',nil,scroll);D.edit=edit
        edit:SetMultiLine(true);edit:SetAutoFocus(false);edit:SetFontObject('ChatFontNormal');edit:SetMaxLetters(0);edit:SetSize(660,400)
        scroll:SetScrollChild(edit);edit:SetScript('OnEscapePressed',function() D.window:Hide() end)
        U.Action(D.window,'Select all',24,526,120,function() edit:SetFocus();edit:HighlightText() end)
        U.Action(D.window,'Close',596,526,120,function() D.window:Hide() end)
    end
    D.edit:SetText(text);A.Dialogs.Show(D.window);D.edit:SetFocus();D.edit:HighlightText()
end
local base=SlashCmdList.MAPPERLY
SlashCmdList.MAPPERLY=function(msg,...)
    local arg=msg:match('^%s*liftdiag%s*(.-)%s*$')
    if arg==nil then return base(msg,...) end
    if arg=='start' then D.Start();A.Print('Lift capture started. Wait, ride, walk off, then /mapperly liftdiag report.')
    elseif arg=='' or arg=='report' then D.Show()
    elseif arg=='stop' then D.Sample();D.enabled=false
    else A.Print('/mapperly liftdiag start | report | stop') end
end
local observer=CreateFrame('Frame');D.observer=observer
observer:SetSize(1,1);observer:SetPoint('TOPLEFT',UIParent,'TOPLEFT',0,0);observer:EnableMouse(false);observer:Show()
local elapsed=0
observer:SetScript('OnUpdate',function(_,dt)
    if not D.enabled then return end
    elapsed=elapsed+dt;if elapsed<.5 then return end;elapsed=0
    local ok=pcall(D.Sample)
    if not ok then D.lines[#D.lines+1]='<sample unavailable>';if #D.lines>D.limit then table.remove(D.lines,1) end end
end)
observer:RegisterEvent('PLAYER_LOGOUT')
observer:SetScript('OnEvent',function() if #D.lines>0 then MapperlyLiftDiagnosticsDB={report=D.Report()} end end)
