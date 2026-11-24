local _,A=...
local S={};A.NavigationSettings=S
function S.Select(page)
    for key,f in pairs(S.pages or {}) do f:SetShown(key==page) end
    for key,b in pairs(S.tabs or {}) do b.active=key==page;b:UpdateVisual() end
    S.page=page
end
function S.Sync()
    if A.smartRoutingCheck then A.smartRoutingCheck:SetChecked(A.db.navigationMode~='direct') end
    if A.preferRoadsCheck then A.preferRoadsCheck:SetChecked(A.db.preferRoads) end
    if A.swimmingCheck then A.swimmingCheck:SetChecked(A.db.avoidSwimming==true) end
    if A.rememberJourneyCheck then A.rememberJourneyCheck:SetChecked(A.db.rememberJourney~=false) end
    if S.coverageLabel then
        local text='Swimming is allowed where the existing terrain mask permits it. Buildings and platforms may require manual access.'
        if A.db.avoidSwimming then
            text='Tries a dry route first. If no dry route is found, retries with swimming permitted. Unknown dry coverage may require that retry.'
        end
        S.coverageLabel:SetText(text)
    end
    if A.roadStrengthSlider then
        local level,name=A.Roads.Strength(A.db.roadPreferenceStrength)
        S.syncing=true;A.roadStrengthSlider:SetValue(level);S.syncing=nil
        A.roadStrengthSlider.valueText:SetText('Strength: '..name)
        local enabled=A.db.preferRoads and A.db.navigationMode~='direct'
        A.roadStrengthSlider:SetEnabled(enabled)
        A.roadStrengthSlider:SetAlpha(enabled and 1 or .45)
        A.roadStrengthSlider.valueText:SetAlpha(enabled and 1 or .45)
    end
    if A.journeyRouteCheck then A.journeyRouteCheck:SetChecked(A.db.showJourneyRoute) end
    if A.minimapRouteCheck then A.minimapRouteCheck:SetChecked(A.db.showMinimapRoute) end
    if A.routeStepsCheck then A.routeStepsCheck:SetChecked(A.db.showRouteSteps) end
    if A.transportLinksCheck then A.transportLinksCheck:SetChecked(A.db.showTransportLinks) end
    if A.boatsCheck then A.boatsCheck:SetChecked(A.db.useBoats) end
    if A.zeppelinsCheck then A.zeppelinsCheck:SetChecked(A.db.useZeppelins) end
    if A.airshipsCheck then A.airshipsCheck:SetChecked(A.db.useAirships) end
    if A.flightsCheck then A.flightsCheck:SetChecked(A.db.useFlights) end
    if A.tramsCheck then A.tramsCheck:SetChecked(A.db.useTrams) end
    if A.liftsCheck then A.liftsCheck:SetChecked(A.db.useLifts) end
    for _,kind in ipairs({'tram','lift'}) do
        local check=kind=='tram' and A.tramsCheck or A.liftsCheck
        if check then check:SetEnabled(A.Transports and A.Transports.HasMethod(kind) or false) end
    end
    if S.flightStatus and A.Flights then local known,routes=A.Flights.Stats();S.flightStatus:SetText(known..' known / '..routes..' recorded flight routes.\nOpen flight masters to record routes and fares. Board transports manually.') end
    if S.methodStatus then
        local trams=A.Transports and A.Transports.HasMethod('tram')
        S.methodStatus:SetText((trams and 'Tram: walk through the city portal, ride, exit the other city portal.' or 'Tram: bundled station data is unavailable.')..'\nLifts use bundled native landing data. Board transports yourself; no trip recording is needed.')
    end
end
function S.Build(parent)
    local U=A.Dialogs
    S.pages={};S.tabs={}
    for i,key in ipairs({'routing','travel','tools'}) do
        local page=CreateFrame('Frame',nil,parent);page:SetAllPoints(parent);S.pages[key]=page
        S.tabs[key]=U.Action(parent,({routing='Routing',travel='Travel methods',tools='Recovery and reports'})[key],24+(i-1)*200,202,192,function() S.Select(key) end,'choice')
    end
    local mode=U.Card(S.pages.routing,24,246,592,166)
    U.Label(mode,'Route planning',16,14,'GameFontNormal')
    local smart=CreateFrame('CheckButton',nil,mode,'UICheckButtonTemplate');A.smartRoutingCheck=smart
    smart:SetSize(26,26);smart:SetPoint('TOPLEFT',mode,'TOPLEFT',14,-42)
    U.Label(mode,'Smart routing',44,48)
    smart:SetScript('OnClick',function(self) A.Navigation.SetSmartRouting(not not self:GetChecked());S.Sync() end)
    local swimming=CreateFrame('CheckButton',nil,mode,'UICheckButtonTemplate');A.swimmingCheck=swimming
    swimming:SetSize(26,26);swimming:SetPoint('TOPLEFT',mode,'TOPLEFT',304,-42)
    U.Label(mode,'Avoid swimming if possible',334,48)
    swimming:SetScript('OnClick',function(self) A.Navigation.SetAvoidSwimming(not not self:GetChecked());S.Sync() end)
    local description=U.Label(mode,'Finds a walking route around restricted terrain. Turn it off for straight-line guidance.',16,74,'GameFontDisableSmall')
    description:SetSize(556,24);description:SetWordWrap(true)
    local roads=CreateFrame('CheckButton',nil,mode,'UICheckButtonTemplate');A.preferRoadsCheck=roads
    roads:SetSize(26,26);roads:SetPoint('TOPLEFT',mode,'TOPLEFT',14,-100)
    U.Label(mode,'Prefer roads where possible',44,106)
    roads:SetScript('OnClick',function(self) A.Navigation.SetPreferRoads(not not self:GetChecked());S.Sync() end)
    local strength=CreateFrame('Slider',nil,mode,'BackdropTemplate');A.roadStrengthSlider=strength
    strength:SetOrientation('HORIZONTAL');strength:SetSize(236,16);strength:SetPoint('TOPLEFT',mode,'TOPLEFT',320,-124)
    strength:SetBackdrop({bgFile='Interface\\Buttons\\UI-SliderBar-Background',edgeFile='Interface\\Buttons\\UI-SliderBar-Border',tile=true,tileSize=8,edgeSize=8,insets={left=3,right=3,top=3,bottom=3}})
    strength:SetThumbTexture('Interface\\Buttons\\UI-SliderBar-Button-Horizontal')
    local thumb=strength:GetThumbTexture();if thumb then thumb:SetSize(24,24) end
    strength:SetMinMaxValues(1,5);strength:SetValueStep(1);strength:SetObeyStepOnDrag(true);strength:EnableMouse(true)
    strength.valueText=U.Label(mode,'Strength: Balanced',320,106,'GameFontNormal')
    strength:SetScript('OnValueChanged',function(_,value)
        if not S.syncing then A.Navigation.SetRoadPreferenceStrength(value) end
    end)
    strength:SetScript('OnEnter',function(self)
        GameTooltip:SetOwner(self,'ANCHOR_RIGHT');GameTooltip:SetText('Road preference strength')
        GameTooltip:AddLine('Light accepts small detours; Strong favors roads even when the walk is longer. Balanced preserves the original preference. This is not a roads-only mode.',1,.82,0,true)
        GameTooltip:Show()
    end)
    strength:SetScript('OnLeave',function() GameTooltip:Hide() end)
    local roadHelp=U.Label(mode,'Stronger settings allow longer road detours. Missing road data uses normal terrain routing.',16,146,'GameFontDisableSmall')
    roadHelp:SetSize(556,12);roadHelp:SetWordWrap(false)
    local travel=U.Card(S.pages.travel,24,246,592,184)
    U.Label(travel,'Travel methods',16,14,'GameFontNormal')
    for i,item in ipairs({{'boat','Boats','boatsCheck'},{'zeppelin','Zeppelins','zeppelinsCheck'},{'airship','Airships','airshipsCheck'},
        {'flight','Flight paths','flightsCheck'},{'tram','Trams','tramsCheck'},{'lift','Lifts','liftsCheck'}}) do
        local check=CreateFrame('CheckButton',nil,travel,'UICheckButtonTemplate');A[item[3]]=check
        local x=14+((i-1)%3)*184;local y=i<=3 and 42 or 76
        check:SetSize(26,26);check:SetPoint('TOPLEFT',travel,'TOPLEFT',x,-y)
        U.Label(travel,item[2],x+30,y+6)
        local kind=item[1];check:SetScript('OnClick',function(self) A.Navigation.SetTransportPreference(kind,not not self:GetChecked());S.Sync() end)
        if kind=='tram' or kind=='lift' then
            if check.SetMotionScriptsWhileDisabled then check:SetMotionScriptsWhileDisabled(true) end
            check:SetScript('OnEnter',function(self)
                GameTooltip:SetOwner(self,'ANCHOR_RIGHT');GameTooltip:SetText(item[2])
                GameTooltip:AddLine(A.Transports.HasMethod(kind) and 'Use bundled native connections. Mapperly selects the route automatically; board and ride the transport yourself.' or 'No supported native connection is bundled for this method yet.',1,.82,0,true)
                GameTooltip:Show()
            end)
            check:SetScript('OnLeave',function() GameTooltip:Hide() end)
        end
    end
    S.flightStatus=U.Label(travel,'',16,110,'GameFontDisableSmall');S.flightStatus:SetSize(556,28);S.flightStatus:SetWordWrap(true)
    local automatic=U.Label(travel,'Known connections are bundled. No trip recording or setup is required.',16,150,'GameFontDisableSmall');automatic:SetSize(556,26);automatic:SetWordWrap(true)
    local manual=U.Label(travel,'Record each direction after riding it. Return trips are not inferred.',226,146,'GameFontDisableSmall');manual:SetSize(338,30);manual:SetWordWrap(true)
    local methods=U.Card(S.pages.travel,24,444,592,94)
    S.methodStatus=U.Label(methods,'',16,16,'GameFontDisableSmall');S.methodStatus:SetSize(556,66);S.methodStatus:SetWordWrap(true)
    local travelHelp=U.Card(S.pages.travel,24,552,592,108)
    local notes=U.Label(travelHelp,'Travel times are estimates. Choose flights and board vehicles yourself. Tram arrival is recognised after travelling through the station and exiting into the destination city. City portal access uses a direction marker when indoor walking paths are unavailable.',16,16,'GameFontDisableSmall');notes:SetSize(556,76);notes:SetWordWrap(true)
    local display=U.Card(S.pages.routing,24,424,592,104)
    U.Label(display,'Route display',16,14,'GameFontNormal')
    local check=CreateFrame('CheckButton',nil,display,'UICheckButtonTemplate');A.journeyRouteCheck=check
    check:SetSize(26,26);check:SetPoint('TOPLEFT',display,'TOPLEFT',14,-42)
    U.Label(display,'Show route on the world map',44,48)
    local steps=CreateFrame('CheckButton',nil,display,'UICheckButtonTemplate');A.routeStepsCheck=steps
    steps:SetSize(26,26);steps:SetPoint('TOPLEFT',display,'TOPLEFT',304,-42)
    U.Label(display,'On-screen route steps',334,48)
    steps:SetScript('OnClick',function(self) A.RouteSteps.SetShown(not not self:GetChecked()) end)
    check:SetScript('OnClick',function(self)
        A.db.showJourneyRoute=not not self:GetChecked()
        if A.JourneyView then A.JourneyView.Refresh() end
    end)
    local mini=CreateFrame('CheckButton',nil,display,'UICheckButtonTemplate');A.minimapRouteCheck=mini
    mini:SetSize(26,26);mini:SetPoint('TOPLEFT',display,'TOPLEFT',14,-72)
    U.Label(display,'Show route on the minimap',44,78)
    local links=CreateFrame('CheckButton',nil,display,'UICheckButtonTemplate');A.transportLinksCheck=links
    links:SetSize(26,26);links:SetPoint('TOPLEFT',display,'TOPLEFT',304,-72)
    U.Label(display,'Show travel connections',334,78)
    links:SetScript('OnEnter',function(self)
        GameTooltip:SetOwner(self,'ANCHOR_RIGHT');GameTooltip:SetText('Travel connections')
        GameTooltip:AddLine('Show a schematic network of available flights, boats and other transports on continent and world maps. Off by default. Curves show connections, not exact travel paths.',1,.82,0,true)
        GameTooltip:AddLine('Your active journey and marker-hover previews are displayed separately.',.8,.8,.8,true)
        GameTooltip:Show()
    end)
    links:SetScript('OnLeave',function() GameTooltip:Hide() end)
    links:SetScript('OnClick',function(self)
        A.db.showTransportLinks=not not self:GetChecked()
        if A.BoatLinks then A.BoatLinks.Update() end
    end)
    mini:SetScript('OnClick',function(self)
        A.db.showMinimapRoute=not not self:GetChecked()
        if A.MinimapRoute then A.MinimapRoute.Update() end
    end)
    local coverage=U.Card(S.pages.routing,24,542,592,78)
    local text=U.Label(coverage,'',16,14,'GameFontDisableSmall');S.coverageLabel=text
    text:SetSize(556,52);text:SetWordWrap(true)
    local recovery=U.Card(S.pages.tools,24,246,592,132)
    U.Label(recovery,'Journey recovery',16,14,'GameFontNormal')
    local remember=CreateFrame('CheckButton',nil,recovery,'UICheckButtonTemplate');A.rememberJourneyCheck=remember
    remember:SetSize(26,26);remember:SetPoint('TOPLEFT',recovery,'TOPLEFT',14,-42);U.Label(recovery,'Remember destination after reload or login',44,48)
    remember:SetScript('OnClick',function(self)
        A.db.rememberJourney=not not self:GetChecked()
        if A.db.rememberJourney then A.JourneySession.Capture() else A.JourneySession.Clear() end
        S.Sync()
    end)
    S.resumeButton=U.Action(recovery,'Resume saved journey',16,84,192,function() local ok,why=A.JourneySession.Open();if not ok and why then A.Print(why) end end)
    S.forgetButton=U.Action(recovery,'Forget saved journey',222,84,192,function() A.JourneySession.Clear();A.Print('Saved journey cleared for this character.') end)
    local report=U.Card(S.pages.tools,24,392,592,132)
    U.Label(report,'Route problem report',16,14,'GameFontNormal')
    local explain=U.Label(report,'Copy the route, settings and recent planning results when reporting a problem. Nothing is sent automatically.',16,44,'GameFontDisableSmall');explain:SetSize(556,30);explain:SetWordWrap(true)
    S.reportButton=U.Action(report,'Copy route report',16,84,192,function() A.RouteReport.Open() end)
    local info=U.Card(S.pages.tools,24,538,592,124)
    local help=U.Label(info,'Resuming calculates a fresh route from your position using current settings. A saved transport or floor crossing requires confirmation that you are safely on land. Your notes and saved destinations are separate from this journey snapshot.',16,16,'GameFontDisableSmall');help:SetSize(556,90);help:SetWordWrap(true)
    S.Select('routing')
    S.Sync()
end
