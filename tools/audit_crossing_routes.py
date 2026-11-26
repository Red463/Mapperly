"""Exercise every bundled crossing in both directions against shipped runtime data."""
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'.test-deps'))
from lupa.lua51 import LuaRuntime

def main():
    l=LuaRuntime(unpack_returned_tuples=True);l.execute((ROOT/'tests/wow.lua').read_text());l.execute('fakeUI();A={}')
    for f in ['Store.lua','Data/Terrain.lua','Data/GroundCorrections.lua','Data/Water.lua','Data/WalkingRegions.lua','Data/Crossings.lua','Data/Structures.lua','Terrain.lua','Water.lua','Structures.lua','WalkingRegions.lua','TravelNetwork.lua','Journey.lua']:
        l.execute('assert(loadstring(...))("Mapperly",A)',(ROOT/f).read_text())
    l.execute('A.InitStore({})')
    test=l.eval('''function(edge,reverse)
      local a,b=reverse and edge.b or edge.a,reverse and edge.a or edge.b
      local plan,why=A.Journey.Plan(a,b,{walkingOnly=true,maxWalkingCells=20000})
      if not plan then return false,why end
      -- Separately isolate the edge: normal planning may choose a different
      -- valid nearby exit. Require this target's exact handoff/floor as well.
      local all=A.CrossingData.edges;A.CrossingData.edges={edge}
      local exact,reason=A.TravelNetwork.Plan(a,b,{walkingOnly=true,maxWalkingCells=20000})
      A.CrossingData.edges=all
      if not exact then return false,reason end
      for _,leg in ipairs(exact.legs or {})do
        if edge.structure and leg.exitStructure==edge.structure and leg.exitPath then
          if A.TravelNetwork.Distance(leg.exitPath[1],a)<.001 and A.TravelNetwork.Distance(leg.exitPath[#leg.exitPath],b)<.001 then
            return true,plan.distance
          end
        elseif not edge.structure and leg.exitAim then
          local entry=leg.points[#leg.points]
          if A.TravelNetwork.Distance(entry,a)<.001 and A.TravelNetwork.Distance(leg.exitAim,b)<.001 then
            return true,plan.distance
          end
        end
      end
      return false,'Target handoff absent from isolated route'
    end''')
    results=[]
    for _,e in l.globals().A.CrossingData.edges.items():
        row=dict(id=e.id,maps=[e.a.mapID,e.b.mapID],source=e.source,directions=[])
        for reverse in [False,True]:
            success,detail=test(e,reverse);row['directions'].append(dict(reverse=reverse,success=success,detail=detail))
        results.append(row)
        print('Crossing',e.id,all(d['success'] for d in row['directions']),flush=True)
    out=ROOT.parent/'output/bridges-and-crossings-70959';out.mkdir(exist_ok=True)
    (out/'crossing-route-validation.json').write_text(json.dumps(results,indent=2)+'\n')
    bad=[r for r in results if not all(d['success'] for d in r['directions'])]
    print('Validated',len(results),'bundled crossings;',len(bad),'failed. Endpoint routes do not certify all nearby approaches or live transitions.')
    if bad:raise SystemExit(1)

if __name__=='__main__':main()
