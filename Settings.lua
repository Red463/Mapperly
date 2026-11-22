local _,A=...
local windowWidth,windowHeight=640,746
local function label(parent,text,x,y,font) return A.Dialogs.Label(parent,text,x,y,font) end
local function panel(parent,x,y,width,height) return A.Dialogs.Card(parent,x,y,width,height) end
local function changed(layout)
    if layout and A.map then A.ApplyLayout() end
    A.UpdateOpacity();A.Refresh()
end
function A.UpdateMarkerPreview()
    for _,preview in ipairs(A.markerPreviews or {}) do
        preview.icon:SetSize(A.db.iconSize,A.db.iconSize)
        A.SetPinTexture(preview.icon,preview.category,nil,A.db.iconSize)
    end
end
function A.ShowSettings()
    if not A.settingsWindow then A.CreateSettings() end
    local f=A.settingsWindow
    if CloseDropDownMenus then CloseDropDownMenus() end
    f:SetScale(math.min(1,(UIParent:GetWidth()-40)/windowWidth,(UIParent:GetHeight()-40)/windowHeight))
    A.SyncSettings();f:Show();f:Raise()
end
function A.SyncSettings()
    if not A.settingsControls then return end
    A.settingsSyncing=true
    for key,c in pairs(A.settingsControls) do
        if c.kind=='check' then c:SetChecked(A.db[key])
        elseif c.kind=='filter' then c:SetChecked(A.db.filters[key])
        elseif c.kind=='continent' then c:SetChecked(A.db.continentFilters[c.category])
        else c:SetValue(A.db[key]*c.factor);c.valueText:SetText(c.format(A.db[key]*c.factor)) end
    end
    for name,b in pairs(A.themeChoices or {}) do b.active=A.db.theme==name;b:UpdateVisual() end
    A.settingsSyncing=nil;A.UpdateMarkerPreview()
end
function A.CreateSettings()
    local f=A.Dialogs.Window('MapperlySettingsWindow','Mapperly - Settings','Map settings  |  Changes save automatically',windowWidth,windowHeight)
    A.settingsWindow=f;A.settingsControls={};A.settingsLayerIcons={};A.markerPreviews={}
    local display=CreateFrame('Frame',nil,f);display:SetAllPoints(f)
    local layers=CreateFrame('Frame',nil,f);layers:SetAllPoints(f);layers:Hide()
    f.displayPage=display;f.layersPage=layers
    local function action(parent,text,x,y,width,fn)
        local b=A.CreateMapButton(parent,text,width-16,0,fn)
        b:ClearAllPoints();b:SetPoint('TOPLEFT',parent,'TOPLEFT',x,-y);b:SetSize(width,28);b:UpdateVisual();return b
    end
    A.settingsTabs={}
    local function selectPage(page)
        if page=='display' then display:Show();layers:Hide() else display:Hide();layers:Show() end
        for key,tab in pairs(A.settingsTabs) do tab.active=key==page;A.Theme.ButtonRole(tab,'tab') end
        A.SyncSettings()
    end
    A.settingsTabs.display=action(f,'Map appearance',24,88,170,function() selectPage('display') end)
    A.settingsTabs.layers=action(f,'Location layers',202,88,170,function() selectPage('layers') end)
    A.settingsTabs.display.active=true;A.Theme.ButtonRole(A.settingsTabs.display,'tab');A.Theme.ButtonRole(A.settingsTabs.layers,'tab')
    local themes=panel(f,24,132,592,58)
    label(themes,'Appearance theme',16,21,'GameFontNormal')
    A.themeChoices={}
    A.themeChoices.gatherly=action(themes,'Default',220,15,166,function() A.Theme.Set('gatherly') end)
    A.themeChoices.original=action(themes,'Minimal Charcoal',394,15,166,function() A.Theme.Set('original') end)
    A.AttachButtonTooltip(A.themeChoices.gatherly,'Default Mapperly theme. Applies immediately.')
    A.AttachButtonTooltip(A.themeChoices.original,'Minimal Charcoal theme. Applies immediately.')
    local function check(parent,key,text,x,y,layout,filter)
        local c=CreateFrame('CheckButton',nil,parent,'UICheckButtonTemplate');c:SetSize(26,26);c:SetPoint('TOPLEFT',parent,'TOPLEFT',x,-y)
        if text then label(parent,text,x+30,y+6) end
        c.kind=filter=='continent' and 'continent' or filter and 'filter' or 'check';c.category=key
        A.settingsControls[filter=='continent' and 'continent_'..key or key]=c
        c:SetScript('OnClick',function(s)
            if filter=='continent' then A.db.continentFilters[key]=not not s:GetChecked()
            elseif filter then A.db.filters[key]=not not s:GetChecked() else A.db[key]=not not s:GetChecked() end
            changed(layout)
        end)
    end
    local displayCard=panel(display,24,202,592,110)
    label(displayCard,'Map display',16,12,'GameFontNormal')
    check(displayCard,'coordinates','Show coordinates',14,38)
    check(displayCard,'reveal','Reveal unexplored areas',306,38)
    check(displayCard,'locked','Lock map position',14,72,true)
    check(displayCard,'questPane','Show quest log',306,72,true)
    local sizeCard=panel(display,24,324,592,206)
    label(sizeCard,'Map and markers',16,12,'GameFontNormal')
    local function slider(parent,key,text,x,y,width,lo,hi,step,factor,layout,format)
        label(parent,text,x,y)
        local s=CreateFrame('Slider',nil,parent,'BackdropTemplate');s.kind='slider';s.factor=factor;s.format=format
        s:SetOrientation('HORIZONTAL');s:SetSize(width,18);s:SetPoint('TOPLEFT',parent,'TOPLEFT',x,-y-25)
        s:SetBackdrop({bgFile='Interface\\Buttons\\UI-SliderBar-Background',edgeFile='Interface\\Buttons\\UI-SliderBar-Border',tile=true,tileSize=8,edgeSize=8,insets={left=3,right=3,top=3,bottom=3}})
        s:SetThumbTexture('Interface\\Buttons\\UI-SliderBar-Button-Horizontal')
        local thumb=s:GetThumbTexture();if thumb then thumb:SetSize(28,28) end
        s:SetMinMaxValues(lo,hi);s:SetValueStep(step);s:SetObeyStepOnDrag(true)
        s:EnableMouse(true);s:SetHitRectInsets(0,0,-6,-6)
        s.valueText=label(parent,'',x+width-56,y,'GameFontNormal')
        label(parent,format(lo),x,y+48,'GameFontDisableSmall')
        local maximum=label(parent,format(hi),x+width-56,y+48,'GameFontDisableSmall');maximum:SetWidth(56);maximum:SetJustifyH('RIGHT')
        A.settingsControls[key]=s
        s:SetScript('OnValueChanged',function(_,v)
            if A.settingsSyncing then return end
            v=math.max(lo,math.min(hi,math.floor((v-lo)/step+.5)*step+lo))
            A.db[key]=v/factor;s.valueText:SetText(format(v))
            if key=='iconSize' then A.UpdateMarkerPreview() end
            changed(layout)
        end)
    end
    local percent=function(v) return string.format('%d%%',v) end
    slider(sizeCard,'scale','Compact map size',20,42,548,50,110,1,100,true,percent)
    label(sizeCard,'Minimum size keeps the controls readable.',20,104,'GameFontDisableSmall')
    slider(sizeCard,'iconSize','Map marker size',20,120,280,12,36,1,1,false,function(v) return string.format('%d px',v) end)
    local previewCard=panel(sizeCard,326,108,246,82)
    label(previewCard,'Live marker preview',12,10,'GameFontNormalSmall')
    for i,category in ipairs({'inn','mail','dungeon','flight'}) do
        local icon=previewCard:CreateTexture(nil,'ARTWORK');icon:SetPoint('CENTER',previewCard,'TOPLEFT',32+(i-1)*60,-52)
        A.markerPreviews[#A.markerPreviews+1]={icon=icon,category=category}
    end
    local opacityCard=panel(display,24,544,592,142)
    label(opacityCard,'Compact map opacity',16,12,'GameFontNormal')
    slider(opacityCard,'alpha','While stationary',20,42,250,20,100,5,100,false,percent)
    slider(opacityCard,'movingAlpha','While moving',320,42,250,20,100,5,100,false,percent)
    label(opacityCard,'The enlarged map stays fully opaque.',20,116,'GameFontDisableSmall')
    local layerCard=panel(layers,24,202,592,454)
    label(layerCard,'Location',16,14,'GameFontNormal')
    label(layerCard,'Show',392,14,'GameFontNormal')
    local continentTitle=label(layerCard,'On continents',482,14,'GameFontNormal')
    continentTitle:SetWidth(110);continentTitle:SetJustifyH('CENTER')
    local names={mail='Mailboxes',inn='Inns',dungeon='Dungeon entrances',flight='Flight masters',transport='Boats and zeppelins',portal='Portals',border='Zone exits',notes='Custom notes'}
    for i,key in ipairs(A.categories) do
        local y=38+(i-1)*46
        local row=CreateFrame('Frame',nil,layerCard);row:SetPoint('TOPLEFT',layerCard,'TOPLEFT',8,-y);row:SetSize(576,42)
        local bg=row:CreateTexture(nil,'BACKGROUND');bg:SetAllPoints(row);bg:SetColorTexture(1,1,1,i%2==1 and .025 or 0)
        local icon=row:CreateTexture(nil,'ARTWORK');icon:SetPoint('LEFT',row,'LEFT',12,0);icon:SetSize(24,24)
        A.SetPinTexture(icon,key,nil,24);A.settingsLayerIcons[key]=icon
        label(row,names[key],50,14)
        check(row,key,nil,386,8,false,true)
        check(row,key,nil,516,8,false,'continent')
    end
    label(layerCard,'Show enables the layer. On continents also shows it on overview maps.',16,416,'GameFontDisableSmall')
    local coverage=label(layers,'Bundled locations plus your discoveries.',28,668,'GameFontDisableSmall')
    coverage:SetWidth(330);coverage:SetWordWrap(false)
    action(layers,'Show all',376,662,112,function() for _,k in ipairs(A.categories) do A.db.filters[k]=true end;A.SyncSettings();changed() end)
    action(layers,'Hide all',496,662,112,function() for _,k in ipairs(A.categories) do A.db.filters[k]=false end;A.SyncSettings();changed() end)
    A.Theme.ButtonRole(action(f,'Reset map position',24,704,162,function() A.ResetMapPosition();changed(false) end),'primary')
    A.Theme.ButtonRole(action(f,'Done',496,704,120,function() f:Hide() end),'primary')
    f:Hide()
end
