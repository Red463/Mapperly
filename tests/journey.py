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
local profiling=debugprofilestop
local timerCompleted=false
debugprofilestop=function() error('profiling unavailable') end
A.PlanningJob.Start(function() return plan end,function() timerCompleted=true end)
assert(pcall(A.PlanningJob.Step) and timerCompleted,'unavailable profiling APIs must not strand a job before coroutine resume')
debugprofilestop=profiling



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
