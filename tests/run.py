"""Run from a Mapperly checkout after installing requirements-dev.txt."""
from pathlib import Path
import sys
root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root/'.test-deps'))
from lupa.lua51 import LuaRuntime
lua = LuaRuntime(unpack_returned_tuples=True)
for path in root.rglob('*.lua'):
    lua.execute('assert(loadstring(...))', path.read_text(encoding='utf-8-sig'))
lua.execute('A = {}; assert(loadstring(...))("Mapperly", A)', (root/'Store.lua').read_text())
lua.execute('''
local db=A.InitStore({scale=99, movingAlpha=-1, filters={mail=false}, notes=false})
assert(A.InitStore({}).iconSize==18)
assert(A.InitStore({iconSize=24}).iconSize==24,'saved marker sizes must remain intact')
A.InitStore(db)
assert(db.scale==1 and db.layoutVersion==2 and db.movingAlpha==.2 and db.filters.mail==false)
assert(A.InitStore({layoutVersion=2,scale=99}).scale==1.1)
A.InitStore(db)
assert(db.filters.inn and type(db.notes)=='table')
assert(db.continentFilters and db.continentFilters.dungeon==true and db.continentFilters.inn==false,'overview defaults must show only dungeons')
local custom=A.InitStore({continentFilters={inn=true,dungeon=false,mail='bad'}})
assert(custom.continentFilters.inn and not custom.continentFilters.dungeon and custom.continentFilters.mail==false)
A.InitStore(db)
assert(not A.AddNote(1,1.1,.4,'Bad'))
assert(not A.AddNote(1,0/0,.4,'Bad'))
assert(not A.AddNote(1,.1,.4,' '))
assert(A.AddNote(1,.1,.4,'Meeting point'))
assert(#db.notes==1 and db.notes[1].name=='Meeting point')
assert(A.InitStore(db).notes[1].x==.1)
assert(A.InitStore({position={x=math.huge,y=0}}).position==nil)
assert(A.InitStore({position={x=0/0,y=0}}).position==nil)
assert(A.InitStore({position={}}).position==nil)
A.InitStore(db)
assert(not A.ValidPin({map=1,x=-1,y=0,name='bad'}))
''')
lua.execute((root/'tests/wow.lua').read_text())
lua.execute('''
fakeUI()
local createFrame=CreateFrame
CreateFrame=function(kind,...)
 local object=createFrame(kind,...)
 if kind=='Texture' then object.SetTexture=function(self,path) self.texture=path;return true end end
 if kind=='FontString' then object.GetStringWidth=function(self) return #self:GetText()*7.5 end end
 return object
end
InCombatLockdown=function() return false end
GetUnitSpeed=function() return 0 end
GetCursorPosition=function() return 50,50 end
IsAltKeyDown=function() return false end
UnitFactionGroup=function() return 'Alliance' end
C_Map={GetPlayerMapPosition=function() return nil end}
WorldMapFrame.GetMapID=function() return 1416 end
WorldMapFrame.EnumerateDataProviders=function() return function() end end
WorldMapFrame.canvas:SetSize(1000,600)
WorldMapFrame:SetSize(900,650)
WorldMapFrame.GetScale=function(self) return self.scale or 1 end
WorldMapFrame.BorderFrame=CreateFrame('Frame')
WorldMapFrame.BorderFrame.MaximizeMinimizeFrame=CreateFrame('Frame')
WorldMapFrame.NavBar=CreateFrame('Frame')
WorldMapFrame.BlackoutFrame=CreateFrame('Frame')
WorldMapFrame.QuestLog=CreateFrame('Frame')
WorldMapFrame.questLogWidth=333
WorldMapFrame.QuestLog:SetWidth(333)
WorldMapFrame.QuestLog.QuestsFrame=CreateFrame('Frame',nil,WorldMapFrame.QuestLog)
local questScroll=CreateFrame('ScrollFrame',nil,WorldMapFrame.QuestLog.QuestsFrame)
WorldMapFrame.QuestLog.QuestsFrame.ScrollFrame=questScroll
questScroll.GetHeight=function() return WorldMapFrame:GetHeight()-A.headerHeight-A.footerHeight-29 end
questScroll.Background=questScroll:CreateTexture(nil,'BACKGROUND')
questScroll.Background.GetAtlas=function(self) return self.atlas end
questScroll.Background.SetAtlas=function(self,name,useSize)
 self.atlas=name;self:SetTexCoord(.125,.625,.25,.75)
 if useSize then self:SetSize(304,430) end
end
questScroll.Background:SetAtlas('QuestLog-main-background',true)
questScroll.ResizeBackground=function(self)
 local height=self.Background:GetHeight()
 self.Background:SetHeight(math.min(height,self:GetHeight()))
 self.Background:SetTexCoord(0,1,0,math.min(1,self:GetHeight()/height))
end
WorldMapFrame.SetQuestLogPanelShown=function(self,shown) if shown then self.QuestLog:Show() else self.QuestLog:Hide() end end
WorldMapFrame.ScrollContainer.GetWidth=function() return WorldMapFrame:GetWidth()-(A.questPaneExtent or 0)-(A.railWidth or 0) end
WorldMapFrame.ScrollContainer.GetHeight=function() return WorldMapFrame:GetHeight()-(A.headerHeight+A.footerHeight) end
WorldMapFrame.OnFrameSizeChanged=function(self)
 self.fittedWidth=self.ScrollContainer:GetWidth();self.fittedHeight=self.ScrollContainer:GetHeight()
end
WorldMapFrame.ResetZoom=function(self,ignoreScaleRatio) self.centered=ignoreScaleRatio end
local minimized=0
WorldMapFrame.Minimize=function() minimized=minimized+1 end
WorldMapFrame.Maximize=function(self) self:SetSize(1920,1080) end
WorldMapFrame.Minimize=function(self) self:SetSize(900,650);self:OnFrameSizeChanged() end
UIDropDownMenu_Initialize=function() end
UIDropDownMenu_CreateInfo=function() return {} end
UIDropDownMenu_AddButton=function() end
hooksecurefunc=function(object,key,callback)
 local original=object[key]
 object[key]=function(...) original(...);callback(...) end
end
StaticPopupDialogs={};SlashCmdList={}
DEFAULT_CHAT_FRAME={AddMessage=function() end}
LibStub=function() return nil end
WorldMapFrame.nativePins={}
WorldMapFrame.RemoveAllPinsByTemplate=function(self,template)
 assert(template=='MapperlyMapPinTemplate','must never remove third-party pins')
 for _,pin in ipairs(self.nativePins) do pin:Hide() end;self.nativePins={}
end
WorldMapFrame.AcquirePin=function(self,template,data)
 assert(template=='MapperlyMapPinTemplate')
 local pin=CreateFrame('Button',nil,self.canvas)
 pin.ShouldMouseButtonBePassthrough=function(_,button) return button=='RightButton' end
 for key,fn in pairs(MapperlyMapPinMixin) do pin[key]=fn end
 pin.icon=pin:CreateTexture(nil,'ARTWORK')
 pin.icon.SetTexture=function(s,path) s.texture=path;return true end
 pin.icon.SetSnapToPixelGrid=function(s,v) s.snapped=v end
 pin.icon.SetTexelSnappingBias=function(s,v) s.snappingBias=v end
 pin.UseFrameLevelType=function(s,kind) s.frameLevelType=kind;s:SetFrameLevel(kind=='PIN_FRAME_LEVEL_GOSSIP' and 521 or 500) end
 pin.SetScalingLimits=function(s,...) s.scalingLimits={...} end
 pin.SetPosition=function(s,x,y) s.normalizedPosition={x,y} end
 pin:OnLoad();pin:OnAcquired(data);pin:Show();table.insert(self.nativePins,pin);return pin
end
''')
for name in ['Data/Places.lua','Data/FlightData.lua','Data/ZoneLevels.lua','ZoneLevels.lua','Places.lua','Data/Services.lua','Services.lua','Navigation.lua','Pins.lua','Reveal.lua','Shell.lua','Opacity.lua','Settings.lua','Buttons.lua','NavigationUI.lua','Map.lua','Core.lua']:
    lua.execute('assert(loadstring(...))("Mapperly", A)', (root/name).read_text(encoding='utf-8-sig'))
lua.execute('''
A.AttachMap()
assert(A.map==WorldMapFrame and A.bar)
assert(A.navigation.rightBorder and not A.navigation.rightBorder:IsShown(),'icon buttons must not retain visible border edges')
local questScroll=A.map.QuestLog.QuestsFrame.ScrollFrame
local function fittedQuestBackground()
 assert(questScroll.Background.all==questScroll,'quest-list background must fill the resized list without a fixed-height join')
 assert(questScroll.Background.coords[1]==.125 and questScroll.Background.coords[4]==.75,'native atlas coordinates must be restored after background resize')
end
fittedQuestBackground()
questScroll:ResizeBackground();fittedQuestBackground()
questScroll.Background:SetAtlas('QuestLog-empty-quest-background',true)
questScroll:ResizeBackground();fittedQuestBackground()
assert(questScroll.Background:GetAtlas()=='QuestLog-empty-quest-background','empty-log artwork must be preserved')
local function fitted()
 assert(A.map.fittedWidth==A.map.ScrollContainer:GetWidth(),'zoom bounds must use final viewport width')
 assert(A.map.fittedHeight==A.map.ScrollContainer:GetHeight(),'zoom bounds must use final viewport height')
 assert(A.map.centered==true,'size changes must fit and center without old pan ratio')
end
fitted()
for _,compactMode in ipairs({false,true,false,true}) do
 A.db.compact=compactMode;A.ApplyLayout()
 local expected=compactMode and 'Resize' or 'Compact'
 assert(A.sizeButton.icon.texture:match(expected..'$'),'size icon must describe the next action in both modes')
end
for i=1,6 do A.sizeButton:GetScript('OnClick')();fitted() end
local timers={}
C_Timer={After=function(_,fn) timers[#timers+1]=fn end}
A.sizeButton:GetScript('OnClick')()
A.sizeButton:GetScript('OnClick')()
assert(#timers==1,'rapid size changes should coalesce into one settled fit')
-- Simulate a native callback writing stale geometry after our layout changes.
A.map.fittedWidth=700;A.map.fittedHeight=466
timers[1]();fitted()
assert(not A.viewportFitQueued)
C_Timer=nil
local calls={}
LibStub=function() return {GetZoneCoordinatesFromWorldInstance=function(_,x,y,instance,map)
 calls[#calls+1]={x,y,instance,map};return .25,.5
end} end
A.PlacesForMap(1431)
assert(calls[1][1]==1571.6 and calls[1][2]==-231,'game north/east coordinates must be swapped for HBD horizontal/vertical projection')
LibStub=function() return nil end
local records={}
UIDropDownMenu_AddButton=function(info) records[#records+1]=info end
A.BuildMenu(nil,1)
assert(#records==10,'filters should contain only eight pin categories and show/hide all')
for _,info in ipairs(records) do assert(not info.text:find('opacity') and not info.text:find('Quest pane')) end
assert(A.controls.quests and A.controls.notes and A.controls.reveal and A.controls.settings)
-- Forever popups expose GetEditBox(), not the legacy lowercase editBox field.
local popup,edit
StaticPopup_Show=function(which,_,__,data)
 assert(which=='MAPPERLY_NOTE')
 edit={text='stale',SetText=function(self,v) self.text=v end,GetText=function(self) return self.text end,
       SetFocus=function(self) self.focused=true end}
 popup={data=data,GetEditBox=function() return edit end,Hide=function(self) self.hidden=true end}
 edit.GetParent=function() return popup end
 return popup
end
local savedPosition=C_Map.GetPlayerMapPosition
C_Map.GetPlayerMapPosition=function(id) if id==1416 then return {GetXY=function() return .3,.6 end} end end
C_Map.GetBestMapForUnit=function() return 1416 end
local notesBefore=#A.db.notes
A.controls.notes:GetScript('OnClick')()
assert(popup and edit.focused and edit.text=='','Add note must focus the Forever popup edit box')
edit:SetText('Meeting spot')
A.db.filters.notes=false
StaticPopupDialogs.MAPPERLY_NOTE.OnAccept(popup,popup.data)
assert(#A.db.notes==notesBefore+1 and A.db.notes[#A.db.notes].name=='Meeting spot')
assert(A.db.filters.notes,'new notes must not be hidden by their category filter')
local visibleNote=false
for _,pin in ipairs(A.pinPool) do if pin.data.name=='Meeting spot' and pin:IsShown() then visibleNote=true end end
assert(visibleNote,'accepted note must reach the visible native map pins')
local savedGetMapID,savedSetMapID=A.map.GetMapID,A.map.SetMapID
local noteMap=1431
A.map.GetMapID=function() return noteMap end
A.map.SetMapID=function(_,id) noteMap=id end
popup=nil
A.controls.notes:GetScript('OnClick')()
assert(popup and popup.data.map==1416 and noteMap==1416,'Add note from another map must navigate to the player zone')
edit:SetText('')
assert(StaticPopupDialogs.MAPPERLY_NOTE.OnAccept(popup,popup.data)==true,'blank note must keep the naming dialog open')
edit:SetText('Second spot')
StaticPopupDialogs.MAPPERLY_NOTE.EditBoxOnEnterPressed(edit,popup.data)
assert(popup.hidden and #A.db.notes==notesBefore+2,'Enter must save the note and close the dialog')
A.ShowNote(1416,.2,.4)
edit:SetText('Cancelled')
StaticPopupDialogs.MAPPERLY_NOTE.EditBoxOnEscapePressed(edit)
assert(popup.hidden and #A.db.notes==notesBefore+2,'Escape must close without saving')
A.map.GetMapID=savedGetMapID;A.map.SetMapID=savedSetMapID
C_Map.GetPlayerMapPosition=savedPosition
A.controls.settings:GetScript('OnClick')()
assert(A.settingsWindow and A.settingsWindow:IsShown(),'settings action must open a dedicated window')
assert(A.controls.quests:GetParent()==A.actionRail,'quest toggle must join the right-side icon rail')
assert(A.bar:GetHeight()==42 and A.controls.filters:GetHeight()==28,'approved raised buttons need breathing room')
assert(A.controls.quests:GetWidth()==28 and A.controls.quests:GetHeight()==28)
local skinButton=A.controls.filters
assert(not skinButton.face.gradient and not skinButton.topBevel,'buttons must have a solid flat face without bevels')
for _,key in ipairs({'locate','navigate','notes','filters','reveal','lock','settings','quests','parent','size','close'}) do
 local b=A.controls[key]
 assert(b:GetParent()==A.actionRail and b.iconOnly and b:GetWidth()==28 and b:GetHeight()==28,'every action must be a compact icon on the right rail: '..key)
 assert(b.icon and b.icon:GetWidth()==24 and b:GetText()=='','toolbar artwork must be larger with less padding')
 assert(not b.outer:IsShown() and not b.rim:IsShown(),'icon buttons must not draw nested background borders')
 for _,edge in ipairs(b.borders) do assert(not edge:IsShown(),'all icon borders must be removed') end
 b:GetScript('OnEnter')(b);assert(GameTooltip:GetText()~='','each icon must retain a descriptive tooltip')
 b:GetScript('OnLeave')(b)
end
assert(skinButton.face.color[1]<.16,'flat charcoal button fill must be darker')
local savedCursor=A.map.GetNormalizedCursorPosition
local savedPlayerPosition=C_Map.GetPlayerMapPosition
A.map.GetNormalizedCursorPosition=function() return .384,.563 end
C_Map.GetPlayerMapPosition=function() return {GetXY=function() return .799,.568 end} end
A.UpdateCoordinates()
assert(A.playerCoordinates:GetText()=='Player: 79.9, 56.8')
assert(A.cursorCoordinates:GetText()=='Cursor: 38.4, 56.3')
assert(A.playerCoordinates.point[1]=='LEFT' and A.cursorCoordinates.point[1]=='RIGHT','coordinate fields must occupy separate anchored columns')
assert(A.footer:GetFrameStrata()=='HIGH' and A.footer:GetFrameLevel()>2000,'opaque footer must cover older coordinate labels beneath it')
A.map.GetNormalizedCursorPosition=function() return 2,-1 end
A.UpdateCoordinates();assert(A.cursorCoordinates:GetText()=='Cursor: --, --','outside-map cursor must have a clean placeholder')
A.db.coordinates=false;A.UpdateCoordinates()
assert(A.playerCoordinates:GetText()=='' and A.cursorCoordinates:GetText()=='')
A.db.coordinates=true
A.map.GetNormalizedCursorPosition=savedCursor;C_Map.GetPlayerMapPosition=savedPlayerPosition
local railHeight=4
for _,key in ipairs({'close','size','parent','locate','navigate','notes','filters','quests','reveal','lock','settings'}) do
 local b=A.controls[key]
 railHeight=railHeight+b:GetHeight()+(key=='close' and 0 or (key=='parent' or key=='filters' or key=='lock') and 10 or 4)
end
assert(railHeight<400,'compact icon rail must remain short enough for the supported compact map')
local dropdownAnchor
ToggleDropDownMenu=function(_,__,menu,anchor) dropdownAnchor=anchor end
A.controls.filters:GetScript('OnClick')(A.controls.filters)
assert(dropdownAnchor==A.controls.filters,'filters popup must anchor to its new icon button')
A.controls.navigate:GetScript('OnClick')()
assert(A.navigationWindow and A.navigationWindow:IsShown() and A.navigationWindow.targetMap==A.map:GetMapID(),'navigation rail action must open coordinate entry for the viewed map')
A.navigationWindow:Hide()
local savedFilters={}
for _,key in ipairs(A.categories) do savedFilters[key]=A.db.filters[key];A.db.filters[key]=false end
local savedNoteCount=#A.db.notes
A.Navigation.target={map=A.map:GetMapID(),x=.4,y=.6,name='Navigation destination',category='navigation'}
A.RefreshPins()
assert(#A.pinPool==1 and A.pinPool[1].data.category=='navigation','destination pin must remain visible with all location filters disabled')
assert(A.pinPool[1].icon.texture:find('Markers',1,true) and A.pinPool[1].icon.texture:match('Destination$'),'destination must use the painted marker asset')
assert(A.pinPool[1].frameLevelType=='PIN_FRAME_LEVEL_WAYPOINT_LOCATION','destination must use the native waypoint layer')
assert(not A.pinPool[1]:ShouldMouseButtonBePassthrough('RightButton'))
A.pinPool[1]:OnClick('RightButton')
assert(not A.Navigation.target and #A.pinPool==0 and #A.db.notes==savedNoteCount,'stopping a destination must leave permanent notes intact')
for key,value in pairs(savedFilters) do A.db.filters[key]=value end
A.RefreshPins()
skinButton:GetScript('OnMouseDown')(skinButton)
assert(skinButton.pressed and skinButton:GetFontString().point[5]==0,'flat button caption must remain stationary')
skinButton:GetScript('OnLeave')(skinButton)
assert(not skinButton.pressed and skinButton:GetFontString().point[5]==0)
local locked=A.db.locked
A.controls.lock:GetScript('OnClick')()
assert(A.controls.lock.active==A.db.locked and A.controls.lock.activeLine:IsShown()==A.db.locked)
A.controls.lock:GetScript('OnClick')();assert(A.db.locked==locked)
assert(A.actionRail.point[1]=='BOTTOMRIGHT','rail must stay on the right edge')
local pingCount=0
local playerPin={StopPlayerPing=function() end,UpdatePlayerPins=function() end,StartPlayerPing=function(_,duration,interval)
 assert(duration==2 and interval==.25);pingCount=pingCount+1
end}
local oldSetMapID,oldGetMapID=A.map.SetMapID,A.map.GetMapID
local selectedMap=1416
A.map.SetMapID=function(_,id) selectedMap=id end
A.map.GetMapID=function() return selectedMap end
A.map.EnumeratePinsByTemplate=function(_,template)
 assert(template=='GroupMembersPinTemplate');local done=false
 return function() if not done then done=true;return playerPin end end
end
C_Map.GetBestMapForUnit=function() return 1416 end
for click=1,3 do A.controls.locate:GetScript('OnClick')();assert(pingCount==click,'each same-zone click must restart player ping') end
selectedMap=1431;A.controls.locate:GetScript('OnClick')()
assert(selectedMap==1416 and pingCount==4,'cross-zone locate must still navigate and ping')
A.map.SetMapID=oldSetMapID;A.map.GetMapID=oldGetMapID
assert(A.controls.quests.point[1]=='TOP')
assert(A.controls.quests.icon.texture=='Interface\\\\AddOns\\\\Mapperly\\\\Media\\\\Toolbar\\\\Small\\\\Quest')
local originalPane=A.db.questPane
A.controls.quests:GetScript('OnClick')();assert(A.db.questPane~=originalPane)
A.controls.quests:GetScript('OnClick')();assert(A.db.questPane==originalPane)
assert(A.settingsControls.questPane:GetChecked()==originalPane)
local originalInfo=C_Map.GetMapInfo
C_Map.GetMapInfo=function(id) return {mapID=id,name='Test map',mapType=id==9000 and 2 or id==9001 and 1 or 3} end
local originalPins=A.PinsForMap
A.PinsForMap=function(map)
 local result={}
 for _,category in ipairs(A.categories) do result[#result+1]={map=map,x=.3,y=.4,category=category,name=category} end
 return result
end
local visibilityMap=A.map.GetMapID
A.map.GetMapID=function() return 9000 end
for _,key in ipairs(A.categories) do A.db.filters[key]=true;A.db.continentFilters[key]=key=='dungeon' end
A.RefreshPins()
assert(#A.pinPool==1 and A.pinPool[1].data.category=='dungeon','continent maps must initially show dungeons only')
local continentInn=A.settingsControls.continent_inn
assert(continentInn,'settings must expose per-category continent visibility')
continentInn:SetChecked(true);continentInn:GetScript('OnClick')(continentInn)
assert(A.db.continentFilters.inn and #A.pinPool==2,'continent checkbox must immediately reveal the enabled category')
A.SyncSettings();assert(continentInn:GetChecked(),'settings must retain the continent preference')
for _,pin in ipairs(A.pinPool) do assert(pin.frameLevelType=='PIN_FRAME_LEVEL_AREA_POI','overview pins retain the normal POI tier') end
A.db.filters.inn=false;A.RefreshPins();assert(#A.pinPool==1,'main layer filter must still hide continent icons')
A.db.filters.inn=true
A.map.GetMapID=function() return 9001 end
A.RefreshPins();assert(#A.pinPool==2,'world maps must use the same overview settings')
A.map.GetMapID=function() return 1416 end
A.RefreshPins();assert(#A.pinPool==#A.categories,'all enabled categories must remain visible on zone maps')
for _,pin in ipairs(A.pinPool) do
 assert(pin.frameLevelType=='PIN_FRAME_LEVEL_GOSSIP' and pin:GetFrameLevel()>500,'zone icons must use the native tier above resource nodes')
end
local reused=A.pinPool[1]
reused:OnAcquired({map=9000,x=.3,y=.4,category='dungeon',name='Reused'})
assert(reused.frameLevelType=='PIN_FRAME_LEVEL_AREA_POI','reused pins must reset the layer when moving to an overview')
A.map.GetMapID=visibilityMap;A.PinsForMap=originalPins;C_Map.GetMapInfo=originalInfo
local beforeAlpha=A.db.alpha
A.ShowSettings();assert(A.db.alpha==beforeAlpha,'opening settings must not mutate saved values')
for _,category in ipairs(A.categories) do
 assert(A.settingsLayerIcons and A.settingsLayerIcons[category],'every location row needs its marker artwork')
 assert(A.settingsLayerIcons[category]:GetWidth()==24)
end
assert(A.markerPreviews and #A.markerPreviews==4,'size setting must have a representative live marker preview')
A.settingsControls.alpha:SetValue(65);assert(A.db.alpha==.65,'opacity slider must set explicit percentage')
A.settingsControls.iconSize:SetValue(28);assert(A.db.iconSize==28)
for _,preview in ipairs(A.markerPreviews) do
 assert(preview.icon:GetWidth()==28 and preview.icon:GetHeight()==28,'preview must follow selected marker dimensions')
 assert(preview.icon.texture:find('Medium',1,true),'preview must use the same size tier as map pins')
end
A.settingsControls.iconSize:SetValue(12)
for _,preview in ipairs(A.markerPreviews) do assert(preview.icon:GetWidth()==12 and preview.icon.texture:find('Small',1,true)) end
A.settingsControls.iconSize:SetValue(36)
for _,preview in ipairs(A.markerPreviews) do assert(preview.icon:GetWidth()==36) end
A.settingsControls.iconSize:SetValue(28)
A.settingsControls.coordinates:SetChecked(false)
A.settingsControls.coordinates:GetScript('OnClick')(A.settingsControls.coordinates)
assert(not A.db.coordinates)
local settings=A.settingsWindow
settings:Hide();A.ShowSettings();assert(A.settingsWindow==settings and settings:IsShown())
assert(A.settingsControls.alpha.value==65,'reopening settings must restore saved slider value')
assert(A.markerPreviews[1].icon:GetWidth()==28,'reopening settings must restore the saved marker preview')
A.settingsTabs.layers:GetScript('OnClick')()
assert(A.settingsWindow.layersPage:IsShown() and not A.settingsWindow.displayPage:IsShown() and A.settingsTabs.layers.active,'location tab must show and highlight its page')
A.settingsTabs.display:GetScript('OnClick')()
assert(A.settingsWindow.displayPage:IsShown() and not A.settingsWindow.layersPage:IsShown() and A.settingsTabs.display.active)
UIParent:SetSize(800,600);A.ShowSettings()
assert(A.settingsWindow:GetHeight()*A.settingsWindow.scale<=560.01,'settings must fit smaller screens')
assert(A.settingsWindow:GetWidth()*A.settingsWindow.scale<=760.01)
UIParent:SetSize(1920,1080);A.ShowSettings()
QuestieLoader=setmetatable({}, {__index=function() error('no runtime Questie data access is permitted') end})
local oldMapID=A.map.GetMapID
A.map.GetMapID=function() return 1431 end
local mapping={mapData={[1431]={}}}
function mapping:GetZoneCoordinatesFromWorldInstance(east,north,instance,map)
 if instance~=0 or map~=1431 then return end
 local x,y=(833.3333-east)/2700,(-9716.666-north)/1800
 if x>=0 and x<=1 and y>=0 and y<=1 then return x,y end
end
LibStub=function() return mapping end
assert(#A.BundledServices==156)
A.LoadServices()
local inn,mail=0,0
for _,p in ipairs(A.ServicePins[1431]) do
 if p.category=='inn' then inn=inn+1;assert(p.id==6790);assert(math.abs(p.x-.73872)<.0001 and math.abs(p.y-.44407)<.0001) end
 if p.category=='mail' then mail=mail+1 end
end
assert(inn==1 and mail>=1,'Duskwood must have its bundled inn and mailbox without Questie')
A.db.filters.inn=true;A.RefreshPins()
local foundInn=false
for _,pin in ipairs(A.pinPool) do if pin:IsShown() and pin.data.category=='inn' then foundInn=true end end
assert(foundInn,'bundled services must reach native map pins')
local function innCount()
 local n=0;for _,p in ipairs(A.PinsForMap(1431)) do if p.category=='inn' then n=n+1 end end;return n
end
local before=innCount()
table.insert(A.db.observed,{map=1431,x=.73872,y=.44407,name='Observed inn',category='inn'})
assert(innCount()==before,'observed and bundled services near each other must deduplicate')
table.remove(A.db.observed)
UnitFactionGroup=function() return 'Horde' end
assert(innCount()==0,'opposite-faction inn must not leak through cached projections')
UnitFactionGroup=function() return 'Alliance' end
assert(innCount()==1,'faction cache must rebuild when returning to Alliance')
local oldBest,oldPosition=C_Map.GetBestMapForUnit,C_Map.GetPlayerMapPosition
C_Map.GetBestMapForUnit=function() return 1431 end
C_Map.GetPlayerMapPosition=function() return {GetXY=function() return .2,.2 end} end
local observedCount=#A.db.observed
A.Observe('mail','Discovered mailbox')
assert(#A.db.observed==observedCount+1 and A.db.observed[#A.db.observed].access=='A')
A.InitStore(A.db)
local discovered=false
for _,p in ipairs(A.PinsForMap(1431)) do if p.name=='Discovered mailbox' then discovered=true end end
assert(discovered,'new discoveries must supplement bundled data and survive store initialization')
A.Observe('mail','Discovered mailbox')
assert(#A.db.observed==observedCount+1,'revisiting a service must not keep adding records')
table.remove(A.db.observed)
C_Map.GetBestMapForUnit=oldBest;C_Map.GetPlayerMapPosition=oldPosition
A.map.GetMapID=oldMapID;LibStub=function() return nil end
local selected
local texture={SetTexCoord=function() end,SetTexture=function(_,path) selected=path;return true end}
A.SetPinTexture(texture,'dungeon')
assert(selected=='Interface\\\\AddOns\\\\Mapperly\\\\Media\\\\Markers\\\\Dungeon')
A.SetPinTexture(texture,'inn')
assert(selected=='Interface\\\\AddOns\\\\Mapperly\\\\Media\\\\Markers\\\\Hearthstone')
A.SetPinTexture(texture,'flight')
assert(selected=='Interface\\\\AddOns\\\\Mapperly\\\\Media\\\\Markers\\\\FlightMaster')
for _,kind in ipairs({'boat','zeppelin','airship'}) do
 A.SetPinTexture(texture,'transport',kind)
 local expected=kind:sub(1,1):upper()..kind:sub(2)
 assert(selected=='Interface\\\\AddOns\\\\Mapperly\\\\Media\\\\Markers\\\\'..expected)
end
for category,name in pairs({mail='Mail',portal='Portal',notes='Note',border='ZoneExit'}) do
 A.SetPinTexture(texture,category)
 assert(selected=='Interface\\\\AddOns\\\\Mapperly\\\\Media\\\\Markers\\\\'..name)
end
QuestieLoader=nil
local compact=A.map:GetHeight()
assert(compact>=UIParent:GetHeight()*.70,'compact mode should use a substantial screen area')
assert(not A.map.BorderFrame:IsShown() and not A.map.BlackoutFrame:IsShown())
assert(not A.map.QuestLog:IsShown(),'quest pane must be opt-in')
A.db.compact=false;A.ApplyLayout()
assert(A.map:GetHeight()>compact, 'enlarged mode must be larger')
assert(A.map:GetWidth()*A.map:GetScale()<=UIParent:GetWidth()*.92+.01)
assert(A.map:GetHeight()*A.map:GetScale()<=UIParent:GetHeight()*.90+.01)
A.map:Maximize()
assert(not A.db.compact and A.map:GetWidth()<1920,'native maximize must return to Mapperly windowed canvas')
assert(A.map:GetHeight()*A.map:GetScale()<=UIParent:GetHeight()*.90+.01)
A.sizeButton:GetScript('OnClick')()
assert(A.db.compact,'top-right button must toggle Mapperly mode')
A.map:SetQuestLogPanelShown(true)
assert(A.db.questPane and A.map.QuestLog:IsShown())
assert(A.map.QuestLog:GetWidth()>=A.map.questLogWidth,'quest pane must not squeeze fixed native quest controls')
assert(A.questPaneExtent>=A.map.QuestLog:GetWidth()+12,'pane must reserve its width plus gutters')
assert(A.controls.quests:GetWidth()==28,'quest toggle must match compact rail controls')
assert(A.controls.quests.arrow:GetText()=='<','open quest drawer must show a closing arrow')
fitted()
A.map:SetQuestLogPanelShown(false)
assert(not A.db.questPane and not A.map.QuestLog:IsShown())
assert(A.controls.quests.arrow:GetText()=='>','closed quest drawer must show an opening arrow')
fitted()
for _,dims in ipairs({{1280,720},{2560,1080},{1024,768}}) do
 UIParent:SetSize(dims[1],dims[2])
 for _,mode in ipairs({true,false}) do
  for _,shown in ipairs({true,false}) do
   A.db.compact=mode;A.db.questPane=shown;A.ApplyLayout()
   assert(A.map:GetWidth()*A.map:GetScale()<=dims[1]*.92+.01)
   assert(A.map:GetHeight()*A.map:GetScale()<=dims[2]*.90+.01)
   assert(A.map.ScrollContainer:GetWidth()>0)
   fittedQuestBackground()
   assert(A.railWidth==32 and A.map.ScrollContainer:GetWidth()+A.questPaneExtent+A.railWidth==A.map:GetWidth(),'narrow rail and quest panel must sit outside the map artwork')
   assert(A.playerCoordinates:GetWidth()+A.cursorCoordinates:GetWidth()+32==A.footer:GetWidth(),'footer columns must preserve an explicit gap at every map size')
   if shown then
    assert(A.map.QuestLog:GetWidth()>=333,'compact mode must preserve native quest-control width')
    assert(A.controls.quests.arrow:GetText()=='<')
   else assert(A.controls.quests.arrow:GetText()=='>') end
  end
 end
end
UIParent:SetSize(1920,1080)
A.db.compact=true;A.ApplyLayout()
A.Refresh()
assert(#A.PlacesForMap(1416)>0)
assert(#A.pinPool>=1)
for _,pin in ipairs(A.pinPool) do
 assert(pin.frameLevelType=='PIN_FRAME_LEVEL_GOSSIP','zone pins must use the native layer above resource POIs')
 assert(pin.normalizedPosition[1]==pin.data.x and pin.normalizedPosition[2]==pin.data.y)
 assert(pin:GetWidth()==A.db.iconSize,'pin size must be managed by native scaling')
 assert(pin.icon.snapped and pin.icon.snappingBias==0,'marker textures must align to pixels')
 local tier=A.db.iconSize<=24 and 'Small' or 'Medium'
 assert(pin.icon.texture:find(tier,1,true),'native pins must select size-appropriate artwork')
 local level=pin:GetFrameLevel();pin:OnMouseEnter();assert(pin:GetFrameLevel()==level+20)
 pin:OnMouseLeave();assert(pin:GetFrameLevel()==level)
end
A.db.filters.dungeon=false;A.RefreshPins()
for _,p in ipairs(A.pinPool) do if p:IsShown() then assert(p.data.category~='dungeon') end end
local n=#A.db.notes
SlashCmdList.MAPPERLY('note 1416 25 50 Test note')
assert(#A.db.notes==n+1)
local notePin
for _,pin in ipairs(A.pinPool) do if pin.data==A.db.notes[#A.db.notes] then notePin=pin end end
assert(notePin and not notePin:ShouldMouseButtonBePassthrough('RightButton'),'custom notes must consume right-click before native navigation')
local parentNavigations=0
if notePin:ShouldMouseButtonBePassthrough('RightButton') then parentNavigations=parentNavigations+1 else notePin:OnClick('RightButton') end
assert(#A.db.notes==n and parentNavigations==0,'right-click must remove the note without changing zones')
assert(notePin:ShouldMouseButtonBePassthrough('LeftButton')==false)
assert(MapperlyMapPinMixin.ShouldMouseButtonBePassthrough({data={category='inn'}},'RightButton'),'service pins must preserve native right-click navigation')
SlashCmdList.MAPPERLY('note 1416 250 50 Invalid note')
assert(#A.db.notes==n)
SlashCmdList.MAPPERLY('note 1416 . 50 Invalid note')
SlashCmdList.MAPPERLY('pin portal 1416 1..2 50 Invalid pin')
assert(#A.db.notes==n)
local oldCompact,oldAlpha,oldMoving=A.db.compact,A.db.alpha,A.db.movingAlpha
local moving=true
IsPlayerMoving=function() return moving end
-- Native movement fader keeps active and deferred registries and otherwise
-- writes its own alpha every frame, independently of Mapperly's poll.
local active,deferred={},{}
local other={};active[other]=true
PlayerMovementFrameFader={RemoveFrame=function(frame) active[frame]=nil;deferred[frame]=nil end}
local function nativeTick()
 if deferred[A.map] then active[A.map]=true;deferred[A.map]=nil end
 if active[A.map] then A.map:SetAlpha(moving and .5 or 1) end
end
A.db.compact=true;A.db.alpha=.9;A.db.movingAlpha=.45
for cycle=1,3 do
 active[A.map]=true;deferred[A.map]=true
 A.map:GetScript('OnShow')(A.map)
 assert(not active[A.map] and not deferred[A.map],'opening map must remove both native fade registrations')
 assert(active[other],'opacity ownership must affect only this map')
 for frame=1,40 do nativeTick();A.UpdateOpacity();assert(A.map:GetAlpha()==.45,'moving opacity must remain stable') end
end
moving=false;A.UpdateOpacity();assert(A.map:GetAlpha()==.9)
moving=true;A.UpdateOpacity();assert(A.map:GetAlpha()==.45)
A.db.compact=false;A.UpdateOpacity();assert(A.map:GetAlpha()==1)
PlayerMovementFrameFader=nil;IsPlayerMoving=nil
A.db.compact=oldCompact;A.db.alpha=oldAlpha;A.db.movingAlpha=oldMoving;A.UpdateOpacity()
local oldInfo,oldLevels,oldAtPosition=C_Map.GetMapInfo,C_Map.GetMapLevels,C_Map.GetMapInfoAtPosition
local oldMapID,oldCursor=A.map.GetMapID,A.map.GetNormalizedCursorPosition
C_Map.GetMapInfo=function(id) return {mapID=id,name=id==1431 and 'Duskwood' or 'Kalimdor',mapType=id==1415 and 2 or 3} end
C_Map.GetMapLevels=function() return 0,0 end
assert(A.ZoneTitle(1431,'Duskwood')=='Duskwood (18–30)')
assert(A.ZoneTitle(999999,'Unknown zone')=='Unknown zone')
assert(A.ZoneLevelRange(1453)==nil and A.ZoneLevelRange(1415)==nil)
C_Map.GetMapLevels=function() return 22,34 end
assert(A.ZoneTitle(1431,'Duskwood')=='Duskwood (22–34)','valid client ranges should take precedence')
C_Map.GetMapLevels=function() return 0,0 end
A.map.GetMapID=function() return 1431 end
A.UpdateNavigation();assert(A.zoneHeading:GetText()=='Duskwood (18–30)')
A.map.GetMapID=function() return 1415 end
A.map.GetNormalizedCursorPosition=function() return .5,.5 end
C_Map.GetMapInfoAtPosition=function() return {mapID=1431,name='Duskwood'} end
local label=CreateFrame('Frame');label.Name=label:CreateFontString()
label.labelInfoByType={[3]={name='Duskwood'}}
label.GetHighestPriorityLabelInfo=function(self) return self.labelInfoByType[3] end
label:SetScript('OnUpdate',function(self) self.Name:SetText('Duskwood') end)
local oldProviders=A.map.dataProviders
A.map.dataProviders={[{Label=label}]=true}
A.AttachZoneLevels();A.AttachZoneLevels()
for i=1,3 do label:GetScript('OnUpdate')(label);assert(label.Name:GetText()=='Duskwood (18–30)') end
label.GetHighestPriorityLabelInfo=function() return {name='Higher-priority POI'} end
label.Name:SetText('Higher-priority POI');A.UpdateHoverZoneLabel(label)
assert(label.Name:GetText()=='Higher-priority POI','zone hover must not overwrite POI banners')
A.map.dataProviders=oldProviders;A.map.GetMapID=oldMapID;A.map.GetNormalizedCursorPosition=oldCursor
C_Map.GetMapInfo=oldInfo;C_Map.GetMapLevels=oldLevels;C_Map.GetMapInfoAtPosition=oldAtPosition
local pin=CreateFrame('Button');pin.data={category='dungeon',name='Gnomeregan (29–38)',description='Should not show'}
local oldAddLine=GameTooltip.AddLine;local lines=0
GameTooltip.AddLine=function() lines=lines+1 end
MapperlyMapPinMixin.OnMouseEnter(pin)
assert(GameTooltip:GetText()=='Gnomeregan (29–38)' and lines==0,'dungeon tooltips should contain only name and range')
GameTooltip.AddLine=oldAddLine
InCombatLockdown=function() return true end
A.ApplyLayout();assert(A.layoutPending)
''')
print('PASS: standalone services without Questie, Forever projection, faction filtering, discovery persistence/deduplication; Lua syntax, settings, native pins, sizing, opacity and locate ping')
from PIL import Image
for name in ['Boat','Zeppelin','Airship','Portal','Dungeon','Mail','Note','ZoneExit','Hearthstone','FlightMaster','Quest','Destination']:
    path=root/'Media/Markers'/f'{name}.tga'
    with Image.open(path) as icon:
        assert icon.mode=='RGBA' and icon.size==(128,128)
        alpha=icon.getchannel('A')
        assert alpha.getextrema()[0]==0 and alpha.getextrema()[1]>200
        assert alpha.histogram()[0]>128*128*.2, f'{name} needs transparent space around its silhouette'
        for point in [(0,0),(127,0),(0,127),(127,127)]: assert icon.getpixel(point)[3]==0
    assert path.read_bytes()[2]==2, 'WoW textures must use uncompressed TGA encoding'
for folder,size in [('Small',32),('Medium',64)]:
    for path in (root/'Media/Markers'/folder).glob('*.tga'):
        with Image.open(path) as icon:
            assert icon.mode=='RGBA' and icon.size==(size,size)
            for point in [(0,0),(size-1,0),(0,size-1),(size-1,size-1)]: assert icon.getpixel(point)[3]==0
        assert path.read_bytes()[2]==2
    assert len(list((root/'Media/Markers'/folder).glob('*.tga')))==12
print('PASS: 36 WoW marker textures, size variants, transparent corners and valid TGA encoding')
toolbar_names=['Locate','AddNote','Filters','Reveal','Lock','Settings','Resize','Compact','Close','ParentMap','Quest']
for folder,size in [('',128),('Medium',64),('Small',32)]:
    for name in toolbar_names:
        path=root/'Media/Toolbar'/folder/(name+'.tga')
        with Image.open(path) as icon:
            assert icon.mode=='RGBA' and icon.size==(size,size)
            assert icon.getchannel('A').getextrema()==(0,255)
            for point in [(0,0),(size-1,0),(0,size-1),(size-1,size-1)]: assert icon.getpixel(point)[3]==0
        assert path.read_bytes()[2]==2
print('PASS: 33 toolbar textures, native size variants and transparent backgrounds')
