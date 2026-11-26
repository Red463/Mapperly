"""Terrain walking plans, cooperative jobs, and transactional navigation."""
from pathlib import Path
import sys
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'.test-deps'))
from lupa.lua51 import LuaRuntime
lua=LuaRuntime(unpack_returned_tuples=True)
lua.execute((root/'tests/wow.lua').read_text())
lua.execute("fakeUI(); A={}; InCombatLockdown=function() return false end")
for name in ['Store.lua','Terrain.lua','PlanningJob.lua','Journey.lua']:
 p=root/name
 if p.exists(): lua.execute('assert(loadstring(...))("Mapperly",A)',p.read_text(encoding='utf-8-sig'))
lua.execute('''
A.InitStore({layoutVersion=2})
local alphabet='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'
local function rows(lines)
 local packed={}
 for _,line in ipairs(lines) do
  local result={}
  for at=1,#line,6 do
   local n=0;for i=0,5 do n=n*2+(line:sub(at+i,at+i)=='1' and 1 or 0) end
   result[#result+1]=alphabet:sub(n+1,n+1)
  end
  packed[#packed+1]=table.concat(result)
 end
 return packed
end
A.TerrainData={version=1,zones={[1]={status='complete',w=5,h=5,widthYards=100,heightYards=100,rows=rows({'11011','11011','11011','11011','11111'})}}}
local start={mapID=1,x=.1,y=.1};local goal={mapID=1,x=.9,y=.1,name='Across the ridge'}
assert(A.Journey and A.Journey.Plan,'walking journey planner must exist')
local plan,reason=A.Journey.Plan(start,goal,{})
assert(plan,reason)
assert(plan.kind=='walking' and #plan.points>2 and plan.distance>80 and plan.estimatedSeconds>0,'a walking preview must include the terrain detour and estimates')
assert(A.Terrain.Validate(plan),'every rendered/followed walking segment must be permitted')
local bad,why=A.Journey.Plan(start,{mapID=1,x=.5,y=.1},{})
assert(not bad and why:find('blocked'),'blocked destinations must fail explicitly')
bad,why=A.Journey.Plan(start,{mapID=99,x=.5,y=.1},{})
assert(not bad and why,'unsupported cross-zone journeys must fail explicitly')
local before=0;local done=0;local failed=0
A.PlanningJob.Start(function()
 before=before+1;coroutine.yield();before=before+1;return plan
end,function(p) assert(p==plan);done=done+1 end,function() failed=failed+1 end)
A.PlanningJob.Step();assert(before==1 and done==0,'planning must span frames without publishing partial results')
A.PlanningJob.Step();assert(before==2 and done==1 and failed==0)
A.PlanningJob.Start(function() coroutine.yield();return plan end,function() done=done+1 end)
A.PlanningJob.Step();A.PlanningJob.Cancel();A.PlanningJob.Step();assert(done==1,'cancelled work must not publish')
A.PlanningJob.Start(function() return nil,'unreachable' end,function() done=done+1 end,function(reason) assert(reason=='unreachable');failed=failed+1 end)
A.PlanningJob.Step();assert(failed==1 and done==1)
local published=false
A.PlanningJob.Start(function() for i=1,100 do A.PlanningJob.Checkpoint() end;return plan end,function() published=true end)
A.PlanningJob.Step();assert(not published,'a frozen profiling clock must still yield after bounded work')
for i=1,20 do A.PlanningJob.Step() end
assert(published,'bounded checkpoints must eventually finish')
local displayError
A.PlanningJob.Start(function() return plan end,function() error('native preview widget failed') end,function(reason) displayError=reason end)
assert(pcall(A.PlanningJob.Step),'display errors must be reported rather than leave the UI looking stuck')
assert(displayError and displayError:find('native preview widget failed',1,true) and not A.PlanningJob.IsRunning())
local history=A.PlanningJob.Recent()
local displayFailure=history[#history]
assert(displayFailure.state=='failed' and displayFailure.reason==displayError,'job history must report the display failure shown to the player')
local profiling=debugprofilestop
local timerCompleted=false
debugprofilestop=function() error('profiling unavailable') end
A.PlanningJob.Start(function() return plan end,function() timerCompleted=true end)
assert(pcall(A.PlanningJob.Step) and timerCompleted,'unavailable profiling APIs must not strand a job before coroutine resume')
debugprofilestop=profiling
''')
lua.execute('''
-- Preview a genuinely disconnected point while the player follows a different route.
A.TerrainData.zones[2]={status='complete',w=5,h=5,widthYards=100,heightYards=100,rows={'2','2','2','2','2'}}
A.Navigation={target={map=1,x=.3,y=.7}}
C_Map={GetBestMapForUnit=function() return 2 end,GetPlayerMapPosition=function() return {GetXY=function() return .1,.1 end} end}
local preview={map=2,x=.9,y=.1,name='Preview'}
local captured
assert(A.Journey.Request(preview,nil,function(reason)
    local rows=A.PlanningJob.Recent()
    captured=rows[#rows]
    assert(captured.reason==reason)
end))
while A.PlanningJob.IsRunning() do A.PlanningJob.Step() end
assert(captured and captured.state=='failed','the disconnected preview must fail')
assert(captured.destination.map==2 and captured.destination.x==.9,'job history must identify the failed preview destination')
assert(captured.start.mapID==2 and captured.start.x==.1 and captured.start.y==.1,'record the player position used to plan that preview')
assert(A.Navigation.target.map==1,'preview failure must preserve the active destination')
''')
lua.execute('''
local plan=assert(A.Journey.Plan({mapID=1,x=.1,y=.1},{mapID=1,x=.9,y=.1,name='Goal'},{}))
A.Journey.Install(plan)
local nextPoint=assert(A.Journey.Update({mapID=1,x=.1,y=.1}))
assert(A.Terrain.Segment({mapID=1,x=.1,y=.1},nextPoint),'the HUD must first target a visible terrain bend')
A.Journey.Pause()
local p,why=A.Journey.Update({mapID=1,x=.1,y=.1});assert(not p and why=='Paused')
assert(A.Journey.Resume({mapID=1,x=.1,y=.1}))
local index=A.Journey.index
local skipped=A.Journey.Skip({mapID=1,x=.1,y=.1})
if skipped then assert(A.Terrain.Segment({mapID=1,x=.1,y=.1},A.Journey.Current())) else assert(A.Journey.index==index) end
for i=1,100 do
 local target=A.Journey.Current();if not target then break end
 local p,reason=A.Journey.Update(target)
 if not p then assert(reason=='arrived');break end
end
local _,why=A.Journey.Update(plan.points[#plan.points]);assert(why=='arrived')
''')
lua.execute('''
local plan=assert(A.Journey.Plan({mapID=1,x=.1,y=.1},{mapID=1,x=.9,y=.1,name='Restricted cell test'},{}))
A.Journey.Install(plan)
local target,index=A.Journey.Current(),A.Journey.index
for _,p in ipairs({{mapID=1,x=.5,y=.1},{mapID=1,x=.5,y=.3},{mapID=1,x=.5,y=.5}}) do
 assert(not A.Terrain.Segment(p,p))
 local nextPoint=assert(A.Journey.Update(p))
 assert(nextPoint==target and A.Journey.active==plan and A.Journey.index==index,'restricted player cells must retain the current route and waypoint')
end
A.Journey.Pause();assert(A.Journey.Resume({mapID=1,x=.5,y=.1}),'resume must remain available in a restricted player cell')
assert(A.Journey.Skip({mapID=1,x=.5,y=.1}),'manual skip must remain available outside the mask')
assert(A.Terrain.Validate(plan),'restricted player movement must not rewrite planned geometry')
local closePlan={mapID=1,points={{mapID=1,x=.1,y=.1},{mapID=1,x=.39,y=.1},{mapID=1,x=.2,y=.2}}}
assert(A.Terrain.Validate(closePlan))
A.Journey.Install(closePlan)
local p=A.Journey.Update({mapID=1,x=.41,y=.1})
assert(p==closePlan.points[3] and A.Journey.index==3,'a restricted cell inside the arrival radius must not trap a route bend')
A.Journey.Install(assert(A.Journey.Plan({mapID=1,x=.1,y=.1},{mapID=1,x=.39,y=.1},{})))
local _,reason=A.Journey.Update({mapID=1,x=.41,y=.1});assert(reason=='arrived','arrival must remain available in a restricted player cell')
''')
print('PASS: validated terrain walking plans, blocked/unavailable endpoints, background jobs and cancellation')

# Check the shipped data independently of the small algorithm fixtures.
lua.execute('assert(loadstring(...))("Mapperly",A)',(root/'Data/Terrain.lua').read_text(encoding='utf-8'))
lua.execute('''
local supported,partial=0,0
for id,z in pairs(A.TerrainData.zones) do
 if z.status=='complete' or z.status=='partial' then
  supported=supported+1;if z.status=='partial' then partial=partial+1 end
  assert(#z.rows==z.h and A.Terrain.Zone(id))
  for _,row in ipairs(z.rows) do assert(#row==math.ceil(z.w/6) and not row:find('[^A-Za-z0-9+/]')) end
 end
end
assert(supported==55 and partial==12,'coverage must match the supplied mask inventory')
''')
print('PASS: all 55 bundled terrain masks validate; 12 partial maps retain explicit coverage')

lua.execute('''
local a={mapID=1429,x=.825,y=.686}
local b={mapID=1429,x=.42265799844097,y=.665577526985558,name='Elwynn screenshot'}
local result,reason
A.PlanningJob.Start(function() return A.Journey.Plan(a,b,{}) end,function(p) result=p end,function(r) reason=r end)
for i=1,100 do A.PlanningJob.Step();if not A.PlanningJob.IsRunning() then break end end
assert(result,reason)
assert(A.Terrain.Validate(result) and result.distance>1300 and result.distance<1450,'the supplied Elwynn route must finish with valid geometry')
''')
print('PASS: screenshot Elwynn coordinates calculate a validated walking preview')
