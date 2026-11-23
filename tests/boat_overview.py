"""Cross-ocean overview travel and hover previews never change active guidance."""
from pathlib import Path
import runpy
root=Path(__file__).resolve().parents[1]
lua=runpy.run_path(str(root/'tests/journey_ui.py'))['lua']
lua.execute('''
local B=assert(A.BoatLinks,'boat overview overlay must exist')
local row={id='ocean',kind='boat',fromName='Booty Bay',toName='Ratchet',
 a={mapID=1434,x=.2,y=.3},b={mapID=1413,x=.4,y=.5},
 board={worldX=100,worldY=200,instance=0},arrival={worldX=300,worldY=400,instance=1},
 path={{worldX=100,worldY=200,instance=0},{worldX=120,worldY=220,instance=0},{worldX=290,worldY=390,instance=1,breakBefore=true},{worldX=300,worldY=400,instance=1}}}
A.TransportData={version=1,edges={row}}
A.Transports.Edges=function() return {{transport=row}} end
A.db.filters.transport=true;A.db.continentFilters.transport=true
A.db.showTransportLinks=false
local map=947;A.map.GetMapID=function() return map end;A.map:Show()
local hbd={GetZoneCoordinatesFromWorldInstance=function(_,x,y,instance,target)
 if target==947 then return instance==0 and .8 or .2,y/1000 end
 if instance==0 then return x/1000,y/1000 end
end}
LibStub=function() return hbd end
local plan={points={},legs={{kind='transport',transport=row}}}
A.Journey.Install(plan);local active=A.Journey.active
B.Update(plan)
local shown=0;for _,line in ipairs(B.lines) do if line:IsShown() then shown=shown+1 end end
assert(shown>0,'cross-continent boat leg must have a visible world-overview connection')
A.Journey.Clear();A.Navigation.target=nil
local pin={map=947,category='transport',kind='boat',transportID='ocean',name='Boat to Ratchet'}
assert(B.Hover(pin));B.Update()
shown=0;for _,line in ipairs(B.lines) do if line:IsShown() then shown=shown+1 end end
assert(shown>0 and not A.Journey.active and not A.Navigation.target,'hover preview must work without starting a route')
B.Clear(pin);for _,line in ipairs(B.lines) do assert(not line:IsShown(),'hover-only lines must clear on leave') end
A.Journey.Install(plan);B.Hover(pin);B.Clear(pin);B.Update(plan)
assert(A.Journey.active==plan,'hover cannot replace or stop the installed journey')
map=1429;B.Update(plan);for _,line in ipairs(B.lines) do assert(not line:IsShown(),'overview connectors cannot leak onto zone maps') end
map=947
local found
for _,p in ipairs(A.PlacesForMap(947)) do if p.transportID=='ocean' then found=p;break end end
assert(found and found.name=='Boat to Ratchet','visible boat pin must identify its native outgoing service')
local frame=CreateFrame('Button');frame.icon=frame:CreateTexture()
for key,method in pairs(MapperlyMapPinMixin) do frame[key]=method end
frame:OnAcquired(found);frame:OnMouseEnter();assert(B.hover==found,'native boat hover must activate its route preview')
frame:OnMouseLeave();assert(not B.hover and A.Journey.active==plan)
frame:OnMouseEnter();frame:OnReleased();assert(not B.hover and not frame.hoverBaseLevel,'pin recycling must clear the route and hover level')
''')
print('PASS: cross-ocean schematic links, independent hover, leave cleanup and zone isolation')
