"""Standalone reference fishing levels and map-heading integration."""
from pathlib import Path
import runpy
root=Path(__file__).resolve().parents[1]
l=runpy.run_path(str(root/'tests/run.py'))['lua']
l.execute('''
assert(type(A.FishingRange)=='function','Fishing reference data and formatter are missing')
local count=0
for id,row in pairs(A.FishingLevelsData.maps)do
 count=count+1;assert(type(id)=='number' and row.minimum>=1 and row.recommended>=row.minimum)
 assert((row.maximum or row.minimum)>=row.minimum and (row.recommendedMaximum or row.recommended)>=row.recommended)
end
assert(count==43,'Keep the published coverage explicit')
local oldInfo=C_Map.GetMapInfo;local oldID=A.map.GetMapID
C_Map.GetMapInfo=function(id)return {mapID=id,name='Zone',mapType=(id==1415 or id==947) and 2 or 3}end
local lo,rec,hi,highRec=A.FishingRange(1431)
assert(lo==51 and rec==150 and hi==51 and highRec==150)
assert(A.FishingLabel(1431)=='Fishing: 51+ · Recommended: 150')
assert(A.FishingLabel(1429)=='Fishing: 1+ · Recommended: 25')
assert(A.FishingLabel(1453)=='Fishing: 1+ · Recommended: 75','Cities can have fishing without a quest level range')
assert(A.FishingLabel(1447)=='Fishing: 201–326+ · Recommended: 300–425','Azshara special waters must not be flattened')
assert(A.FishingLabel(1434)=='Fishing: 126–201+ · Recommended: 225–300')
assert(A.FishingLabel(1444)=='Fishing: 201–326+ · Recommended: 300–425')
for _,id in ipairs({1415,947,999999,1418})do assert(A.FishingLabel(id)==nil,'Do not invent levels for unsupported maps')end
A.map.GetMapID=function()return 1431 end
A.UpdateNavigation();local f=A.fishingHeading
assert(f and f:IsShown() and f.text:GetText()==A.FishingLabel(1431))
assert(f.point[1]=='TOP' and f.point[2]==A.map.ScrollContainer and f.point[5]==-34)
assert(f:GetWidth()<=A.map.ScrollContainer:GetWidth()-48)
local label=CreateFrame('Frame');label.Name=label:CreateFontString()
A.PositionHoverZoneLabel(label,true);assert(label.point[5]==-60,'Subzone must clear fishing row')
local lines={};GameTooltip.SetOwner=function(self,owner)self.owner=owner end
GameTooltip.IsOwned=function(self,owner)return self.owner==owner end
GameTooltip.AddLine=function(_,line)lines[#lines+1]=line end
f:GetScript('OnEnter')(f)
assert(GameTooltip:GetText()=='Fishing skill')
local tip=table.concat(lines,' ')
assert(tip:find('51',1,true) and tip:find('150',1,true) and tip:find('lure',1,true))
for _,word in ipairs({'WCLBox','checked','published','Published','server','2026-'})do assert(not tip:find(word,1,true),'Tooltip should omit source/date and server-reference wording')end
A.Theme.Set('original');assert(f.point[1]=='TOPLEFT' and f.point[2]==A.map.ScrollContainer,'Charcoal fishing row must sit below header')
A.Theme.Set('gatherly');assert(f.point[1]=='TOP' and f:IsShown())
A.map.GetMapID=function()return 999999 end;A.UpdateNavigation();assert(not f:IsShown(),'Clear stale zone fishing data')
A.PositionHoverZoneLabel(label,true);assert(label.point[5]==-40)
A.map.GetMapID=function()return 1453 end;A.UpdateNavigation();assert(f:IsShown())
A.map.GetMapID=function()return 1415 end;A.UpdateNavigation();assert(not f:IsShown())
C_Map.GetMapInfo=oldInfo;A.map.GetMapID=oldID
''')
print('PASS: both fishing values, mixed waters, cities, unknown/overview maps, tooltip, themes and subzone spacing')
