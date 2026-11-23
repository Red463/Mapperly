"""Continent background uses native pieces, including skipped sampling breaks."""
from pathlib import Path
import runpy
root=Path(__file__).resolve().parents[1]
lua=runpy.run_path(str(root/'tests/journey_ui.py'))['lua']
lua.execute('''
local B=A.BoatLinks
A.Journey.Clear();A.JourneyView.plan=nil
A.db.showTransportLinks=true;A.db.filters.transport=true;A.db.continentFilters.transport=true
A.map.GetMapID=function() return 1415 end;A.map:Show();A.map:GetCanvas():SetSize(1000,600)
local info=C_Map.GetMapInfo;C_Map.GetMapInfo=function(id) if id==1415 then return {mapType=2} end;return info(id) end
LibStub=function() return {GetZoneCoordinatesFromWorldInstance=function(_,x,y,instance,target) if instance==0 then return x/1000,y/1000 end end} end
local row={id='native',kind='boat',toName='Destination',board={worldX=100,worldY=200,instance=0},arrival={worldX=300,worldY=400,instance=1},
 path={{worldX=100,worldY=200,instance=0},{worldX=800,worldY=800,instance=0},{worldX=300,worldY=400,instance=1,breakBefore=true}}}
A.Transports.Edges=function() return {{transport=row}} end
B.Update({legs={}})
local shown={};for _,line in ipairs(B.lines) do if line:IsShown() then shown[#shown+1]=line end end
assert(#shown==1 and shown[1].lineStart[3]==100 and shown[1].lineEnd[3]==800 and shown[1].lineEnd[4]==-480,'remote endpoint cannot hide or replace the native visible continent piece')
row.path={}
for i=1,100 do row.path[i]={worldX=i<17 and 100+i or 800+i,worldY=200,instance=0,breakBefore=i==17} end
B.Update({legs={}})
for _,line in ipairs(B.lines) do if line:IsShown() then
 local x1,x2=line.lineStart[3],line.lineEnd[3]
 assert(not (x1<200 and x2>800),'downsampling cannot bridge an unsampled native break')
end end
local visible=row;visible.toName='Z visible';local edges={}
for i=1,49 do edges[#edges+1]={transport={id='offmap'..i,kind='boat',toName='A offmap '..i,
 board={worldX=100,worldY=200,instance=1},arrival={worldX=200,worldY=300,instance=1},
 path={{worldX=100,worldY=200,instance=1},{worldX=200,worldY=300,instance=1}}}} end
edges[#edges+1]={transport=visible};A.Transports.Edges=function() return edges end
B.Update({legs={}})
local count=0;for _,line in ipairs(B.lines) do if line:IsShown() then count=count+1 end end
assert(count>0,'off-map offers cannot consume the background connection limit before visible sources')
''')
print('PASS: continent native bends, cross-instance clipping and sampled geometry breaks')
