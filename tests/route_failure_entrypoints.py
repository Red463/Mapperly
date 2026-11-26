"""User-requested routing failures reach the report action once per attempt."""
from pathlib import Path
import runpy

root = Path(__file__).resolve().parents[1]
lua = runpy.run_path(str(root / 'tests/run.py'))['lua']
lua.execute("""
local N, S, V = A.Navigation, A.PlanningStatus, A.JourneyView
N.Stop()
A.db.navigationMode = 'terrain'
LibStub = function() return {
    GetWorldCoordinatesFromZone = function(_, x, y, map)
        if map==1431 then return x*1000, y*1000, 0 end
    end,
    GetPlayerWorldPosition = function() return nil end,
} end
C_Map.GetBestMapForUnit = function() return 1431 end
C_Map.GetPlayerMapPosition = function() return nil end
A.map:Hide()

local notices, lastRequested = 0
local failed = S.Failed
S.Failed = function(id, candidate, reason)
    notices = notices + 1
    lastRequested = candidate
    return failed(id, candidate, reason)
end
local function verifyFailure(before, reason, label)
    assert(notices == before+1, label..' must present exactly one failure')
    assert(S.frame:IsShown() and S.frame.state=='failed', label..' must show the failure status')
    assert(S.frame.detail:GetText():find(reason, 1, true), label..' must explain this attempt')
end
local pin = {map=1431, x=.73, y=.64, name='Requested destination'}
local unavailable = 'Player position is unavailable.'
A.NavigateCommand('73 64 Requested destination')
verifyFailure(0, unavailable, '/way')
assert(lastRequested.map==pin.map and lastRequested.x==pin.x and lastRequested.y==pin.y)

local before = notices
assert(not N.Start(9999, 22, 77, 'Unprojectable zone'))
verifyFailure(before, 'This map cannot be used for navigation', 'Unprojectable destination')
assert(lastRequested.map==9999 and lastRequested.x==.22 and lastRequested.y==.77)
before = notices
assert(not N.Start(1431, -10, 64, pin.name))
assert(notices==before, 'Malformed coordinates stay on the entry form')

assert(not N.ToPin(pin))
verifyFailure(before, unavailable, 'Map marker')
N.target = pin
before = notices
assert(not N.Replan())
verifyFailure(before, unavailable, 'Replan')
assert(N.target==pin)

before = notices
assert(not N.Start(pin.map, 73, 64, pin.name, {automatic=true}))
assert(notices==before, 'Automatic recovery must keep existing guidance quiet')

for _,mode in ipairs({'terrain', 'direct'}) do
    before = notices
    A.db.navigationMode = mode
    assert(not V.Preview(pin))
    verifyFailure(before, unavailable, mode..' preview')
    assert(lastRequested==pin)
end
before = notices
V.OpenCurrent()
verifyFailure(before, unavailable, 'Active direct preview')

local repair = {category='repair', name='Repairer', key='npc:repair', map=1431, x=.73, y=.64}
A.db.navigationMode = 'terrain'
A.NearbyServices.List = function(role) assert(role=='repair'); return {repair} end
before = notices
assert(not A.NearbyServices.Navigate(repair))
verifyFailure(before, unavailable, 'Nearby repairer')
assert(lastRequested.name==repair.name and lastRequested.map==repair.map)

local J = A.PlanningJob
J.Start(function() coroutine.yield() end)
local id = S.Begin(pin)
before = notices
assert(not V.Preview(pin))
assert(notices==before+1 and S.frame.notice:find('already being planned', 1, true))
assert(S.frame.state=='running' and S.frame.jobID==id and J.IsRunning(),
       'A rejected preview preserves the running job and its Cancel action')
""")
print('PASS: synchronous navigation, preview and service failures preserve the request and automatic recovery stays quiet')
