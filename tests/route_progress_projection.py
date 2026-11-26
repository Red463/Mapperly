"""The two route overlays split the same active walking segment in world space."""
from pathlib import Path
import sys

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root / '.test-deps'))
from lupa.lua51 import LuaRuntime

lua = LuaRuntime(unpack_returned_tuples=True)
lua.execute('A = {}')
lua.execute('assert(loadstring(...))("Mapperly", A)', (root / 'RouteProgress.lua').read_text())
lua.execute('''
local P = A.RouteProgress
local hbd = {}
local reads = 0
function hbd:GetPlayerWorldPosition() reads = reads + 1; return 130, 240, 0 end
function hbd:GetWorldCoordinatesFromZone(x, y, map) return x * 1000, y * 2000, map end
LibStub = function() return hbd end
local a = {x=.1, y=.1, mapID=0}
local b = {worldX=160, worldY=280, instance=0}
local c = {worldX=160, worldY=200, instance=0}
local plan = {kind='walking', points={a,b,c}}
local leg
local J = {active=plan, index=2, Leg=function() return leg end}
A.Journey = J

local i, t, length = P.Split(plan)
assert(i==1 and t==.5 and length==100 and reads==1, 'obtain player once and project in yards')
i, t = P.Split(plan, hbd, 134, 237, 0)
assert(i==1 and t==.5 and reads==1, 'an offset player projects onto the line at the same fraction')
i, t = P.Split(plan, hbd, 163, 284, 0)
assert(i==1 and t==1, 'clamp within the end cap')
assert(not P.Split(plan, hbd, 97, 196, 0), 'nothing behind the player at the start')
assert(not P.Split(plan, hbd, 160, 200, 0), 'never pick a nearby later segment')
assert(not P.Split(plan, hbd, 200, 333, 0), 'ignore positions well past the current endpoint')
assert(not P.Split(plan, hbd, 130, 240, 1), 'player and route instances must match')
b.instance=1; assert(not P.Split(plan, hbd, 130, 240, 0)); b.instance=0
b.breakBefore=true; assert(not P.Split(plan)); b.breakBefore=nil
b.transport=true; assert(not P.Split(plan)); b.transport=nil
leg={kind='transport'}; assert(not P.Split(plan) and P.Segment(plan)==1); leg=nil
J.paused=true; assert(not P.Split(plan)); J.paused=false
A.RouteRecovery={IsOffRoute=function() return true end}; assert(not P.Split(plan)); A.RouteRecovery=nil
A.Flights={OnTaxi=function() return true end}; assert(not P.Split(plan)); A.Flights=nil
assert(not P.Split({points=plan.points}) and reads==1, 'separate previews never fetch position')
plan.kind='direct'; assert(not P.Split(plan)); plan.kind='walking'

J.index=2; leg={kind='walk',last=2,exitAim=c}; J.crossing=true
assert(P.Segment(plan)==2, 'ordinary crossing starts at the final approach point')
i, t = P.Split(plan, hbd, 160, 240, 0)
assert(i==2 and t==.5, 'walk across the actual connector to the next zone')
leg.exitPath={a,b,c}; leg.corridorStart=1; J.structureIndex=3
assert(P.Segment(plan)==2, 'structure index follows the sampled corridor')
assert(J.index==2 and J.structureIndex==3 and J.crossing, 'projection preserves follower state')

leg=nil; J.crossing=false; J.index=3
i, t = P.Split(plan, hbd, 160, 240, 0)
assert(i==2 and t==.5, 'immediately follow a confirmed rejoin or skip')
J.index=2
local secret={}; issecretvalue=function(v) return v==secret end
assert(not P.Split(plan, hbd, secret, 240, 0))
assert(not P.Split(plan, hbd, 130, 240, secret))
hbd.GetPlayerWorldPosition=function() error('unavailable') end
assert(not P.Split(plan))
b.instance=secret; assert(not P.Split(plan, hbd, 130, 240, 0)); b.instance=0
local original=hbd.GetWorldCoordinatesFromZone
local conversions=0
hbd.GetWorldCoordinatesFromZone=function(...) conversions=conversions+1; return original(...) end
a.x=secret; assert(not P.Split(plan, hbd, 130, 240, 0) and conversions==0)
a.x=.1; hbd.GetWorldCoordinatesFromZone=function() return secret, 200, 0 end
assert(not P.Split(plan, hbd, 130, 240, 0))
hbd.GetWorldCoordinatesFromZone=original
b.worldX=100; b.worldY=200; assert(not P.Split(plan, hbd, 100, 200, 0), 'zero-length segment')
''')
print('PASS: active walking progress, corridor indices, clamped world projection and unavailable positions')
