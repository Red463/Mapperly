"""Ground anchors must compose into real journeys, not just handoff routes."""
from pathlib import Path
import json,sys,time
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'.test-deps'))
from lupa.lua51 import LuaRuntime
lua=LuaRuntime(unpack_returned_tuples=True)
lua.execute((root/'tests/wow.lua').read_text());lua.execute('fakeUI();A={}')
for f in ['Store.lua','Data/Terrain.lua','Data/GroundCorrections.lua','Data/Water.lua','Data/WalkingRegions.lua','Data/Crossings.lua','Data/Structures.lua','Terrain.lua','Water.lua','Structures.lua','WalkingRegions.lua','TravelNetwork.lua','Journey.lua']:
    lua.execute('assert(loadstring(...))("Mapperly",A)',(root/f).read_text())
lua.execute('A.InitStore({})')
plan=lua.eval('''function(a,b)
 local p,why=A.Journey.Plan(a,b,{walkingOnly=true,preferRoads=false,maxWalkingCells=40000})
 return p~=nil,p and p.distance or why
end''')
wanted={tuple(sorted(p))for p in [(1426,1432),(1431,1436),(1433,2548),(1437,1417),(1440,1447),(1448,1450)]}
rows=json.loads((root/'tools/data/crossing-approaches-manifest.json').read_text())['links']
done=set();started=time.perf_counter()
for row in rows:
    a,b=row['sides'];pair=tuple(sorted((a['mapID'],b['mapID'])))
    if pair not in {tuple(sorted(p))for p in wanted}or pair in done or 'point'not in a or 'point'not in b:continue
    for start,goal in ((a['point'],b['point']),(b['point'],a['point'])):
        ok,detail=plan(lua.table_from(start),lua.table_from(goal))
        assert ok,(row['id'],pair,detail)
    done.add(pair)
    print('Approach journey',row['id'],pair,'both directions',flush=True)
assert wanted==done
print('PASS:',len(done)*2,'approach journeys in',round(time.perf_counter()-started,2),'seconds')
