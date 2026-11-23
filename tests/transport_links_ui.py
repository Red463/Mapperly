"""All supported modes render/select safely through native pins and themed UI."""
from pathlib import Path
import runpy
root=Path(__file__).resolve().parents[1]
lua=runpy.run_path(str(root/'tests/journey_ui.py'))['lua']
lua.execute('''
local L,B=A.TransportLinks,A.BoatLinks
A.db.filters.transport=true;A.db.continentFilters.transport=true
A.db.filters.flight=true;A.db.continentFilters.flight=true;A.db.showTransportLinks=true
local rows={}
for i,kind in ipairs({'boat','zeppelin','airship','flight'}) do
 rows[i]={id=kind..':test',kind=kind,fromName='Source',toName='Destination '..i,name='Source to destination',fromNodeID=2,
 a={mapID=1431,x=.2,y=.3},b={mapID=1429,x=.4,y=.5},board={worldX=100,worldY=200,instance=0},arrival={worldX=300,worldY=400,instance=1},
 path={{worldX=100,worldY=200,instance=0},{worldX=150,worldY=250,instance=0}},planningSeconds=180,fare=123,geometryUnknown=kind=='flight'}
end
A.Transports.Edges=function() local r={};for _,row in ipairs(rows) do r[#r+1]={transport=row} end;return r end
local map=947;A.map.GetMapID=function() return map end;A.map:Show()
LibStub=function() return {GetZoneCoordinatesFromWorldInstance=function(_,x,y,instance,target) return instance==0 and .8 or .2,y/1000 end} end
local active=A.Journey.active;local target=A.Navigation.target
local function shown() local n=0;for _,line in ipairs(B.lines) do if line:IsShown() then n=n+1 end end;return n end
for _,row in ipairs(rows) do
 local pin={map=947,name='Source',category=row.kind=='flight' and 'flight' or 'transport',kind=row.kind,transportID=row.kind~='flight' and row.id or nil,flightNodeID=row.kind=='flight' and 2 or nil}
 assert(B.Hover(pin));assert(shown()>0)
 assert(L.Show(pin) and L.window:IsShown())
 local item=L.window.list.rows[1];assert(item.record.id==row.id)
 item:GetScript('OnEnter')(item);assert(B.focus and B.focus.id==row.id)
 item:GetScript('OnLeave')(item);assert(not B.focus)
 L.window:Hide()
end
assert(A.Journey.active==active and A.Navigation.target==target,'browse/hover cannot mutate the installed journey')
B.Clear();B.Update();assert(shown()>0,'enabled overview network must draw without an active journey')
A.db.showTransportLinks=false;B.Update();assert(shown()==0,'network setting hides background connections')
local pin={map=947,category='transport',kind='zeppelin',transportID=rows[2].id,name='Source'}
assert(B.Hover(pin) and shown()>0,'explicit hover still highlights a connection with background disabled')
L.Show(pin)
local preview=A.JourneyView.Preview;local count=0
A.JourneyView.Preview=function(p) count=count+1;assert(p.map==1429 and p.x==.4);return true end
local item=L.window.list.rows[1];item.preview:GetScript('OnClick')(item.preview)
assert(count==1 and not L.window:IsShown());A.JourneyView.Preview=preview
L.Show(pin);A.Transports.Edges=function() return {} end
item.navigate:GetScript('OnClick')(item.navigate)
assert(L.window:IsShown() and L.window.status:GetText():find('no longer available',1,true),'stale actions report unavailability without changing navigation')
L.window:Hide();map=1431;B.Update();assert(shown()==0,'network and highlights cannot leak onto zone maps')
-- Own-marker clicks retain ping and waypoint ownership.
local opened,waypoints,pings=0,0,0;local ctrl,alt=false,false
local show=L.Show;L.Show=function() opened=opened+1;return true end
local toPin=A.Navigation.ToPin;A.Navigation.ToPin=function() waypoints=waypoints+1;return true end
IsControlKeyDown=function() return ctrl end;A.IsWaypointClick=function(button) return alt and button=='RightButton' end
A.map.ProcessGlobalPinMouseActionHandlers=function() pings=pings+1;return true end
local frame=CreateFrame('Button');frame.data=pin
ctrl=true;MapperlyMapPinMixin.OnClick(frame,'LeftButton');assert(pings==1 and opened==0)
ctrl=false;alt=true;MapperlyMapPinMixin.OnClick(frame,'RightButton');assert(waypoints==1 and opened==0)
alt=false;MapperlyMapPinMixin.OnClick(frame,'RightButton');assert(opened==0)
MapperlyMapPinMixin.OnClick(frame,'LeftButton');assert(opened==1)
L.Show=show;A.Navigation.ToPin=toPin
''')
print('PASS: four travel modes, background/hover controls, themed chooser, preview and stale-action feedback')
