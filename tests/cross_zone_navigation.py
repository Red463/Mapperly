"""Actual Navigation.Start/HUD and automatic job state through a zone change."""
from pathlib import Path
import runpy
root=Path(__file__).resolve().parents[1]
lua=runpy.run_path(str(root/'tests/journey_navigation.py'))['lua']
for name in ['TravelNetwork.lua','RouteRecovery.lua']:
 lua.execute('assert(loadstring(...))("Mapperly",A)',(root/name).read_text())
lua.execute('''
local N,J=A.Navigation,A.Journey
N.Stop();A.db.navigationMode='terrain'
A.TerrainData={version=1,zones={}}
for _,id in ipairs({1431,1429}) do A.TerrainData.zones[id]={status='complete',w=2,h=2,widthYards=1000,heightYards=1000,rows={'w','w'}} end
A.CrossingData={version=1,maps={
 [1431]={name='Duskwood',west=1000,north=1000,width=1000,height=1000,instance=0},
 [1429]={name='Elwynn',west=500,north=1000,width=1000,height=1000,instance=0}},edges={
 {id=1,a={mapID=1431,x=.75,y=.5},b={mapID=1429,x=.3,y=.5},distance=50}}}
hbd.GetWorldCoordinatesFromZone=function(_,x,y,map) return A.TravelNetwork.World({mapID=map,x=x,y=y}) end
local map,x,y=1431,.1,.5
C_Map.GetBestMapForUnit=function() return map end
C_Map.GetPlayerMapPosition=function() return {GetXY=function() return x,y end} end
playerX,playerY,playerInstance=900,500,0;facing=0
assert(N.Start(1429,90,50,'Across the border'))
while A.PlanningJob.IsRunning() do A.PlanningJob.Step() end
assert(N.target and J.active.multiZone and N.frame.icon:IsShown())
assert(N.frame.label:GetText()=='650 yd')
x=.75;N.Tick();assert(J.crossing and N.frame.label:GetText()=='50 yd')
x=.775;N.Tick()
assert(J.crossing and N.frame.label:GetText()=='25 yd','delayed zone assignment must not turn the arrow back to the source waypoint')
map=1429;x=.3;N.Tick()
assert(J.legIndex==2 and N.target.name=='Across the border' and N.frame.label:GetText()=='600 yd','HUD must hand off to the next local leg without changing destination')
local plan,target=J.active,N.target
A.CrossingData.edges={}
map=1431;x=.1
assert(N.Start(1429,80,50,'Unconnected replacement'))
while A.PlanningJob.IsRunning() do A.PlanningJob.Step() end
assert(N.target==target and J.active==plan,'a failed cross-zone replacement must preserve the active destination and route')
map=1429;x=.9;N.Tick();assert(not N.target and not J.active,'arrival applies only to the final leg')
''')
print('PASS: cross-zone Navigation.Start, delayed boundary HUD, destination preservation and final arrival')
