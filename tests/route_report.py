"""Reports retain bounded route failures and counters without private player data."""
from pathlib import Path
import runpy
root=Path(__file__).resolve().parents[1]
lua=runpy.run_path(str(root/'tests/run.py'))['lua']
assert (root/'RouteReport.lua').exists(), 'route report module must exist'
lua.execute('assert(loadstring(...))("Mapperly",A)',(root/'RouteReport.lua').read_text())
lua.execute('''
local R,J,N=A.RouteReport,A.PlanningJob,A.Navigation
UnitGUID=function() return 'Player-private-guid' end;UnitName=function() return 'PrivateName' end
GetBuildInfo=function() return '1.15','12345','date',11508 end
N.target={map=1431,x=.1,y=.2,name='PrivateName',wallet=9000};N.pending={map=1429,x=.7,y=.8,name='PrivateName'}
R.RecordRequest(N.pending,'Failure for PrivateName Player-private-guid', {mapID=1431,x=.2,y=.3})
J.Start(function() J.BeginPath(1429);J.PathProgress(42);J.Report('Searching',{flightRoutes=3,flightSources=2});return nil,'Missing crossing' end)
J.Step()
UnitPosition=function() return 500,600,0,1 end
IsSwimming=function() return false end;UnitOnTaxi=function() return false end;UnitInVehicle=function() return false end
local report=R.Build()
assert(report:find('Native position: north=500 east=600 z=0 instance=1',1,true) and report:find('swimming=false taxi=false vehicle=false',1,true),'report explains native position and land status')
assert(report:find('Path reuse cache:',1,true) and report:find('Water coverage:',1,true),'source and cache coverage included without raw dumps')
assert(report:find('Missing crossing',1,true) and report:find('42',1,true) and report:find('flightRoutes=3',1,true))
assert(not report:find('PrivateName',1,true) and not report:find('Player%-private') and not report:find('9000',1,true),'report excludes names GUID and wallet')
J.Start(function() coroutine.yield();return {} end);J.Step();J.Cancel()
report=R.Build();assert(report:find('cancelled',1,true),'cancelled calculations retained')
J.Start(function() J.Start(function() return {} end);return nil,'stale result' end);J.Step();J.Step()
report=R.Build();assert(not report:find('stale result',1,true),'replaced work cannot claim newer job result')
for i=1,100 do R.RecordRequest(N.pending,string.rep('x',10000)) end
assert(#R.Build()<=16000,'reports remain bounded')
local secret={};issecretvalue=function(v) return v==secret end
N.planningError=secret;N.target={map=secret,x=secret,y=secret,name=secret}
GetBuildInfo=function() return secret,secret,secret,secret end
UnitPosition=function() return secret,secret,secret,secret end
IsSwimming=function() return secret end;UnitOnTaxi=function() return secret end;UnitInVehicle=function() return secret end
assert(pcall(R.Build),'secret API values remain unread')
issecretvalue=nil;R.Open();assert(R.frame:IsShown() and R.frame.edit:GetText()==R.Build())
A.Theme.Set('original');R.Open();A.Theme.Set('gatherly');R.Open()
''')
print('PASS: copyable bounded route report, recent failed/cancelled/newer jobs, privacy and secret safety')
