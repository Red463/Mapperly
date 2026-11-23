"""Walking-only service intent must survive actual navigation and preview entry points."""
from pathlib import Path
import runpy
root=Path(__file__).resolve().parents[1]
l=runpy.run_path(str(root/'tests/run.py'))['lua']
l.execute("""
local N,J,V,S=A.Navigation,A.Journey,A.JourneyView,A.NearestServices
N.Stop();A.db.navigationMode='terrain'
local oldLib=LibStub
local hbd={GetWorldCoordinatesFromZone=function(_,x,y,map)local m=A.CrossingData.maps[map];return m.west-x*m.width,m.north-y*m.height,m.instance end,
 GetZoneCoordinatesFromWorldInstance=function(_,x,y,i,map)local m=A.CrossingData.maps[map];if m and m.instance==i then return (m.west-x)/m.width,(m.north-y)/m.height end end,
 GetPlayerWorldPosition=function()return 0,0,0 end}
LibStub=function(name)if name=='HereBeDragons-2.0' then return hbd end end
local request,tick,resolve=J.Request,N.Tick,S.Resolve
local captured
J.Request=function(p,done,failed)captured=p;return true end
N.Tick=function()end;S.Resolve=function(p)return p end
local pin={map=1431,x=.74,y=.44,name='Service',serviceKey='fixture',serviceKind='inn',walkingOnly=true}
assert(N.ToPin(pin));assert(captured.walkingOnly and N.pending.walkingOnly,'ToPin must pass walking intent through Start and Request')
N.target=N.pending;N.pending=nil
assert(N.Replan());assert(captured.walkingOnly,'explicit replan must retain walking-only choice')
assert(N.SetSmartRouting(false));assert(N.target.walkingOnly,'direct-mode transition retains the destination profile')
assert(N.SetSmartRouting(true));assert(captured.walkingOnly,'switching back to Smart routing restores the walking-only profile')
assert(N.SetPreferRoads(not A.db.preferRoads));assert(captured.walkingOnly,'road preference replan must retain walking-only choice')
assert(N.Start(1431,74,44,'Ordinary waypoint'));assert(not captured.walkingOnly,'ordinary destinations must keep transport support')
J.Request=request;N.Tick=tick;N.Stop()
-- The real Request worker must carry the flag into Plan too.
local player,plan=J.PlayerPosition,J.Plan
local start=assert(A.Terrain.Approach({mapID=1431,x=.826,y=.575},30))
J.PlayerPosition=function()return start end
local planned,done
J.Plan=function(a,b,o)planned=o.walkingOnly;return {kind='walking',points={a,b},distance=0,estimatedSeconds=0,legs={}}end
assert(J.Request({map=1431,x=start.x,y=start.y,name='Service',walkingOnly=true},function()done=true end,function(e)error(e)end))
while A.PlanningJob.IsRunning() do A.PlanningJob.Step() end
assert(planned and done,'Request must carry walking intent into the async plan')
J.PlayerPosition=player;J.Plan=plan
-- Preview Start revalidates and retains the same profile.
local navStart=N.Start;local starts=0
N.Start=function(map,x,y,name,o)assert(o.walkingOnly and o.mode=='terrain');starts=starts+1;return true end
V.Show({kind='walking',name='Service',distance=1,estimatedSeconds=1,points={{mapID=1431,x=.74,y=.44},{mapID=1431,x=.75,y=.44}},legs={}},pin)
V.start:GetScript('OnClick')(V.start);assert(starts==1)
S.Resolve=function()return nil,'Service changed' end
V.start:GetScript('OnClick')(V.start);assert(starts==1 and V.steps:GetText()=='Service changed')
V.CancelPreview();V.start:GetScript('OnClick')(V.start);assert(starts==1,'an invalidated preview action must be harmless')
N.Start=navStart;S.Resolve=resolve;LibStub=oldLib
""")
print('PASS: actual ToPin/Start/Request, replan, smart/road transitions, ordinary vehicle support and stale guarded preview Start')
