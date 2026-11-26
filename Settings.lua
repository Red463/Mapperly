local _,A=...
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

function A.ShowSettings(drawerKey)
    if not A.settingsWindow then A.CreateSettings() end
    A.SyncSettings()
    A.Dialogs.Show(A.settingsWindow,drawerKey)
end

function A.SyncSettings()
    if not A.settingsControls then return end
    A.settingsSyncing=true
    for key,c in pairs(A.settingsControls) do
        if key=='questPane' then c:SetChecked(A.drawerKey=='settings' and A.db.questPane or A.QuestPaneSelected())
        elseif c.kind=='check' then c:SetChecked(A.db[key])
        elseif c.kind=='filter' then c:SetChecked(A.db.filters[key])
        elseif c.kind=='continent' then c:SetChecked(A.db.continentFilters[c.category])
        else c:SetValue(A.db[key]*c.factor);c.valueText:SetText(c.format(A.db[key]*c.factor)) end
    end
    for name,b in pairs(A.themeChoices or {}) do b.active=A.db.theme==name;b:UpdateVisual() end
    A.settingsSyncing=nil;A.UpdateMarkerPreview()
    if A.NavigationSettings then A.NavigationSettings.Sync() end
end

local function check(parent,key,text,x,y,layout,kind)
    local c=CreateFrame('CheckButton',nil,parent,'UICheckButtonTemplate')
    local size=kind and 23 or 24
    c:SetSize(size,size);c:SetPoint('TOPLEFT',parent,'TOPLEFT',x,-y)
    if text then
        local label=A.Dialogs.Label(parent,text,x+26,y+5)
        c:SetHitRectInsets(0,-2-label:GetStringWidth(),0,0)
    end
    c.kind=kind or 'check';c.category=key
    A.settingsControls[kind=='continent' and 'continent_'..key or key]=c
    c:SetScript('OnClick',function(self)
        local on=not not self:GetChecked()
        if key=='questPane' then
            if A.drawerKey=='settings' then A.db.questPane=on else A.SelectQuestPane(on) end
            return
        end
        if kind=='continent' then A.db.continentFilters[key]=on
        elseif kind=='filter' then A.db.filters[key]=on else A.db[key]=on end
        changed(layout)
    end)
end

local function slider(parent,key,text,x,y,width,lo,hi,step,factor,layout,format)
    local U=A.Dialogs
    U.Label(parent,text,x,y,'GameFontNormalSmall')
    local s=CreateFrame('Slider',nil,parent,'BackdropTemplate')
    s.kind='slider';s.factor=factor;s.format=format
    s:SetOrientation('HORIZONTAL');s:SetSize(width,16);s:SetPoint('TOPLEFT',parent,'TOPLEFT',x,-y-21)
    s:SetBackdrop({bgFile='Interface\\Buttons\\UI-SliderBar-Background',edgeFile='Interface\\Buttons\\UI-SliderBar-Border',tile=true,tileSize=8,edgeSize=8,insets={left=3,right=3,top=3,bottom=3}})
    s:SetThumbTexture('Interface\\Buttons\\UI-SliderBar-Button-Horizontal')
    local thumb=s:GetThumbTexture();if thumb then thumb:SetSize(24,24) end
    s:SetMinMaxValues(lo,hi);s:SetValueStep(step);s:SetObeyStepOnDrag(true)
    s:EnableMouse(true);s:SetHitRectInsets(0,0,-4,-4)
    s.valueText=U.Label(parent,'',x+width-38,y,'GameFontHighlightSmall')
    s.valueText:SetWidth(38);s.valueText:SetJustifyH('RIGHT')
    A.settingsControls[key]=s
    s:SetScript('OnValueChanged',function(_,v)
        if A.settingsSyncing then return end
        v=math.max(lo,math.min(hi,math.floor((v-lo)/step+.5)*step+lo))
        A.db[key]=v/factor;s.valueText:SetText(format(v))
        if key=='iconSize' then A.UpdateMarkerPreview() end
        changed(layout)
    end)
end

local function buildDisplay(display)
    local U=A.Dialogs
    local general=CreateFrame('Frame',nil,display);general:SetAllPoints(display)
    local sizes=CreateFrame('Frame',nil,display);sizes:SetAllPoints(display)
    local tabs={}
    local function selectSize(selected)
        general:SetShown(not selected);sizes:SetShown(selected)
        tabs.general.active=not selected;tabs.general:UpdateVisual()
        tabs.sizes.active=selected;tabs.sizes:UpdateVisual()
    end
    tabs.general=U.Action(display,'General',10,84,151,function() selectSize(false) end,'choice')
    tabs.sizes=U.Action(display,'Size & opacity',165,84,151,function() selectSize(true) end,'choice')
    selectSize(false)

    local theme=U.Card(general,10,117,306,60)
    U.Label(theme,'Appearance theme',8,5,'GameFontNormal')
    A.themeChoices={}
    A.themeChoices.gatherly=U.Action(theme,'Default',6,25,138,function() A.Theme.Set('gatherly') end,'choice')
    A.themeChoices.original=U.Action(theme,'Minimal Charcoal',148,25,152,function() A.Theme.Set('original') end,'choice')

    local map=U.Card(general,10,183,306,85)
    U.Label(map,'Map display',8,6,'GameFontNormal')
    check(map,'coordinates','Coordinates',5,27)
    check(map,'reveal','Reveal unexplored',149,27)
    check(map,'locked','Lock position',5,54,true)
    check(map,'questPane','Show quest log',149,54,true)
    U.Action(general,'Reset map position',10,286,171,function() A.ResetMapPosition();changed(false) end)

    local card=U.Card(sizes,10,117,306,163)
    local percent=function(v) return string.format('%d%%',v) end
    slider(card,'scale','Compact map',10,10,134,50,110,1,100,true,percent)
    slider(card,'iconSize','Marker size',162,10,134,12,36,1,1,false,function(v) return string.format('%d px',v) end)
    U.Label(card,'Marker preview',10,65,'GameFontDisableSmall')
    for i,category in ipairs({'inn','mail','dungeon','flight'}) do
        local icon=card:CreateTexture(nil,'ARTWORK');icon:SetPoint('CENTER',card,'TOPLEFT',123+(i-1)*48,-70)
        A.markerPreviews[#A.markerPreviews+1]={icon=icon,category=category}
    end
    U.Label(card,'Compact map opacity',10,95,'GameFontNormal')
    slider(card,'alpha','Stationary',10,116,134,20,100,5,100,false,percent)
    slider(card,'movingAlpha','Moving',162,116,134,20,100,5,100,false,percent)
end

local function buildLayers(page)
    local U=A.Dialogs
    local names={mail='Mailboxes',inn='Inns',dungeon='Dungeon entrances',flight='Flight masters',transport='Boats and zeppelins',portal='Portals',border='Zone exits',notes='Custom notes'}
    local card=U.Card(page,10,83,306,200)
    U.Label(card,'Location',6,3,'GameFontNormalSmall')
    U.Label(card,'Show',192,3,'GameFontNormalSmall')
    U.Label(card,'Continents',240,3,'GameFontNormalSmall')
    for i,key in ipairs(A.categories) do
        local row=CreateFrame('Frame',nil,card)
        row:SetPoint('TOPLEFT',card,'TOPLEFT',2,-(16+(i-1)*23));row:SetSize(302,23)
        local bg=row:CreateTexture(nil,'BACKGROUND');bg:SetAllPoints(row);bg:SetColorTexture(1,1,1,i%2==1 and .035 or 0)
        local icon=row:CreateTexture(nil,'ARTWORK');icon:SetSize(24,24);icon:SetPoint('LEFT',row,'LEFT',3,0)
        A.SetPinTexture(icon,key,nil,24);A.settingsLayerIcons[key]=icon
        U.Label(row,names[key],32,5)
        check(row,key,nil,193,0,false,'filter')
        check(row,key,nil,254,0,false,'continent')
    end
    local function setAll(on)
        for _,key in ipairs(A.categories) do A.db.filters[key]=on end
        A.SyncSettings();changed()
    end
    U.Action(page,'Show all',10,286,94,function() setAll(true) end)
    U.Action(page,'Hide all',108,286,94,function() setAll(false) end)
end

function A.CreateSettings()
    local U=A.Dialogs
    local f=U.ToolWindow('MapperlySettingsWindow','Settings','Changes save automatically',333,320)
    A.settingsWindow=f;A.settingsControls={};A.settingsLayerIcons={};A.markerPreviews={}
    local pages={};A.settingsTabs={}
    local function selectPage(selected)
        for key,page in pairs(pages) do page:SetShown(key==selected) end
        U.Tabs(A.settingsTabs,selected)
        A.SyncSettings()
    end
    local names={display='Display',layers='Layers',navigation='Navigation'}
    for i,key in ipairs({'display','layers','navigation'}) do
        local page=CreateFrame('Frame',nil,f);page:SetAllPoints(f)
        pages[key]=page;f[key..'Page']=page
        A.settingsTabs[key]=U.Action(f,names[key],10+(i-1)*103,52,100,function() selectPage(key) end,'tab')
    end
    buildDisplay(pages.display)
    buildLayers(pages.layers)
    if A.NavigationSettings then A.NavigationSettings.Build(pages.navigation) end
    U.Action(f,'Done',215,286,101,function() f:Hide() end)
    selectPage('display')
    f:Hide()
end
