"""Best-effort dry routing must retain a permitted swimming fallback."""
from pathlib import Path
import runpy
root=Path(__file__).resolve().parents[1]
l=runpy.run_path(str(root/'tests/run.py'))['lua']
l.execute("""
A.InitStore({allowSwimming=false})
assert(A.db.avoidSwimming==true and A.db.allowSwimming==true,'old swimming exclusion must migrate to best-effort preference')
A.InitStore({});assert(A.db.avoidSwimming==false,'ordinary swimming remains the default')
A.db.avoidSwimming=true
local T=A.Terrain
T.Zone=function()return {status='complete'}end
T.Segment=function()return true end
A.Transports=nil;A.Flights=nil;A.TravelNetwork=nil;A.StructureData=nil
local calls={};local dryExists=true
T.Path=function(a,b)
 local allowed=A.Water.AllowSwimming()
 calls[#calls+1]=allowed
 if not allowed and not dryExists then return nil,'blocked' end
 return {a,b},allowed and 10 or 20
end
local a,b={mapID=1429,x=.1,y=.1},{mapID=1429,x=.2,y=.2}
local plan=assert(A.Journey.Plan(a,b))
assert(plan.distance==20 and #calls==1 and calls[1]==false,'choose dry alternative even when swimming is shorter')
assert(A.Water.AllowSwimming(),'planning preference must not become a live arrival prohibition')
dryExists=false;calls={}
plan=assert(A.Journey.Plan(a,b))
assert(plan.distance==10 and #calls==2 and not calls[1] and calls[2],'retry with swimming when dry search fails')
assert(plan.swimmingFallback==true,'preview should disclose permitted-water retry')
A.db.avoidSwimming=false;calls={};assert(A.Journey.Plan(a,b));assert(#calls==1 and calls[1])
A.db.avoidSwimming=true;calls={}
assert(A.Journey.Plan(a,b,{allowSwimming=true}));assert(#calls==1 and calls[1],'explicit internal policy must be honored')
-- A cooperative dry search must never leak into main-thread UI/arrival checks.
local yielded=false
T.Path=function(a,b)
 if not A.Water.AllowSwimming() and not yielded then yielded=true;coroutine.yield() end
 return {a,b},20
end
local c=coroutine.create(function() return A.Journey.Plan(a,b) end)
assert(coroutine.resume(c));assert(coroutine.status(c)=='suspended')
assert(A.Water.AllowSwimming(),'yielded/cancelled job must not change another thread policy')
assert(coroutine.resume(c));assert(coroutine.status(c)=='dead')
A.InitStore({avoidSwimming=true,allowSwimming=true});assert(A.db.avoidSwimming)
""")
print('PASS: saved preference migration, dry-first search, swimming fallback, explicit policy and coroutine isolation')

# Source-backed Elwynn banks: the dry itinerary exists but is much longer.
from lupa.lua51 import LuaRuntime
native=LuaRuntime(unpack_returned_tuples=True);native.execute('A={}')
for name in ['Store.lua','Data/Terrain.lua','Data/Water.lua','Water.lua','Data/GroundCorrections.lua','Terrain.lua','PathReuse.lua','Journey.lua']:
 native.execute('assert(loadstring(...))("Mapperly",A)',(root/name).read_text())
native.execute("""
A.InitStore({avoidSwimming=true,preferRoads=false})
local a={mapID=1429,x=.53001,y=.36421}
local b={mapID=1429,x=.55762,y=.36421}
local dry=assert(A.Journey.Plan(a,b));assert(dry.distance>2000 and not dry.swimmingFallback)
A.db.avoidSwimming=false
local wet=assert(A.Journey.Plan(a,b));assert(wet.distance<110)
-- End inside this same liquid strip: dry-only cannot reach it, preference can.
local water={mapID=1429,x=(a.x+b.x)/2,y=a.y}
assert(A.Terrain.Allowed(water) and not A.Terrain.Allowed(water,{allowSwimming=false}))
A.db.avoidSwimming=true
local fallback=assert(A.Journey.Plan(a,water))
assert(fallback.swimmingFallback and fallback.distance<110)
assert(A.Terrain.Validate(fallback),'accepted swimming fallback must remain valid in live policy')
""")
print('PASS: native Elwynn dry detour, shorter unrestricted route and reachable water destination fallback')
