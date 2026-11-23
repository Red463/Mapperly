"""Marker connections delegate availability and preserve navigation until an action."""
from pathlib import Path
import runpy
root=Path(__file__).resolve().parents[1]
lua=runpy.run_path(str(root/'tests/journey_ui.py'))['lua']
lua.execute('''
local L=assert(A.TransportLinks,'interactive transport adapter must exist')
A.db.filters.transport=true;A.db.continentFilters.transport=true
A.db.filters.flight=true;A.db.continentFilters.flight=true
local row={id='zeppelin:test',kind='zeppelin',name='Tower A to Tower B',fromName='Tower A',toName='Tower B',
 a={mapID=1431,x=.2,y=.3},b={mapID=1429,x=.4,y=.5},board={worldX=10,worldY=20,instance=0},arrival={worldX=30,worldY=40,instance=1},planningSeconds=300}
local flight={id='flight:2:4',kind='flight',fromNodeID=2,toNodeID=4,fromName='Source',toName='Destination',a=row.a,b=row.b,board=row.board,arrival=row.arrival,planningSeconds=120}
local offers={row,flight};local checks=0
A.Transports.Edges=function() checks=checks+1;local r={};for _,v in ipairs(offers) do r[#r+1]={transport=v} end;return r end
local pin={map=947,category='transport',kind='zeppelin',transportID=row.id}
assert(#L.ForPin(pin)==1 and L.ForPin(pin)[1].id==row.id)
assert(#L.ForPin({map=947,category='flight',flightNodeID=2})==1)
assert(#L.ForPin({map=947,category='flight',flightNodeID=99})==0,'unknown flights must not appear')
A.db.continentFilters.transport=false;assert(#L.ForPin(pin)==0);A.db.continentFilters.transport=true
local preview,start=A.JourneyView.Preview,A.Navigation.ToPin;local chosen
A.JourneyView.Preview=function(p) chosen=p;return true end
assert(L.Act(pin,row.id,false));assert(chosen.map==1429 and chosen.x==.4 and chosen.name=='Tower B')
A.Navigation.ToPin=function(p) chosen=p;return true end
assert(L.Act(pin,row.id,true));assert(chosen.y==.5)
offers={flight};chosen=nil
assert(not L.Act(pin,row.id,true) and not chosen,'stale/disallowed selections cannot start navigation')
A.JourneyView.Preview=preview;A.Navigation.ToPin=start
assert(checks>0,'availability must use the real planner adapter, never a second discovery policy')
''')
print('PASS: directed marker binding, filter/discovery delegation, destination actions and stale rejection')
