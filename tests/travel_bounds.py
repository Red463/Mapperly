"""Goal-specific relaxed bounds match an independent all-pairs graph oracle."""
from pathlib import Path
import math
import random
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '.test-deps'))
from lupa.lua51 import LuaRuntime

lua = LuaRuntime(unpack_returned_tuples=True)
lua.execute('''
A={TravelNetwork={World=function(p) return p.worldX,p.worldY,p.instance end}}
''')
lua.execute('assert(loadstring(...))("Mapperly",A)', (ROOT / 'TravelBounds.lua').read_text())


def point(x, y=0, instance=0):
    return dict(worldX=x, worldY=y, instance=instance)


def edge(a, b, seconds):
    return dict(from_=a, to=b, seconds=seconds)


def table_edge(e):
    return lua.table_from({'from': lua.table_from(e['from_']),
                           'to': lua.table_from(e['to']), 'seconds': e['seconds']})


def build(goal, edges, speed):
    return lua.globals().A.TravelBounds.Build(lua.table_from(goal),
        lua.table_from([table_edge(e) for e in edges]), speed)


def distance(a, b):
    return math.hypot(a['worldX'] - b['worldX'], a['worldY'] - b['worldY']) if a['instance'] == b['instance'] else math.inf


def oracle(start, goal, edges, speed):
    points = [start, goal] + [p for e in edges for p in (e['from_'], e['to'])]
    costs = [[distance(a, b) for b in points] for a in points]
    for i, e in enumerate(edges):
        costs[2 + 2*i][3 + 2*i] = min(costs[2 + 2*i][3 + 2*i], e['seconds'] * speed)
    for k in range(len(points)):
        for i in range(len(points)):
            for j in range(len(points)):
                costs[i][j] = min(costs[i][j], costs[i][k] + costs[k][j])
    return costs[0][1]


random.seed(84631)
for _ in range(35):
    goal = point(random.randrange(-100, 100), random.randrange(-100, 100), random.randrange(3))
    pool = [point(random.randrange(-100, 100), random.randrange(-100, 100), random.randrange(3)) for _ in range(6)]
    edges = [edge(random.choice(pool), random.choice(pool), random.randrange(0, 30)) for _ in range(8)]
    speed = random.choice([1, 7, 14])
    bound = build(goal, edges, speed)
    assert bound
    for _ in range(5):
        start = point(random.randrange(-100, 100), random.randrange(-100, 100), random.randrange(3))
        expected = oracle(start, goal, edges, speed)
        actual = bound(lua.table_from(start))
        assert actual == expected or math.isclose(actual, expected, abs_tol=1e-8)
        assert bound(lua.table_from(start)) == actual, 'cached query changed the bound'
    assert bound(lua.table_from(goal)) == 0, 'the goal has zero remaining cost'

goal = point(100)
edges = [edge(point(0), point(0, instance=1), 1),
         edge(point(0, instance=1), point(99), 1)]
assert build(goal, edges, 7)(lua.table_from(point(0))) == 15
assert build(point(0), [], 7)(lua.table_from(point(0))) == 0
assert build(goal, [], 7)(lua.table_from(point(0, instance=1))) == math.inf

# Actual walking detours can only add cost to this deliberately relaxed route.
bound = build(goal, edges, 7)
actual_cost = 30 + 7 + 45 + 7 + 20
assert bound(lua.table_from(point(-10))) <= actual_cost

lua.execute('''
local B=A.TravelBounds.Build
local p={worldX=0,worldY=0,instance=0}
assert(not B(nil,{},7));assert(not B(p,nil,7));assert(not B(p,{},0))
assert(not B(p,{},0/0));assert(not B(p,{},math.huge))
assert(not B({worldX=math.huge,worldY=0,instance=0},{},7))
assert(not B(p,{{from=p,to=p,seconds=-1}},7))
assert(not B(p,{{from=p,to=p,seconds=0/0}},7))
assert(not B(p,{{from=p,to=p,seconds=math.huge}},7))
assert(not B(p,{{from={},to=p,seconds=1}},7))
local b=B(p,{},7);assert(b and not b({}))
local world=A.TravelNetwork.World
A.TravelNetwork.World=function() error('position unavailable') end
assert(not B(p,{},7));assert(not b(p))
A.TravelNetwork.World=world
local checkpoints=0
A.Terrain={Checkpoint=function() checkpoints=checkpoints+1 end}
local edges={}
for i=1,30 do for j=1,30 do
 edges[#edges+1]={from={worldX=i*10,worldY=0,instance=0},to={worldX=j*10,worldY=0,instance=0},seconds=1}
end end
local dense=B({worldX=300,worldY=0,instance=0},edges,1)
for i=1,29 do assert(dense({worldX=i*10,worldY=0,instance=0})==1) end
assert(checkpoints<200,'shared native masters must compact arrival states and departure bounds')
''')
print('PASS: exact relaxed graph bounds, multiple transports, cross-instance travel, zero goal, caching and conservative invalid-input fallback')
