local _,A=...
local S={};A.NavigationSettings=S

function S.Select(page)
    for key,f in pairs(S.pages or {}) do f:SetShown(key==page) end
    for key,b in pairs(S.tabs or {}) do b.active=key==page or (key=='display' and page=='style');b:UpdateVisual() end
    S.page=page
    if page=='style' then S.RefreshStyle() end
end

function S.Sync()
    if A.smartRoutingCheck then A.smartRoutingCheck:SetChecked(A.db.navigationMode~='direct') end
    if A.preferRoadsCheck then A.preferRoadsCheck:SetChecked(A.db.preferRoads) end
    if A.swimmingCheck then A.swimmingCheck:SetChecked(A.db.avoidSwimming==true) end
    if A.rememberJourneyCheck then A.rememberJourneyCheck:SetChecked(A.db.rememberJourney~=false) end
    if S.coverageLabel then
        local text=A.db.avoidSwimming and 'Tries a dry route first, then allows swimming if needed.' or 'Allows swimming where the terrain data permits it.'
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
    if S.flightStatus and A.Flights then
        local known,routes=A.Flights.Stats()
        S.flightStatus:SetText(known..' flight masters known / '..routes..' routes recorded')
    end
end

local function hint(parent,text,x,y,width,height)
    local label=A.Dialogs.Label(parent,text,x,y,'GameFontDisableSmall')
    label:SetSize(width,height);label:SetWordWrap(true)
    label:SetJustifyH('LEFT');label:SetJustifyV('TOP')
    return label
end

local function check(parent,key,text,x,y,apply)
    local b=CreateFrame('CheckButton',nil,parent,'UICheckButtonTemplate')
    b:SetSize(24,24);b:SetPoint('TOPLEFT',parent,'TOPLEFT',x,-y)
    local label=A.Dialogs.Label(parent,text,x+26,y+5)
    b:SetHitRectInsets(0,-2-label:GetStringWidth(),0,0)
    b:SetScript('OnClick',function(self) apply(not not self:GetChecked()) end)
    A[key]=b
    return b
end

local function tooltip(control,title,description)
    control:SetScript('OnEnter',function(self)
        GameTooltip:SetOwner(self,'ANCHOR_RIGHT');GameTooltip:SetText(title)
        GameTooltip:AddLine(type(description)=='function' and description() or description,1,.82,0,true)
        GameTooltip:Show()
    end)
    control:SetScript('OnLeave',function() GameTooltip:Hide() end)
end

local function buildRouting(card)
    local smart=check(card,'smartRoutingCheck','Smart routing',7,5,function(on) A.Navigation.SetSmartRouting(on);S.Sync() end)
    tooltip(smart,'Smart routing','Finds a walking route around restricted terrain. Turn it off for straight-line guidance.')
    check(card,'swimmingCheck','Avoid swimming',149,5,function(on) A.Navigation.SetAvoidSwimming(on);S.Sync() end)
    S.coverageLabel=hint(card,'',10,34,286,30)

    check(card,'preferRoadsCheck','Prefer roads',7,70,function(on) A.Navigation.SetPreferRoads(on);S.Sync() end)
    local strength=CreateFrame('Slider',nil,card,'BackdropTemplate');A.roadStrengthSlider=strength
    strength:SetOrientation('HORIZONTAL');strength:SetSize(277,16);strength:SetPoint('TOPLEFT',card,'TOPLEFT',14,-101)
    strength:SetBackdrop({bgFile='Interface\\Buttons\\UI-SliderBar-Background',edgeFile='Interface\\Buttons\\UI-SliderBar-Border',tile=true,tileSize=8,edgeSize=8,insets={left=3,right=3,top=3,bottom=3}})
    strength:SetThumbTexture('Interface\\Buttons\\UI-SliderBar-Button-Horizontal')
    local thumb=strength:GetThumbTexture();if thumb then thumb:SetSize(24,24) end
    strength:SetMinMaxValues(1,5);strength:SetValueStep(1);strength:SetObeyStepOnDrag(true);strength:EnableMouse(true)
    strength.valueText=A.Dialogs.Label(card,'',147,75,'GameFontNormalSmall')
    strength:SetScript('OnValueChanged',function(_,value)
        if not S.syncing then A.Navigation.SetRoadPreferenceStrength(value) end
    end)
    tooltip(strength,'Road preference strength','Light accepts short detours. Strong favors roads on longer detours. Areas without road data use normal terrain routing.')
    hint(card,'Stronger preferences allow longer detours along roads.',10,130,286,29)
end

local function buildDisplay(card)
    A.Dialogs.Label(card,'Route display',10,8,'GameFontNormal')
    A.Dialogs.Action(card,'Route style',185,2,114,function() S.Select('style') end)
    check(card,'journeyRouteCheck','Show route on the world map',7,29,function(on)
        A.db.showJourneyRoute=on
        if A.JourneyView then A.JourneyView.Refresh() end
    end)
    check(card,'minimapRouteCheck','Show route on the minimap',7,59,function(on)
        A.db.showMinimapRoute=on
        if A.MinimapRoute then A.MinimapRoute.Update() end
    end)
    check(card,'routeStepsCheck','Show on-screen route steps',7,89,function(on) A.RouteSteps.SetShown(on) end)
    local links=check(card,'transportLinksCheck','Show travel connections',7,119,function(on)
        A.db.showTransportLinks=on
        if A.BoatLinks then A.BoatLinks.Update() end
    end)
    tooltip(links,'Travel connections','Shows available flights, boats and other transport links on continent and world maps. The curves connect stops schematically. Your journey and marker previews are shown separately.')
end

local markerNames={chevron='Chevron',triangle='Triangle',none='None'}
local nextMarker={chevron='triangle',triangle='none',none='chevron'}

local function redrawStyle()
    S.RefreshStyle()
    if A.JourneyView then A.JourneyView.Refresh(true) end
    if A.MinimapRoute then A.MinimapRoute.Update() end
end

local function colorField(parent,label,key,x)
    local U=A.Dialogs
    U.Label(parent,label,x,43,'GameFontNormalSmall')
    local input=U.Input(parent,x+34,59,95,24,7)
    local swatch=CreateFrame('Button',nil,parent)
    swatch:SetSize(24,22);swatch:SetPoint('TOPLEFT',parent,'TOPLEFT',x,-60)
    local ink=swatch:CreateTexture(nil,'BACKGROUND');ink:SetAllPoints();ink:SetColorTexture(.13,.1,.07,1)
    local fill=swatch:CreateTexture(nil,'ARTWORK')
    fill:SetPoint('TOPLEFT',2,-2);fill:SetPoint('BOTTOMRIGHT',-2,2)
    local function sync()
        local c=A.RouteStyle.Color(key)
        fill:SetColorTexture(c[1],c[2],c[3],1)
        input:SetText(('#%02X%02X%02X'):format(math.floor(c[1]*255+.5),math.floor(c[2]*255+.5),math.floor(c[3]*255+.5)))
    end
    input:SetScript('OnEnterPressed',function(self)
        local hex=self:GetText():match('^#?(%x%x%x%x%x%x)$')
        if not hex then self:HighlightText();return end
        A.db[key]={tonumber(hex:sub(1,2),16)/255,tonumber(hex:sub(3,4),16)/255,tonumber(hex:sub(5,6),16)/255}
        self:ClearFocus();redrawStyle()
    end)
    input:SetScript('OnEscapePressed',function(self) self:ClearFocus();sync() end)
    tooltip(input,label,'Enter a six-digit hex colour and press Enter to apply.')
    tooltip(swatch,label,'Click to choose a colour.')
    swatch:SetScript('OnClick',function()
        local picker=ColorPickerFrame
        if not picker or not picker.SetupColorPickerAndShow then input:SetFocus();input:HighlightText();return end
        local original=A.db[key]
        local c=A.RouteStyle.Color(key)
        picker:SetupColorPickerAndShow({r=c[1],g=c[2],b=c[3],hasOpacity=false,
            swatchFunc=function() A.db[key]={picker:GetColorRGB()};redrawStyle() end,
            cancelFunc=function() A.db[key]=original;redrawStyle() end})
    end)
    return sync
end

local function buildStyle(card)
    local U=A.Dialogs
    local sample=U.Card(card,8,4,290,34)
    local segments={
        {8,-23,60,-23,kind='completed'}, {60,-23,84,-12,kind='completed'},
        {84,-12,140,-12,kind='ahead'}, {140,-12,165,-22,kind='ahead'},
        {165,-22,278,-22,kind='ahead'},
    }
    for _,segment in ipairs(segments) do segment.base=sample:CreateLine(nil,'OVERLAY') end
    local markers,fragments={},{}
    local ahead=colorField(card,'Route ahead','routeAheadColor',12)
    local completed=colorField(card,'Completed trail','routeCompletedColor',161)
    local width=U.Action(card,'Width',7,88,140,function()
        A.db.routeLineWidth=A.RouteStyle.Width()%6+1;redrawStyle()
    end)
    local marker=U.Action(card,'Markers',151,88,148,function()
        A.db.routeMarkerShape=nextMarker[A.RouteStyle.Shape()];redrawStyle()
    end)
    U.Action(card,'Back',7,129,94,function() S.Select('display') end)
    U.Action(card,'Reset style',165,129,134,function()
        A.db.routeAheadColor=nil;A.db.routeCompletedColor=nil
        A.db.routeLineWidth=nil;A.db.routeMarkerShape=nil;redrawStyle()
    end)
    function S.RefreshStyle()
        local style=A.RouteStyle
        ahead();completed()
        width:SetText('Width: '..style.Width()..' px')
        marker:SetText('Markers: '..markerNames[style.Shape()])
        style.Hide(markers);style.HideLines(fragments)
        style.Render(segments,markers,fragments,sample,{worldUnit=1,spacing=66,limit=3,size=5.5,
            thickness=1.7,strokeWidth=3,anchor='TOPLEFT'})
    end
end

local function buildTravel(card)
    for i,item in ipairs({{'boat','Boats','boatsCheck'},{'zeppelin','Zeppelins','zeppelinsCheck'},
        {'airship','Airships','airshipsCheck'},{'flight','Flight paths','flightsCheck'},
        {'tram','Trams','tramsCheck'},{'lift','Lifts','liftsCheck'}}) do
        local kind=item[1]
        local b=check(card,item[3],item[2],7+((i-1)%2)*145,5+math.floor((i-1)/2)*27,function(on)
            A.Navigation.SetTransportPreference(kind,on);S.Sync()
        end)
        if kind=='tram' or kind=='lift' then
            if b.SetMotionScriptsWhileDisabled then b:SetMotionScriptsWhileDisabled(true) end
            tooltip(b,item[2],function()
                if not A.Transports.HasMethod(kind) then return 'No supported connection is bundled for this method yet.' end
                if kind=='tram' then return 'Enter through the city portal, board the tram and leave through the destination city portal.' end
                return 'Mapperly uses bundled landing data. Board the lift and leave at your stop.'
            end)
        end
    end
    S.flightStatus=hint(card,'',10,93,286,16)
    hint(card,'Visit flight masters to record routes and fares. Select flights and board other transports yourself.',10,116,286,42)
end

local function buildTools(card)
    local U=A.Dialogs
    U.Label(card,'Journey recovery',10,8,'GameFontNormal')
    check(card,'rememberJourneyCheck','Remember journey after reload or login',7,29,function(on)
        A.db.rememberJourney=on
        if on then A.JourneySession.Capture() else A.JourneySession.Clear() end
        S.Sync()
    end)
    S.resumeButton=U.Action(card,'Resume journey',7,56,143,function()
        local ok,why=A.JourneySession.Open();if not ok and why then A.Print(why) end
    end)
    S.forgetButton=U.Action(card,'Forget journey',155,56,143,function()
        A.JourneySession.Clear();A.Print('Saved journey cleared for this character.')
    end)
    A.AttachButtonTooltip(S.resumeButton,'Recalculate the saved route from your current position.')
    A.AttachButtonTooltip(S.forgetButton,'Clear the saved journey for this character.')
    U.Label(card,'Route problem report',10,98,'GameFontNormal')
    S.reportButton=U.Action(card,'Copy route report',7,122,162,function() A.RouteReport.Open() end)
    A.AttachButtonTooltip(S.reportButton,'Copy the route, settings and recent planning results to share when reporting a problem.')
end

function S.Build(parent)
    local U=A.Dialogs
    S.pages={};S.tabs={}
    local names={routing='Routing',display='Display',travel='Travel',tools='Tools'}
    local builders={routing=buildRouting,display=buildDisplay,travel=buildTravel,tools=buildTools}
    for i,key in ipairs({'routing','display','travel','tools'}) do
        local page=U.Card(parent,10,117,306,164);S.pages[key]=page
        S.tabs[key]=U.Action(parent,names[key],10+(i-1)*77,84,74,function() S.Select(key) end,'secondary')
        builders[key](page)
    end
    S.pages.style=U.Card(parent,10,117,306,164)
    buildStyle(S.pages.style)
    S.Select('routing')
    S.Sync()
end
