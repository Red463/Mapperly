"""Deterministic rejoin/deviation tests plus automatic-job ownership integration."""
from pathlib import Path
import runpy
root=Path(__file__).resolve().parents[1]
lua=runpy.run_path(str(root/'tests/journey_navigation.py'))['lua']
if (root/'RouteRecovery.lua').exists():lua.execute('assert(loadstring(...))("Mapperly",A)',(root/'RouteRecovery.lua').read_text())
lua.execute('''
assert(A.RouteRecovery,'route recovery module must exist')
local R=A.RouteRecovery
A.TerrainData={version=1,zones={[1431]={status='complete',w=2,h=2,widthYards=1000,heightYards=1000,rows={'w','w'}}}}
local function p(x,y) return {mapID=1431,x=x,y=y} end
local function install(points) R.Clear();A.Journey.Install({kind='walking',mapID=1431,points=points}) end
local points={p(.1,.1),p(.1,.8),p(.8,.8),p(.8,.1)}
install(points)
local q=p(.5,.8)
R.Update(q,0);R.Update(q,1)
assert(A.Journey.index==2,'brief proximity must not skip turns')
local state=R.Update(q,2)
assert(state.rejoined and A.Journey.index==3,'sustained safe proximity must skip the missed turn and guide along the later segment')
R.Update(p(.1,.3),5);assert(A.Journey.index==3,'recovery must never move backwards')
install(points)
R.Update(p(.79,.8),0);R.Update(p(.8,.79),1)
assert(R.Update(p(.8,.78),2).rejoined and A.Journey.index==4,'continuous proximity while moving around an adjacent turn must count as one sustained rejoin')
install({p(.1,.1),p(.9,.9),p(.1,.9),p(.9,.1)})
R.Update(p(.5,.5),0);R.Update(p(.5,.5),3)
assert(A.Journey.index==2,'a crossing with the current leg must not jump ahead')
install({p(.1,.1),p(.1,.8),p(.8,.8),p(.2,.8),p(.9,.8)})
R.Update(p(.5,.8),0);R.Update(p(.5,.8),3)
assert(A.Journey.index==2,'overlapping later legs must remain ambiguous')
install({p(.1,.1),p(.1,.8),p(.8,.8),p(.2,.803)})
R.Update(p(.5,.8025),0);R.Update(p(.5,.8025),2)
assert(A.Journey.index==2,'near-parallel adjacent hairpin interiors must not be mistaken for a shared turn')
install(points)
local original=A.Terrain.Segment
A.Terrain.Segment=function(a,b) return a.x==b.x and a.y==b.y end
R.Update(q,0);R.Update(q,3);assert(A.Journey.index==2,'blocked connectors must not skip terrain bends')
A.Terrain.Segment=original
install(points)
q=p(.5,.5)
assert(not R.Update(q,0).replan)
assert(not R.Update(q,2).replan)
assert(R.Update(q,3).replan,'a sustained detour must request replanning')
assert(not R.Update(q,4).replan and not R.Update(q,12).replan,'replanning attempts need a cooldown')
assert(R.Update(q,13).replan)
A.Journey.Pause();assert(not R.Update(q,30).replan,'pause must suppress recovery')
A.Journey.paused=false
R.Update(nil,31);assert(not R.Update(q,32).replan,'invalid position must reset the deviation streak')
install(points)
A.Terrain.Segment=function() return false end
R.Update(q,0);assert(not R.Update(q,20).replan,'restricted cells must not start impossible replanning loops')
A.Terrain.Segment=original
''')
print('PASS: sustained forward rejoin, crossings/ambiguity, terrain safety, detour timing and cooldown')

lua.execute('''
local R,N,J=A.RouteRecovery,A.Navigation,A.Journey
local request=J.Request;local timer=0;local calls=0;local fail=false
GetTime=function() return timer end
local position={mapID=1431,x=.5,y=.5}
C_Map.GetBestMapForUnit=function() return 1431 end
C_Map.GetPlayerMapPosition=function() return {GetXY=function() return position.x,position.y end} end
local oldPlan
local function setup()
 N.Stop();R.Clear();timer=0;position.x=.5;position.y=.5;fail=false
 A.db.navigationMode='terrain';A.db.preferRoads=true
 N.target={map=1431,x=.9,y=.1,name='Keep this destination',zone='Test',worldX=100,worldY=900,instance=0}
 oldPlan={kind='walking',mapID=1431,points={{mapID=1431,x=.1,y=.1},{mapID=1431,x=.9,y=.1}}}
 J.Install(oldPlan)
end
J.Request=function(candidate,done,failed)
 calls=calls+1;assert(A.db.preferRoads,'automatic requests must retain road preference')
 A.PlanningJob.Start(function()
  coroutine.yield()
  if fail then return nil,'No connection' end
  return {kind='walking',mapID=1431,points={{mapID=1431,x=position.x,y=position.y},{mapID=1431,x=candidate.x,y=candidate.y}}}
 end,done,failed);return true
end
local function detour() N.Tick();timer=3;N.Tick() end
setup();local before=calls;detour()
assert(calls==before+1 and N.autoReplan and N.pending,'sustained deviation must launch a cooperative automatic request')
assert(J.active==oldPlan and N.frame.icon:IsShown(),'automatic planning must keep the last route and arrow')
timer=4;N.Tick();assert(calls==before+1,'an in-flight request must not be restarted')
A.PlanningJob.Step();A.PlanningJob.Step()
assert(J.active~=oldPlan and not N.pending and not N.autoReplan and N.target.name=='Keep this destination','successful automatic route must replace only the route, retaining its destination')
setup();fail=true;detour();A.PlanningJob.Step();A.PlanningJob.Step()
assert(J.active==oldPlan and N.target and not N.pending,'failure must preserve the previous journey')
before=calls;timer=5;N.Tick();timer=12;N.Tick();assert(calls==before,'failed planning must obey retry cooldown')
timer=13;N.Tick();assert(calls==before+1)
setup();detour();N.Pause()
assert(J.paused and not N.autoReplan and not N.pending and not A.PlanningJob.IsRunning(),'pause must cancel automatic work and remain paused')
setup()
A.PlanningJob.Start(function() coroutine.yield();return {} end,function() end)
before=calls;detour();assert(calls==before,'automatic recovery must not steal a preview or manual planning job')
A.PlanningJob.Cancel()
timer=4;N.Tick();assert(calls==before+1,'finishing another planning job must not consume the recovery cooldown')
setup();detour();N.Stop();A.PlanningJob.Step();assert(not N.target and not J.active,'Stop must cancel automatic replacement callbacks')
setup();detour();position.x=.5;position.y=.1;timer=4;N.Tick()
assert(J.active==oldPlan and not N.pending and not A.PlanningJob.IsRunning(),'returning to the current leg must cancel an obsolete off-route replacement')
setup();detour();position.x=.9;position.y=.1;N.Tick()
assert(not N.target and not N.pending and not A.PlanningJob.IsRunning(),'arrival must cancel an automatic request for that same destination')
setup();detour();assert(N.SetSmartRouting(false))
assert(N.target and not J.active and not N.pending and not N.autoReplan,'switching off smart routing must cancel recovery')
setup();detour();assert(N.Start(1431,20,30,'Manual replacement'))
A.PlanningJob.Step();A.PlanningJob.Step()
assert(N.target.name=='Manual replacement' and not N.autoReplan,'a manual destination must replace and cancel the automatic callback')
setup()
J.Install({kind='walking',mapID=1431,points={{mapID=1431,x=.1,y=.1},{mapID=1431,x=.1,y=.8},{mapID=1431,x=.8,y=.8},{mapID=1431,x=.8,y=.1}}})
detour();assert(N.autoReplan)
position.x=.5;position.y=.8;timer=4;N.Tick();timer=6;N.Tick()
assert(J.index==3 and not N.autoReplan and not N.pending and not A.PlanningJob.IsRunning(),'safely rejoining forward must cancel an obsolete automatic search')
J.Request=request
setup();detour();assert(A.PlanningJob.IsRunning())
while A.PlanningJob.IsRunning() do A.PlanningJob.Step() end
assert(J.active~=oldPlan and A.Terrain.Validate(J.active) and not N.pending,'the real planner must commit a validated replacement from the detour')
N.Stop()
''')
print('PASS: automatic replan success/failure, cooldown, pause/stop/arrival cancellation and job ownership')
