"""Continent zone hover shows fishing alongside quest levels without stale data."""
from pathlib import Path
import runpy
root=Path(__file__).resolve().parents[1]
l=runpy.run_path(str(root/'tests/fishing_levels.py'))['l']
l.execute('''
local map,hovered,x,y=1415,{mapID=1429,name='Elwynn Forest'},.5,.5
A.map.GetMapID=function()return map end
A.map.GetNormalizedCursorPosition=function()return x,y end
C_Map.GetMapInfo=function(id)return {mapID=id,mapType=id==1415 and 2 or 3,name='Zone'}end
C_Map.GetMapLevels=function()return 0,0 end
C_Map.GetMapInfoAtPosition=function()return hovered end
local label=CreateFrame('Frame');label.Name=label:CreateFontString()
local createText=label.CreateFontString
label.CreateFontString=function(self,...)
 local f=createText(self,...)
 f.GetFont=function(s)return s.fontPath or 'TestFont',s.fontSize or 10,s.fontFlags or '' end
 return f
end
label.GetScale=function()return .695 end
label.Description=label:CreateFontString();label.Description:SetText('Native description')
label.Description:SetPoint('TOP',label.Name,'BOTTOM',0,-10)
label.Description.GetPoint=function(self)return unpack(self.point)end;label.Description.GetNumPoints=function()return 1 end
label:SetPoint('TOP',A.map.ScrollContainer,'TOP',0,-10)
label.GetPoint=function(self)return unpack(self.point)end;label.GetNumPoints=function()return 1 end
local area={name='Elwynn Forest'};local priority=area
label.labelInfoByType={[3]=area};label.GetHighestPriorityLabelInfo=function()return priority end
local native=0
label:SetScript('OnUpdate',function(self)native=native+1;self.Name:SetText(area.name or '')end)
A.map.dataProviders={[{Label=label}]=true};A.AttachZoneLevels();A.AttachZoneLevels()
local function tick()label:GetScript('OnUpdate')(label)end
tick()
local fish=label.mapperlyFishing
assert(fish and fish:IsShown(),'Continent hover must show fishing guidance')
assert(fish:GetText()==A.FishingLabel(1429) and label.Name:GetText()=='Elwynn Forest (1–10)')
assert(fish.point[1]=='TOP' and fish.point[2]==label.Name and fish.point[3]=='BOTTOM' and fish.point[5]<0,'Fishing must sit below the hovered zone level')
assert(label.Description.point[2]==fish and label.Description:GetText()=='Native description','Preserve native descriptions below the fishing row')
assert(math.abs(fish.fontSize-14/.695)<.001,'Continent fishing should use larger 14px text, compensating native hover scale')
label.GetScale=function()return .8 end;tick();tick()
assert(math.abs(fish.fontSize-17.5)<.001,'Scale changes must not compound font adjustments')
label.GetScale=function()return .695 end;tick()
local before=native;for i=1,3 do tick()end;assert(label.mapperlyFishing==fish and native==before+3,'Reuse one label and preserve native OnUpdate')
hovered={mapID=1447,name='Azshara'};tick();assert(fish:GetText()==A.FishingLabel(1447))
hovered={mapID=1453,name='Stormwind City'};tick();assert(fish:IsShown() and fish:GetText()==A.FishingLabel(1453),'Cities do not need quest levels to have fishing')
hovered={mapID=1418,name='Badlands'};tick();assert(not fish:IsShown(),'Unknown fishing must clear previous values')
assert(label.Description.point[2]==label.Name and label.Description.point[5]==-10,'Restore native description layout without fishing')
hovered={mapID=1429,name='Elwynn Forest'};tick();assert(fish:IsShown())
priority={name='Higher-priority POI'};tick();assert(not fish:IsShown(),'Do not attach zone data to a POI banner')
priority=area;tick();assert(fish:IsShown());hovered=nil;tick();assert(not fish:IsShown())
hovered={mapID=1429,name='Elwynn Forest'};x=-1;tick();assert(not fish:IsShown())
x=.5;area.name=nil;tick();assert(not fish:IsShown());area.name='Elwynn Forest'
for _,theme in ipairs({'original','gatherly'})do
 A.Theme.Set(theme);tick();assert(fish:IsShown() and fish:GetText()==A.FishingLabel(1429))
 assert(not label:GetScript('OnEnter') and not label:GetScript('OnMouseDown'),'Hover text must not intercept map input')
end
label:Hide();assert(not fish:IsShown(),'Native label hide must clear its fishing child')
label:Show();tick();assert(fish:IsShown())
-- Follow the same input source as the native caption, not an idle mouse.
local hasGamepad,mouseFocus=true,true
InputUtil={IsGamepadUIEnabled=function()return true end}
A.map.HasGamepadCursorInput=function()return hasGamepad end
A.map.IsCanvasMouseFocusOrPinFocus=function()return mouseFocus end
A.map.GetNormalizedGamepadCursorPosition=function()return .8,.5 end
C_Map.GetMapInfoAtPosition=function(_,cx)return cx>.7 and {mapID=1431,name='Duskwood'} or {mapID=1429,name='Elwynn Forest'}end
tick();assert(fish:GetText()==A.FishingLabel(1431),'Controller hover must not use the idle mouse zone')
hasGamepad=false;mouseFocus=false;tick();assert(fish:GetText()==A.FishingLabel(1431))
mouseFocus=true;tick();assert(fish:GetText()==A.FishingLabel(1429),'Native mouse focus must restore mouse lookup')
InputUtil=nil
map=1431;A.UpdateNavigation();tick();assert(not fish:IsShown() and A.fishingHeading:IsShown(),'Zone view must retain its own fishing row without a duplicate')
''')
print('PASS: continent hover fishing, cities, mixed waters, stale cleanup, native lifecycle, themes and input transparency')
