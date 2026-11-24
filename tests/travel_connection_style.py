"""Clean optional schematic connections, distinct from real journey geometry."""
from pathlib import Path
import runpy
root=Path(__file__).resolve().parents[1]
l=runpy.run_path(str(root/'tests/journey_ui.py'))['lua']
l.execute('''
local saved=A.db
assert(A.InitStore({}).showTransportLinks==false,'New installs must default travel connections off')
assert(A.InitStore({showTransportLinks=true}).showTransportLinks==false,'Legacy default-on layer must migrate off once')
local explicit=A.InitStore({});explicit.showTransportLinks=true
assert(A.InitStore(explicit).showTransportLinks==true,'Remember deliberate opt-in after migration')
explicit.showTransportLinks=false;assert(A.InitStore(explicit).showTransportLinks==false)
A.InitStore(saved)
local B=A.BoatLinks
A.Journey.Clear();A.JourneyView.plan=nil
A.db.showTransportLinks=true;A.db.filters.flight=true;A.db.continentFilters.flight=true
A.map.GetMapID=function()return 1415 end;A.map:Show();A.map:GetCanvas():SetSize(1000,600)
local oldInfo=C_Map.GetMapInfo
C_Map.GetMapInfo=function(id)if id==1415 then return {mapType=2}end;return oldInfo(id)end
LibStub=function()return {GetZoneCoordinatesFromWorldInstance=function(_,x,y,instance)return x/1000,y/1000 end}end
local a={worldX=100,worldY=200,instance=0};local b={worldX=800,worldY=200,instance=0}
local row={id='forward',kind='flight',fromNodeID=2,toNodeID=4,board=a,arrival=b,
 path={a,{worldX=250,worldY=900,instance=0},{worldX=500,worldY=100,instance=0},b}}
A.Flights.Path=function(r)return r.path end
local offers={{transport=row}};A.Transports.Edges=function()return offers end
local function shown()
 local r={};for _,line in ipairs(B.lines)do if line:IsShown()then r[#r+1]=line end end;return r
end
B.Update({legs={}});local lines=shown();assert(#lines>=12,'Draw a smooth arc, not jagged native sample chords')
local count=#lines;local minY,maxY=0,-1000;local shadow,core=false,false
for _,line in ipairs(lines)do
 local start,finish=line.lineStart,line.lineEnd
 assert(start[3]>=100 and finish[3]<=800,'Curve must stay between its endpoints')
 assert(start[4]>=-180 and start[4]<=-60 and finish[4]>=-180 and finish[4]<=-60,'Curve must ignore native path noise')
 minY=math.min(minY,start[4],finish[4]);maxY=math.max(maxY,start[4],finish[4])
 shadow=shadow or line.thickness>3;core=core or line.thickness<2
end
assert(maxY-minY>5 and shadow and core,'Curves need a gentle bend and clear fine stroke')
for i=1,#lines,2 do
 assert(lines[i].drawSublevel<lines[i+1].drawSublevel,'Dark underlay must not cover the coloured stroke')
 assert(lines[i].lineStart[3]==lines[i+1].lineStart[3] and lines[i].lineEnd[3]==lines[i+1].lineEnd[3])
end
assert(lines[1].lineStart[3]==100 and lines[#lines].lineEnd[3]==800 and lines[#lines].lineEnd[4]==-120)
offers={{transport=row},{transport={id='reverse',kind='flight',board=b,arrival=a,path={b,a}}},{transport=row}}
B.Update({legs={}});assert(#shown()==count,'Reverse and duplicate offers must draw only once')
A.db.showTransportLinks=false;B.Update({legs={}});assert(#shown()==0,'Toggle must immediately clear background lines')
local check=A.transportLinksCheck;assert(check,'Expose the setting in Navigation')
check:SetChecked(true);check:GetScript('OnClick')(check);assert(A.db.showTransportLinks and #shown()==count)
check:SetChecked(false);check:GetScript('OnClick')(check);assert(not A.db.showTransportLinks and #shown()==0)
A.db.showTransportLinks=true;offers={}
for i=1,100 do offers[i]={transport={id='many:'..i,kind='flight',board={worldX=100+i,worldY=200,instance=0},arrival=b}} end
B.Update({legs={}});assert(#shown()<=768,'Background layer must have a hard drawing budget')
local allocated=#B.lines
for i=1,4 do B.Update({legs={}})end
assert(#B.lines==allocated,'Repeated redraws must reuse the bounded line pool')
C_Map.GetMapInfo=oldInfo
''')
print('PASS: default-off migration, opt-in persistence, smooth outlined arcs, reverse deduplication and immediate toggle')
